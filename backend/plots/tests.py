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