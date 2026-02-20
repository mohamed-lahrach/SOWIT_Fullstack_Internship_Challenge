from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework.exceptions import ValidationError

from .models import Plot


class PlotSerializer(GeoFeatureModelSerializer):
    """
    Serializer to convert Plot model instances to GeoJSON.
    """
    class Meta:
        model = Plot
        # Points to the spatial column in your database
        geo_field = 'geometry'
        
        # Fields to include in the GeoJSON 'properties'
        fields = ('id', 'name', 'area', 'created_at')
        # This is the key line:
        read_only_fields = ('area', 'created_at')

    def validate(self, attrs):
        geometry = attrs.get('geometry')
        if geometry is None:
            return attrs

        overlaps_qs = Plot.objects.filter(geometry__intersects=geometry)
        if self.instance is not None:
            overlaps_qs = overlaps_qs.exclude(pk=self.instance.pk)

        if overlaps_qs.exists():
            raise ValidationError(
                {"geometry": "This plot overlaps an existing plot."}
            )

        return attrs
