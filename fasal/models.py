from django.conf import settings
from django.db import models

from .matching import Stop, Trip


class DriverTrip(models.Model):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pickup = models.CharField(max_length=100)
    dropoff = models.CharField(max_length=100)
    departure = models.DateTimeField()
    arrival = models.DateTimeField()
    spare_kg = models.PositiveIntegerField()
    rate_per_kg = models.PositiveIntegerField()
    phone = models.CharField(max_length=12, blank=True)
    share_phone = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def as_trip(self):
        from django.utils.timezone import localtime

        return Trip(
            "Driver listing",
            (Stop(self.pickup, localtime(self.departure).time()),
             Stop(self.dropoff, localtime(self.arrival).time())),
            self.spare_kg, self.rate_per_kg,
            contact_phone=self.phone if self.share_phone else "",
            is_listing=True,
        )
