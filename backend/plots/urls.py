from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PlotViewSet

router = DefaultRouter()
router.register(r'plots', PlotViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
