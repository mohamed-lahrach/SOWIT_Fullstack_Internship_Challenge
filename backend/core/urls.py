from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This wires up our new API!
    # Requests to /api/plots/ will be sent to the plots app.
    path('api/', include('plots.urls')),
]