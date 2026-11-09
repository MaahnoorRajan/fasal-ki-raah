from datetime import time
from decimal import Decimal

from .matching import Shipment, Stop, Trip

OKARA = "Okara collection point"
DEPALPUR = "Depalpur collection point"
SAHIWAL = "Sahiwal mandi"
LOCATIONS = (OKARA, DEPALPUR, SAHIWAL)

# Fictional vehicles, stop orders, schedules and prices. No carriers are listed.
DEMO_TRIPS = (
    Trip("Morning goods van", (Stop(OKARA, time(8)), Stop(SAHIWAL, time(10, 30))), 300, 450),
    Trip("Shared pickup", (Stop(DEPALPUR, time(8)), Stop(OKARA, time(9)), Stop(SAHIWAL, time(12))), 600, 750),
    Trip("Small van", (Stop(OKARA, time(9)), Stop(SAHIWAL, time(11))), 75, 350),
    Trip("Afternoon goods van", (Stop(OKARA, time(14)), Stop(SAHIWAL, time(15, 30))), 500, 400),
    Trip("Return pickup", (Stop(SAHIWAL, time(9)), Stop(OKARA, time(11))), 250, 380),
)

DEMO_SHIPMENT = Shipment(OKARA, SAHIWAL, Decimal("120"), time(14), Decimal("8"), Decimal("15"), Decimal("200"))
