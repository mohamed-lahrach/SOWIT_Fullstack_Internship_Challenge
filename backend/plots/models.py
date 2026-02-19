from django.contrib.gis.db import models

class Plot(models.Model):
    name = models.CharField(max_length=255)
    geometry = models.PolygonField(srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']