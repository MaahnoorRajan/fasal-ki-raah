from django.conf import settings
from django.db import models
from django.db.models import F, Q, Sum
from django.db.models.functions import Round

from .matching import Stop, Trip


class DriverTripQuerySet(models.QuerySet):
    def with_capacity(self):
        return self.annotate(
            reserved_kg=Sum(
                "space_requests__weight_kg",
                filter=Q(space_requests__status__in=SpaceRequest.RESERVING_STATUSES),
                default=0,
            ),
        ).annotate(
            # Round to the form's precision before SQLite compares decimal weights.
            remaining_kg=Round(F("spare_kg") - F("reserved_kg"), precision=2),
        )


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

    objects = DriverTripQuerySet.as_manager()

    def as_trip(self):
        from django.utils.timezone import localtime

        return Trip(
            "Driver listing",
            (Stop(self.pickup, localtime(self.departure).time()),
             Stop(self.dropoff, localtime(self.arrival).time())),
            self.remaining_kg, self.rate_per_kg,
            contact_phone=self.phone if self.share_phone else "",
            listing_id=self.pk,
        )


class SpaceRequest(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COLLECTED = "collected"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RESERVING_STATUSES = (ACCEPTED, COLLECTED, DELIVERED)

    trip = models.ForeignKey(DriverTrip, on_delete=models.CASCADE, related_name="space_requests")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    weight_kg = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=16, default=PENDING)
    agreement = models.JSONField(default=dict, blank=True)

    @property
    def display_status(self):
        from django.utils import timezone

        if self.status == self.PENDING and (not self.trip.active or self.trip.departure <= timezone.now()):
            return "Closed"
        return self.status.capitalize()

    @property
    def can_cancel(self):
        return self.status in (self.PENDING, self.ACCEPTED)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["trip", "sender"], name="one_space_request_per_trip"),
        ]


class BookingEvent(models.Model):
    booking = models.ForeignKey(SpaceRequest, on_delete=models.CASCADE, related_name="events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)


class MarketPrice(models.Model):
    source = models.CharField(max_length=32)
    crop = models.CharField(max_length=80)
    market = models.CharField(max_length=80)
    period = models.DateField()
    frequency = models.CharField(max_length=8)
    price_type = models.CharField(max_length=32)
    original_price = models.DecimalField(max_digits=16, decimal_places=6)
    original_unit = models.CharField(max_length=16)
    pkr_per_kg = models.DecimalField(max_digits=14, decimal_places=4)

    @property
    def period_label(self):
        return self.period.strftime("%Y" if self.frequency == "annual" else "%b %Y")

    class Meta:
        ordering = ["-period", "market", "crop"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "crop", "market", "period", "price_type"],
                name="unique_market_price",
            ),
            models.CheckConstraint(condition=Q(pkr_per_kg__gt=0), name="positive_market_price"),
        ]
