from dataclasses import asdict

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .demo_data import DEMO_CASES, DEMO_SHIPMENT, DEMO_TRIPS
from .forms import ShipmentForm
from .matching import Shipment, evaluate_trip


@require_http_methods(["GET", "POST"])
def planner(request):
    is_example = request.method == "GET"
    shipment = DEMO_CASES.get(request.GET.get("example"), DEMO_SHIPMENT) if is_example else None
    form = ShipmentForm(initial=asdict(shipment)) if is_example else ShipmentForm(request.POST)
    if not is_example and form.is_valid():
        shipment = Shipment(**form.cleaned_data)

    context = {
        "form": form,
        "form_invalid": not is_example and shipment is None,
        "shipment": shipment,
        "is_example": is_example,
        "shipment_fields": [form[name] for name in ("pickup", "dropoff", "weight_kg", "latest_arrival")],
        "price_fields": [form[name] for name in ("farm_price", "mandi_price", "handling_fees", "unsold_kg", "hire_quote")],
    }
    if shipment:
        evaluations = [evaluate_trip(shipment, trip) for trip in DEMO_TRIPS]
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
