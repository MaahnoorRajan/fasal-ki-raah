from dataclasses import asdict
from datetime import datetime
from urllib.parse import urlencode

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from .demo_data import DEMO_CASES, DEMO_SHIPMENT, DEMO_TRIPS
from .forms import DriverTripForm, ShipmentForm, SpaceRequestForm
from .matching import Shipment, evaluate_trip
from .models import DriverTrip, SpaceRequest


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
    next_url = request.POST.get("next") if request.method == "POST" else request.GET.get("next")
    if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
        next_url = ""
    if request.user.is_authenticated:
        return redirect(next_url or "driver-trips")
    form = UserCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect(next_url or "driver-trips")
    return render(request, "fasal/driver_auth.html", {"form": form, "signup": True, "next": next_url})


@login_required
@require_http_methods(["GET", "POST"])
def driver_trips(request):
    form = DriverTripForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        DriverTrip.objects.create(driver=request.user, **form.cleaned_data)
        return redirect("driver-trips")
    return render(request, "fasal/driver_trips.html", {
        "form": form,
        "trips": DriverTrip.objects.filter(driver=request.user).order_by("-departure").prefetch_related(
            Prefetch("space_requests", queryset=SpaceRequest.objects.select_related("sender").order_by("pk")),
        ),
        "now": timezone.now(),
    })


@never_cache
@require_http_methods(["GET", "POST"])
def request_space(request, pk):
    trip = get_object_or_404(DriverTrip, pk=pk)
    available = trip.active and trip.departure > timezone.now()
    if not request.user.is_authenticated:
        if not available:
            raise Http404("This trip no longer takes requests.")
        target = urlencode({"next": request.get_full_path()})
        return render(request, "fasal/request_space.html", {
            "trip": trip, "available": available,
            "login_url": f"{reverse('driver-login')}?{target}",
            "signup_url": f"{reverse('driver-signup')}?{target}",
        })

    existing = trip.space_requests.filter(sender=request.user).first()
    own_trip = trip.driver_id == request.user.pk
    form = None
    if available and not own_trip and existing is None:
        form = SpaceRequestForm(
            request.POST if request.method == "POST" else None,
            initial={"weight_kg": request.GET.get("weight")},
        )
        if request.method == "POST" and form.is_valid():
            weight = form.cleaned_data["weight_kg"]
            if weight > trip.spare_kg:
                form.add_error("weight_kg", "This trip does not have enough spare capacity for that load.")
            else:
                trip.space_requests.get_or_create(sender=request.user, defaults={"weight_kg": weight})
                return redirect("request-space", pk=pk)
    return render(request, "fasal/request_space.html", {
        "trip": trip, "available": available, "own_trip": own_trip, "space_request": existing, "form": form,
    })


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def edit_trip(request, pk):
    trip = get_object_or_404(
        DriverTrip, pk=pk, driver=request.user, active=True, departure__gt=timezone.now(),
    )
    form = DriverTripForm(
        request.POST if request.method == "POST" else None,
        initial={name: getattr(trip, name) for name in DriverTripForm.base_fields},
    )
    if request.method == "POST" and form.is_valid():
        updated = DriverTrip.objects.filter(
            pk=trip.pk, driver=request.user, active=True, departure__gt=timezone.now(),
        ).update(**form.cleaned_data)
        if not updated:
            raise Http404("This listing can no longer be edited.")
        return redirect("driver-trips")
    return render(request, "fasal/driver_trip_edit.html", {"form": form})


@login_required
@require_POST
def withdraw_trip(request, pk):
    trip = get_object_or_404(DriverTrip, pk=pk, driver=request.user)
    trip.active = False
    trip.share_phone = False
    trip.phone = ""
    trip.save(update_fields=["active", "share_phone", "phone"])
    return redirect("driver-trips")
