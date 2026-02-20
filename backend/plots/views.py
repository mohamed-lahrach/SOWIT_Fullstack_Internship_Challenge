from rest_framework import viewsets
from .models import Plot
from .serializers import PlotSerializer

class PlotViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Plots to be viewed or edited.
    GET /api/plots/  -> Lists all plots as GeoJSON
    POST /api/plots/ -> Creates a new plot
    """
    queryset = Plot.objects.all()
    serializer_class = PlotSerializer