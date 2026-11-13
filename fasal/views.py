from dataclasses import asdict
from datetime import datetime

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from .demo_data import DEMO_CASES, DEMO_SHIPMENT, DEMO_TRIPS
from .forms import DriverTripForm, ShipmentForm
from .matching import Shipment, evaluate_trip
from .models import DriverTrip


@never_cache
@require_http_methods(["GET", "POST"])
def planner(request, *, offline=False):
    is_example = request.method == "GET"
    travel_date = None
    shipment = DEMO_CASES.get(request.GET.get("example"), DEMO_SHIPMENT) if is_example else None
    form = ShipmentForm(initial=asdict(shipment)) if is_example else ShipmentForm(request.POST)
    if not is_example and form.is_valid():
        data = form.cleaned_data.copy()
        travel_date = data.pop("travel_date")
        shipment = Shipment(**data)

    context = {
        "form": form,
        "form_invalid": not is_example and shipment is None,
        "shipment": shipment,
        "is_example": is_example,
        "travel_date": travel_date,
        "offline": offline,
        "driver_signed_in": request.user.is_authenticated,
        "shipment_fields": [form[name] for name in (
            ("pickup", "dropoff", "weight_kg", "latest_arrival") if offline
            else ("pickup", "dropoff", "weight_kg", "latest_arrival", "travel_date")
        )],
        "price_fields": [form[name] for name in ("farm_price", "mandi_price", "handling_fees", "unsold_kg", "hire_quote")],
    }
    if shipment:
        trips = DEMO_TRIPS
        if travel_date:
            deadline = timezone.make_aware(datetime.combine(travel_date, shipment.latest_arrival))
            trips = (
                listing.as_trip() for listing in DriverTrip.objects.filter(
                    active=True, pickup=shipment.pickup, dropoff=shipment.dropoff,
                    departure__gt=timezone.now(), departure__date=travel_date,
                    arrival__lte=deadline, spare_kg__gte=shipment.weight_kg,
                )
            )
        evaluations = [evaluate_trip(shipment, trip) for trip in trips]
        context.update(
            farm_net=shipment.weight_kg * shipment.farm_price,
            unused_kg=max(0, 500 - shipment.weight_kg),
            used_percent=shipment.weight_kg / 5,
            matches=sorted(
                (result for result in evaluations if not result.rejection),
                key=lambda result: result.mandi_net,
                reverse=True,
            ),
            rejections=[result for result in evaluations if result.rejection],
        )
    return render(request, "fasal/planner.html", context)


@require_http_methods(["GET", "POST"])
def driver_signup(request):
    if request.user.is_authenticated:
        return redirect("driver-trips")
    form = UserCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("driver-trips")
    return render(request, "fasal/driver_auth.html", {"form": form, "signup": True})


@login_required
@require_http_methods(["GET", "POST"])
def driver_trips(request):
    form = DriverTripForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        DriverTrip.objects.create(driver=request.user, **form.cleaned_data)
        return redirect("driver-trips")
    return render(request, "fasal/driver_trips.html", {
        "form": form,
        "trips": DriverTrip.objects.filter(driver=request.user).order_by("-departure"),
    })


@login_required
@require_POST
def withdraw_trip(request, pk):
    trip = get_object_or_404(DriverTrip, pk=pk, driver=request.user)
    trip.active = False
    trip.share_phone = False
    trip.phone = ""
    trip.save(update_fields=["active", "share_phone", "phone"])
    return redirect("driver-trips")
