from datetime import time
from decimal import Decimal

from .matching import Shipment, Stop, Trip

OKARA = "Okara collection point"
DEPALPUR = "Depalpur collection point"
SAHIWAL = "Sahiwal mandi"
WAREHOUSE = "Sahiwal warehouse"
KARACHI = "Karachi collection point"
HYDERABAD = "Hyderabad mandi"
LOCATIONS = (OKARA, DEPALPUR, SAHIWAL, WAREHOUSE, KARACHI, HYDERABAD)

# Fictional vehicles, stop orders, schedules and prices. No carriers are listed.
DEMO_TRIPS = (
    Trip("Morning goods van", (Stop(OKARA, time(8)), Stop(SAHIWAL, time(10, 30)), Stop(WAREHOUSE, time(11))), 500, 10),
    Trip("Shared pickup", (Stop(DEPALPUR, time(8)), Stop(OKARA, time(9)), Stop(SAHIWAL, time(12))), 600, 12),
    Trip("Small van", (Stop(OKARA, time(9)), Stop(SAHIWAL, time(11))), 75, 9),
    Trip("Afternoon goods van", (Stop(OKARA, time(14)), Stop(SAHIWAL, time(15, 30))), 500, 8),
    Trip("Return pickup", (Stop(SAHIWAL, time(9)), Stop(OKARA, time(11))), 250, 8),
    Trip("Hyderabad shared pickup", (Stop(KARACHI, time(8)), Stop(HYDERABAD, time(12, 30))), 500, 20),
)

DEMO_SHIPMENT = Shipment(OKARA, SAHIWAL, Decimal("150"), time(14), Decimal("8"),
                         Decimal("25"), Decimal("200"), hire_quote=Decimal("5000"))
DEMO_CASES = {
    "punjab": DEMO_SHIPMENT,
    "warehouse": Shipment(OKARA, WAREHOUSE, Decimal("150"), time(14), Decimal("8"),
                          Decimal("25"), Decimal("200"), hire_quote=Decimal("5000")),
    "sindh": Shipment(KARACHI, HYDERABAD, Decimal("150"), time(14), Decimal("8"),
                      Decimal("35"), Decimal("200"), hire_quote=Decimal("9000")),
}
