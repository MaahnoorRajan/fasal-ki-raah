"""Business rules for the demo. This module can be used without Django."""

from dataclasses import dataclass
from datetime import time
from decimal import Decimal

from matching_lab.match_routes import check_route


@dataclass(frozen=True)
class Shipment:
    pickup: str
    dropoff: str
    weight_kg: Decimal
    latest_arrival: time
    farm_price: Decimal
    mandi_price: Decimal
    handling_fees: Decimal
    unsold_kg: Decimal = Decimal("0")
    hire_quote: Decimal | None = None

    @property
    def saleable_kg(self) -> Decimal:
        return self.weight_kg - self.unsold_kg


@dataclass(frozen=True)
class Stop:
    name: str
    arrival: time


@dataclass(frozen=True)
class Trip:
    name: str
    stops: tuple[Stop, ...]
    spare_kg: int
    rate_per_kg: int
    contact_phone: str = ""
    is_listing: bool = False


@dataclass(frozen=True)
class Evaluation:
    trip: Trip
    rejection: str = ""
    arrival: time | None = None
    mandi_net: Decimal | None = None
    difference: Decimal | None = None
    freight: Decimal | None = None
    hire_saving: Decimal | None = None


def evaluate_trip(shipment: Shipment, trip: Trip) -> Evaluation:
    route_ok, reason = check_route(
        [stop.name for stop in trip.stops], shipment.pickup, shipment.dropoff
    )
    if not route_ok:
        return Evaluation(trip, rejection=reason)
    if shipment.weight_kg > trip.spare_kg:
        return Evaluation(trip, rejection="Not enough spare weight capacity.")

    arrival = next(stop.arrival for stop in trip.stops if stop.name == shipment.dropoff)
    if arrival > shipment.latest_arrival:
        return Evaluation(trip, rejection="Reaches the destination after your deadline.")

    # Shared freight uses loaded weight, even when some produce goes unsold.
    freight = shipment.weight_kg * trip.rate_per_kg
    farm_net = shipment.weight_kg * shipment.farm_price
    mandi_net = shipment.saleable_kg * shipment.mandi_price - freight - shipment.handling_fees
    hire_saving = (shipment.hire_quote - freight
                   if shipment.hire_quote is not None and shipment.weight_kg <= 500 else None)
    return Evaluation(trip, arrival=arrival, mandi_net=mandi_net, difference=mandi_net - farm_net,
                      freight=freight, hire_saving=hire_saving)
