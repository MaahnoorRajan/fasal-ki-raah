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


@dataclass(frozen=True)
class Stop:
    name: str
    arrival: time


@dataclass(frozen=True)
class Trip:
    name: str
    stops: tuple[Stop, ...]
    spare_kg: int
    quote: int


@dataclass(frozen=True)
class Evaluation:
    trip: Trip
    rejection: str = ""
    arrival: time | None = None
    mandi_net: Decimal | None = None
    difference: Decimal | None = None


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

    # A quote covers this whole demo shipment, not each kilogram.
    farm_net = shipment.weight_kg * shipment.farm_price
    mandi_net = shipment.weight_kg * shipment.mandi_price - trip.quote - shipment.handling_fees
    return Evaluation(trip, arrival=arrival, mandi_net=mandi_net, difference=mandi_net - farm_net)
