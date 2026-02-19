from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Plot

class PlotSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Plot
        geo_field = 'geometry'
        fields = ['id', 'name', 'geometry', 'created_at']