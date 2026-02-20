from django.contrib.gis.db import models
from django.db.models import UniqueConstraint

class Plot(models.Model):
    name = models.CharField(max_length=200)
    
    # srid=4326 is standard GPS (Lat/Long)
    geometry = models.PolygonField(srid=4326)
    
    # Store the calculated area
    area = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Automatically calculate the area before saving.
        Note: To get the area in square meters from 4326 (degrees), 
        we temporarily transform it to a metric system (3857).
        """
        if self.geometry:
            # Transform to Web Mercator (meters) to get a real-world area size
            geom_in_meters = self.geometry.transform(3857, clone=True)
            self.area = geom_in_meters.area
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # The "Idempotency" guard at the database level
            UniqueConstraint(fields=['geometry'], name='unique_plot_geometry')
        ]