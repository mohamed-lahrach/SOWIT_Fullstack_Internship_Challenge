from django.contrib.gis.geos import Polygon
from django.db import DatabaseError
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Plot


class PlotTests(APITestCase):
    def setUp(self):
        self.list_url = reverse('plot-list')  # Adjust name if your router uses a different basename
        self.valid_payload = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-7.632, 33.585],
                    [-7.633, 33.585],
                    [-7.633, 33.586],
                    [-7.632, 33.586],
                    [-7.632, 33.585]
                ]]
            },
            "properties": {
                "name": "Original Plot"
            }
        }

    def _square_geometry(self, min_lng, min_lat, size=0.001):
        max_lng = min_lng + size
        max_lat = min_lat + size
        return {
            "type": "Polygon",
            "coordinates": [[
                [min_lng, min_lat],
                [max_lng, min_lat],
                [max_lng, max_lat],
                [min_lng, max_lat],
                [min_lng, min_lat]
            ]]
        }

    def _payload(self, name, min_lng, min_lat, size=0.001):
        return {
            "type": "Feature",
            "geometry": self._square_geometry(min_lng, min_lat, size=size),
            "properties": {"name": name},
        }

    def test_create_plot_and_calculate_area(self):
        """Test creating a plot and ensuring area is calculated."""
        response = self.client.post(self.list_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify area is not null
        plot = Plot.objects.get(name="Original Plot")
        self.assertIsNotNone(plot.area)
        self.assertGreater(plot.area, 0)

    def test_prevent_duplicate_geometry(self):
        """Test idempotency: cannot post the exact same geometry twice."""
        # First post
        self.client.post(self.list_url, self.valid_payload, format='json')
        # Second post (same data)
        response = self.client.post(self.list_url, self.valid_payload, format='json')
        
        # Should fail due to our UniqueConstraint or Serializer validation
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_prevent_overlapping_geometry(self):
        """Test that a plot partially overlapping another is blocked."""
        # Create first plot
        self.client.post(self.list_url, self.valid_payload, format='json')
        
        # Payload that overlaps 50% of the first plot
        overlapping_payload = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-7.6325, 33.585], # Starts halfway inside the first one
                    [-7.6340, 33.585],
                    [-7.6340, 33.586],
                    [-7.6325, 33.586],
                    [-7.6325, 33.585]
                ]]
            },
            "properties": {
                "name": "Overlapping Plot"
            }
        }
        response = self.client.post(self.list_url, overlapping_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_plots_list(self):
        """Test retrieving the GeoJSON FeatureCollection."""
        self.client.post(self.list_url, self.valid_payload, format='json')
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'FeatureCollection')
        self.assertEqual(len(response.data['features']), 1)

    def test_missing_name_is_rejected(self):
        """Missing name in properties should fail validation."""
        invalid_payload = {
            "type": "Feature",
            "geometry": self.valid_payload["geometry"],
            "properties": {},
        }
        response = self.client.post(self.list_url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_polygon_ring_is_rejected(self):
        """Polygon ring must be closed; invalid geometry should be rejected."""
        invalid_payload = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-7.632, 33.585],
                    [-7.633, 33.585],
                    [-7.633, 33.586],
                    [-7.632, 33.586]
                    # Missing closing point [-7.632, 33.585]
                ]]
            },
            "properties": {
                "name": "Invalid Ring"
            }
        }
        response = self.client.post(self.list_url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_same_geometry_on_same_instance_allowed(self):
        """Updating the same object with the same geometry should not self-block."""
        create_resp = self.client.post(self.list_url, self.valid_payload, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)

        plot_id = create_resp.data["id"]
        detail_url = reverse('plot-detail', args=[plot_id])

        patch_payload = {
            "type": "Feature",
            "geometry": self.valid_payload["geometry"],
            "properties": {
                "name": "Renamed Plot"
            }
        }
        response = self.client.patch(detail_url, patch_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["properties"]["name"], "Renamed Plot")

    def test_delete_removes_plot_from_list(self):
        """After delete, plot should no longer be returned by list endpoint."""
        create_resp = self.client.post(self.list_url, self.valid_payload, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        plot_id = create_resp.data["id"]
        detail_url = reverse('plot-detail', args=[plot_id])

        delete_resp = self.client.delete(detail_url)
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)

        list_resp = self.client.get(self.list_url)
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_resp.data['features']), 0)

    def test_almost_identical_geometry_is_rejected_as_overlap(self):
        """Near-identical geometry should still be blocked by overlap rule."""
        self.client.post(self.list_url, self.valid_payload, format='json')

        near_duplicate_payload = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-7.6320001, 33.5850001],
                    [-7.6330001, 33.5850001],
                    [-7.6330001, 33.5860001],
                    [-7.6320001, 33.5860001],
                    [-7.6320001, 33.5850001]
                ]]
            },
            "properties": {
                "name": "Near Duplicate Plot"
            }
        }
        response = self.client.post(self.list_url, near_duplicate_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_non_overlapping_second_plot_is_allowed(self):
        """A second plot that does not intersect should be accepted."""
        first = self._payload("Plot A", -7.640, 33.580)
        second = self._payload("Plot B", -7.620, 33.560)

        first_resp = self.client.post(self.list_url, first, format="json")
        self.assertEqual(first_resp.status_code, status.HTTP_201_CREATED)

        second_resp = self.client.post(self.list_url, second, format="json")
        self.assertEqual(second_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Plot.objects.count(), 2)

    def test_touching_boundary_is_rejected_by_intersects_rule(self):
        """With geometry__intersects, edge-touching polygons are considered intersecting."""
        first = self._payload("Plot A", -7.640, 33.580, size=0.002)
        # Shares boundary at x = -7.638
        touching = self._payload("Plot Touching", -7.638, 33.580, size=0.002)

        first_resp = self.client.post(self.list_url, first, format="json")
        self.assertEqual(first_resp.status_code, status.HTTP_201_CREATED)

        touching_resp = self.client.post(self.list_url, touching, format="json")
        self.assertEqual(touching_resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_to_overlapping_geometry_is_rejected(self):
        """Updating an existing plot geometry to intersect another plot should fail."""
        first_resp = self.client.post(
            self.list_url, self._payload("Plot A", -7.640, 33.580), format="json"
        )
        self.assertEqual(first_resp.status_code, status.HTTP_201_CREATED)

        second_resp = self.client.post(
            self.list_url, self._payload("Plot B", -7.620, 33.560), format="json"
        )
        self.assertEqual(second_resp.status_code, status.HTTP_201_CREATED)

        second_id = second_resp.data["id"]
        detail_url = reverse("plot-detail", args=[second_id])
        patch_payload = {
            "type": "Feature",
            "geometry": self._square_geometry(-7.6405, 33.5800, size=0.001),
            "properties": {"name": "Plot B Overlap"},
        }
        patch_resp = self.client.patch(detail_url, patch_payload, format="json")
        self.assertEqual(patch_resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bbox_filter_returns_only_matching_plots(self):
        """GET with in_bbox should only return features intersecting that bbox."""
        # One inside bbox around Casablanca-ish coords
        inside = self._payload("Inside", -7.632, 33.585)
        # One far away
        outside = self._payload("Outside", -6.900, 34.100)

        inside_resp = self.client.post(self.list_url, inside, format="json")
        self.assertEqual(inside_resp.status_code, status.HTTP_201_CREATED)

        outside_resp = self.client.post(self.list_url, outside, format="json")
        self.assertEqual(outside_resp.status_code, status.HTTP_201_CREATED)

        # bbox around the first polygon only
        bbox = "-7.64,33.58,-7.62,33.59"
        resp = self.client.get(self.list_url, {"in_bbox": bbox})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [f["properties"]["name"] for f in resp.data["features"]]
        self.assertIn("Inside", names)
        self.assertNotIn("Outside", names)

    def test_area_is_read_only_on_create(self):
        """Client-provided area should be ignored; server computes real area."""
        payload = self._payload("Area ReadOnly", -7.700, 33.500)
        payload["properties"]["area"] = 999999999

        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        plot = Plot.objects.get(name="Area ReadOnly")
        self.assertIsNotNone(plot.area)
        self.assertNotEqual(plot.area, 999999999)


class PlotDatabaseConstraintTests(TransactionTestCase):
    def _poly(self, min_lng, min_lat, size=0.001):
        max_lng = min_lng + size
        max_lat = min_lat + size
        return Polygon(
            (
                (min_lng, min_lat),
                (max_lng, min_lat),
                (max_lng, max_lat),
                (min_lng, max_lat),
                (min_lng, min_lat),
            ),
            srid=4326,
        )

    def test_direct_orm_insert_overlap_is_blocked_by_db(self):
        """DB trigger must block overlaps even when bypassing serializer/API."""
        Plot.objects.create(name="ORM A", geometry=self._poly(-7.640, 33.580))
        with self.assertRaises(DatabaseError):
            Plot.objects.create(name="ORM B", geometry=self._poly(-7.6405, 33.580))

    def test_direct_orm_insert_non_overlap_is_allowed(self):
        """DB trigger should allow non-overlapping direct ORM inserts."""
        Plot.objects.create(name="ORM A", geometry=self._poly(-7.640, 33.580))
        Plot.objects.create(name="ORM C", geometry=self._poly(-7.620, 33.560))
        self.assertEqual(Plot.objects.count(), 2)
