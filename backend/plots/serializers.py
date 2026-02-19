from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Plot


class PlotSerializer(GeoFeatureModelSerializer):
    geometry = GeometryField()

    class Meta:
        model = Plot
        geo_field = 'geometry'
        fields = ['id', 'name', 'geometry', 'created_at']
