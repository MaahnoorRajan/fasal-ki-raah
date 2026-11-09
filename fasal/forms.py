from decimal import Decimal

from django import forms

from .demo_data import LOCATIONS

STOPS = [(place, place) for place in LOCATIONS]


class ShipmentForm(forms.Form):
    pickup = forms.ChoiceField(label="Pickup point", choices=STOPS)
    dropoff = forms.ChoiceField(label="Destination", choices=STOPS)
    weight_kg = forms.DecimalField(
        label="Load weight (kg)", min_value=Decimal("0.01"), max_value=10000,
        max_digits=7, decimal_places=2,
    )
    latest_arrival = forms.TimeField(
        label="Arrive by (Pakistan time)", input_formats=["%H:%M"],
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
    )
    farm_price = forms.DecimalField(
        label="Farm-gate offer (PKR/kg)", min_value=0, max_digits=8, decimal_places=2,
    )
    mandi_price = forms.DecimalField(
        label="Expected mandi price (PKR/kg)", min_value=0, max_digits=8, decimal_places=2,
    )
    handling_fees = forms.DecimalField(
        label="Loading and market fees (PKR total)", min_value=0, max_digits=10, decimal_places=2,
    )

    def clean(self):
        data = super().clean()
        if data.get("pickup") and data["pickup"] == data.get("dropoff"):
            self.add_error("dropoff", "Choose a destination different from the pickup point.")
        return data
