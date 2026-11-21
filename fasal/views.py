from dataclasses import asdict
from datetime import datetime
from urllib.parse import urlencode

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import F, Prefetch, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from .demo_data import DEMO_CASES, DEMO_SHIPMENT, DEMO_TRIPS
from .forms import DriverTripForm, ShipmentForm, SpaceRequestForm
from .matching import Shipment, evaluate_trip
from .models import BookingEvent, DriverTrip, SpaceRequest


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
                listing.as_trip() for listing in DriverTrip.objects.with_capacity().filter(
                    active=True, pickup=shipment.pickup, dropoff=shipment.dropoff,
                    departure__gt=timezone.now(), departure__date=travel_date,
                    arrival__lte=deadline, remaining_kg__gte=shipment.weight_kg,
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


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def driver_trips(request):
    form = DriverTripForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        DriverTrip.objects.create(driver=request.user, **form.cleaned_data)
        return redirect("driver-trips")
    return render_driver_trips(request, form=form)


def render_driver_trips(request, *, form=None, error=None):
    return render(request, "fasal/driver_trips.html", {
        "form": form if form is not None else DriverTripForm(),
        "trips": DriverTrip.objects.with_capacity().filter(driver=request.user).order_by("-departure").prefetch_related(
            Prefetch("space_requests", queryset=SpaceRequest.objects.select_related("sender").order_by("pk")),
        ),
        "now": timezone.now(),
        "booking_error": error,
    }, status=409 if error else 200)


@never_cache
@login_required
@require_http_methods(["GET"])
def my_requests(request):
    return render(request, "fasal/my_requests.html", {
        "requests": SpaceRequest.objects.filter(sender=request.user).select_related("trip").order_by("-pk"),
        "now": timezone.now(),
    })


@never_cache
@require_http_methods(["GET", "POST"])
def request_space(request, pk):
    trip = get_object_or_404(DriverTrip.objects.with_capacity(), pk=pk)
    open_trip = trip.active and trip.departure > timezone.now()
    available = open_trip and trip.remaining_kg > 0
    if not request.user.is_authenticated:
        if not open_trip:
            raise Http404("This trip no longer takes requests.")
        target = urlencode({"next": request.get_full_path()})
        return render(request, "fasal/request_space.html", {
            "trip": trip, "available": available, "open_trip": open_trip,
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
            if weight > trip.remaining_kg:
                form.add_error("weight_kg", "This trip does not have enough spare capacity for that load.")
            else:
                trip.space_requests.get_or_create(sender=request.user, defaults={"weight_kg": weight})
                return redirect("request-space", pk=pk)
    return render(request, "fasal/request_space.html", {
        "trip": trip, "available": available, "open_trip": open_trip, "own_trip": own_trip,
        "space_request": existing, "form": form,
    })


def booking_agreement(trip, weight):
    return {
        "pickup": trip.pickup, "dropoff": trip.dropoff,
        "departure": timezone.localtime(trip.departure).isoformat(),
        "arrival": timezone.localtime(trip.arrival).isoformat(),
        "rate_per_kg": trip.rate_per_kg,
        "freight_pkr": str(weight * trip.rate_per_kg),
    }


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def booking_detail(request, pk):
    error = None
    if request.method == "POST":
        item = get_object_or_404(
            SpaceRequest.objects.filter(Q(sender=request.user) | Q(trip__driver=request.user)),
            pk=pk,
        )
        with transaction.atomic():
            # Authorize before locking, then serialize every transition against
            # acceptance, trip edits and other changes to this trip's capacity.
            DriverTrip.objects.filter(pk=item.trip_id).update(spare_kg=F("spare_kg"))
            item = SpaceRequest.objects.select_related("trip").get(pk=pk)
            action = request.POST.get("action")
            target = {"cancel": SpaceRequest.CANCELLED, "collect": SpaceRequest.COLLECTED,
                      "deliver": SpaceRequest.DELIVERED}.get(action)
            permitted = (
                action == "cancel"
                or action == "collect" and item.trip.driver_id == request.user.pk
                or action == "deliver" and item.sender_id == request.user.pk
            )
            valid = (
                action == "cancel" and item.can_cancel
                or action == "collect" and item.status == SpaceRequest.ACCEPTED and item.trip.active
                or action == "deliver" and item.status == SpaceRequest.COLLECTED
            )
            if not target or not permitted:
                error = "You cannot perform that action on this booking."
            elif item.status == target:
                return redirect("booking-detail", pk=pk)
            elif not valid:
                error = "The booking has changed. That action is no longer available."
            else:
                item.status = target
                item.save(update_fields=["status"])
                BookingEvent.objects.create(booking=item, actor=request.user, status=target)
                return redirect("booking-detail", pk=pk)
    item = get_object_or_404(
        SpaceRequest.objects.filter(Q(sender=request.user) | Q(trip__driver=request.user)).select_related("trip"),
        pk=pk,
    )
    return render(request, "fasal/booking_detail.html", {
        "booking": item, "events": item.events.select_related("actor").order_by("created_at", "pk"),
        "is_driver": item.trip.driver_id == request.user.pk,
        "agreed_departure": parse_datetime(item.agreement.get("departure", "")),
        "agreed_arrival": parse_datetime(item.agreement.get("arrival", "")),
        "booking_error": error,
    }, status=409 if error else 200)


def lock_owned_trip(request, pk):
    trips = DriverTrip.objects.filter(pk=pk, driver=request.user)
    # Acquire the database write lock before reading reservations. This works on
    # SQLite, where select_for_update() has no effect.
    if not trips.update(spare_kg=F("spare_kg")):
        raise Http404
    return trips


@login_required
@require_POST
def accept_space_request(request, pk, request_id):
    error = None
    with transaction.atomic():
        trip = lock_owned_trip(request, pk).with_capacity().get()
        item = get_object_or_404(trip.space_requests, pk=request_id)
        if item.status in SpaceRequest.RESERVING_STATUSES:
            return redirect("driver-trips")
        if item.status != SpaceRequest.PENDING:
            error = "This request was cancelled and cannot be accepted."
        elif not trip.active or trip.departure <= timezone.now():
            error = "This trip has closed. The request could not be accepted."
        elif item.weight_kg > trip.remaining_kg:
            error = "There is not enough remaining capacity to accept this request."
        else:
            item.status = SpaceRequest.ACCEPTED
            item.agreement = booking_agreement(trip, item.weight_kg)
            item.save(update_fields=["status", "agreement"])
            BookingEvent.objects.create(booking=item, actor=request.user, status=item.status)
    if error:
        return render_driver_trips(request, error=error)
    return redirect("driver-trips")


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def edit_trip(request, pk):
    if request.method == "POST":
        with transaction.atomic():
            trip = get_object_or_404(
                lock_owned_trip(request, pk).with_capacity(), active=True, departure__gt=timezone.now(),
            )
            form = DriverTripForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data["spare_kg"] < trip.reserved_kg:
                    form.add_error("spare_kg", "Capacity cannot be lower than the weight already reserved.")
                if trip.reserved_kg and any(
                    data[field] != getattr(trip, field)
                    for field in ("pickup", "dropoff", "departure", "arrival", "rate_per_kg")
                ):
                    form.add_error(None, "The route, times and rate are fixed after a request is accepted.")
                if not form.errors:
                    DriverTrip.objects.filter(pk=pk).update(**data)
                    return redirect("driver-trips")
    else:
        trip = get_object_or_404(
            DriverTrip.objects.with_capacity(), pk=pk, driver=request.user,
            active=True, departure__gt=timezone.now(),
        )
        form = DriverTripForm(initial={name: getattr(trip, name) for name in DriverTripForm.base_fields})
    return render(request, "fasal/driver_trip_edit.html", {"form": form, "reserved_kg": trip.reserved_kg})


@login_required
@require_POST
def withdraw_trip(request, pk):
    with transaction.atomic():
        trips = lock_owned_trip(request, pk)
        trip = trips.with_capacity().get()
        blocked = trip.departure > timezone.now() and trip.reserved_kg > 0
        if not blocked:
            trips.update(active=False, share_phone=False, phone="")
    if blocked:
        return render_driver_trips(request, error="An upcoming trip with accepted requests cannot be withdrawn.")
    return redirect("driver-trips")
