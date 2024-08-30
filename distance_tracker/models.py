from django.db import models
from django.utils import timezone
from foodcartapp.models import Order

class Location(models.Model):
    address = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address

    def needs_update(self):
        return (timezone.now() - self.last_updated).days > 30

class Distance(models.Model):
    order = models.ForeignKey(Order, related_name='distances', on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=255)
    distance_km = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.restaurant_name} - {self.distance_km} км"
