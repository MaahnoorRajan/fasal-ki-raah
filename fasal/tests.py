from dataclasses import asdict, replace
from datetime import time
from decimal import Decimal

from django.test import Client, SimpleTestCase

from .demo_data import DEMO_SHIPMENT, DEMO_TRIPS, OKARA
from .matching import evaluate_trip


class MatchingTests(SimpleTestCase):
    def test_suitable_trip_can_beat_farm_gate_after_all_fees(self):
        result = evaluate_trip(DEMO_SHIPMENT, DEMO_TRIPS[0])
        self.assertEqual(result.rejection, "")
        self.assertEqual(result.freight, Decimal("1500"))
        self.assertEqual(result.hire_saving, Decimal("3500"))
        self.assertEqual(result.mandi_net, Decimal("2050"))
        self.assertEqual(result.difference, Decimal("850"))

    def test_compatible_trip_can_still_pay_less(self):
        result = evaluate_trip(replace(DEMO_SHIPMENT, unsold_kg=Decimal("40")), DEMO_TRIPS[1])
        self.assertEqual(result.rejection, "")
        self.assertEqual(result.difference, Decimal("-450"))

    def test_unsold_crop_reduces_revenue_not_the_weight_to_transport(self):
        shipment = replace(DEMO_SHIPMENT, unsold_kg=Decimal("80"))
        result = evaluate_trip(shipment, DEMO_TRIPS[0])
        self.assertEqual(result.mandi_net, Decimal("50"))
        self.assertEqual(result.difference, Decimal("-1150"))
        self.assertIn("weight", evaluate_trip(shipment, DEMO_TRIPS[2]).rejection)

    def test_rejections_explain_distinct_constraints(self):
        for trip, reason in zip(DEMO_TRIPS[2:], ("weight", "deadline", "before the pickup", "Pickup is not"), strict=True):
            with self.subTest(trip=trip.name):
                self.assertIn(reason, evaluate_trip(DEMO_SHIPMENT, trip).rejection)

    def test_exact_capacity_and_deadline_are_allowed(self):
        shipment = replace(DEMO_SHIPMENT, weight_kg=Decimal("500"), latest_arrival=time(10, 30))
        self.assertEqual(evaluate_trip(shipment, DEMO_TRIPS[0]).rejection, "")

    def test_no_saving_when_full_hire_vehicle_cannot_carry_load(self):
        result = evaluate_trip(replace(DEMO_SHIPMENT, weight_kg=Decimal("550")), DEMO_TRIPS[1])
        self.assertEqual(result.freight, Decimal("6600"))
        self.assertIsNone(result.hire_saving)


class PlannerTests(SimpleTestCase):
    def form_values(self, **changes):
        return {**asdict(DEMO_SHIPMENT), "latest_arrival": "14:00", **changes}

    def test_example_shows_compatible_and_excluded_trips(self):
        response = self.client.get("/")
        self.assertContains(response, "Fictional demo")
        self.assertEqual([r.trip.name for r in response.context["matches"]], ["Morning goods van", "Shared pickup"])
        self.assertEqual(len(response.context["rejections"]), 4)
        self.assertContains(response, "2,050.00")
        self.assertContains(response, "350 kg of capacity would be unused")
        self.assertContains(response, "Prepare carrier message", count=2)

    def test_submission_uses_form_weight_and_deadline(self):
        response = self.client.post("/", self.form_values(weight_kg="550", latest_arrival="12:00"))
        self.assertEqual([r.trip.name for r in response.context["matches"]], ["Shared pickup"])
        self.assertEqual(response.context["farm_net"], Decimal("4400"))
        self.assertFalse(response.context["is_example"])

    def test_sindh_and_warehouse_examples_are_separate_routes(self):
        sindh = self.client.get("/?example=sindh")
        self.assertEqual([r.trip.name for r in sindh.context["matches"]], ["Hyderabad shared pickup"])
        self.assertEqual(sindh.context["matches"][0].hire_saving, Decimal("6000"))
        warehouse = self.client.get("/?example=warehouse")
        self.assertEqual([r.trip.name for r in warehouse.context["matches"]], ["Morning goods van"])

    def test_no_match_is_a_valid_result(self):
        response = self.client.post("/", self.form_values(weight_kg="900"))
        self.assertContains(response, "No demo trips fit this shipment")
        self.assertEqual(response.context["matches"], [])

    def test_entered_unsold_weight_changes_the_comparison(self):
        response = self.client.post("/", self.form_values(unsold_kg="20"))
        self.assertEqual(response.context["farm_net"], Decimal("1200"))
        self.assertEqual(response.context["matches"][0].mandi_net, Decimal("1550"))
        self.assertContains(response, "130 kg expected to sell")

    def test_all_unsold_still_leaves_trip_costs(self):
        response = self.client.post("/", self.form_values(unsold_kg="150"))
        self.assertEqual(response.context["matches"][0].mandi_net, Decimal("-1700"))

    def test_unsold_weight_cannot_exceed_load(self):
        response = self.client.post("/", self.form_values(unsold_kg="150.01"))
        self.assertContains(response, "Unsold weight cannot exceed the load weight.")
        self.assertNotContains(response, "Estimated proceeds after transport")

    def test_blank_unsold_weight_defaults_to_zero(self):
        response = self.client.post("/", self.form_values(unsold_kg=""))
        self.assertEqual(response.context["matches"][0].mandi_net, Decimal("2050"))

    def test_invalid_data_preserves_form_errors_without_results(self):
        response = self.client.post("/", self.form_values(dropoff=OKARA, weight_kg="0"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("dropoff", response.context["form"].errors)
        self.assertIn("weight_kg", response.context["form"].errors)
        self.assertNotContains(response, "Estimated proceeds after transport")

    def test_post_requires_csrf_token(self):
        response = Client(enforce_csrf_checks=True).post("/", self.form_values())
        self.assertEqual(response.status_code, 403)
