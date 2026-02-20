from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlotViewSet

# Create a router and register our viewset with it.
router = DefaultRouter()
router.register(r'plots', PlotViewSet)

# The router automatically generates the URL patterns.
urlpatterns = [
    path('', include(router.urls)),
]