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
        self.assertEqual(result.mandi_net, Decimal("1150"))
        self.assertEqual(result.difference, Decimal("190"))

    def test_compatible_trip_can_still_pay_less(self):
        result = evaluate_trip(DEMO_SHIPMENT, DEMO_TRIPS[1])
        self.assertEqual(result.rejection, "")
        self.assertEqual(result.difference, Decimal("-110"))

    def test_rejections_explain_distinct_constraints(self):
        for trip, reason in zip(DEMO_TRIPS[2:], ("weight", "deadline", "before the pickup")):
            with self.subTest(trip=trip.name):
                self.assertIn(reason, evaluate_trip(DEMO_SHIPMENT, trip).rejection)

    def test_exact_capacity_and_deadline_are_allowed(self):
        shipment = replace(DEMO_SHIPMENT, weight_kg=Decimal("300"), latest_arrival=time(10, 30))
        self.assertEqual(evaluate_trip(shipment, DEMO_TRIPS[0]).rejection, "")


class PlannerTests(SimpleTestCase):
    def form_values(self, **changes):
        return {**asdict(DEMO_SHIPMENT), "latest_arrival": "14:00", **changes}

    def test_example_shows_compatible_and_excluded_trips(self):
        response = self.client.get("/")
        self.assertContains(response, "Fictional demo")
        self.assertEqual([r.trip.name for r in response.context["matches"]], ["Morning goods van", "Shared pickup"])
        self.assertEqual(len(response.context["rejections"]), 3)
        self.assertContains(response, "1,150.00")

    def test_submission_uses_form_weight_and_deadline(self):
        response = self.client.post("/", self.form_values(weight_kg="400", latest_arrival="12:00"))
        self.assertEqual([r.trip.name for r in response.context["matches"]], ["Shared pickup"])
        self.assertEqual(response.context["farm_net"], Decimal("3200"))
        self.assertFalse(response.context["is_example"])

    def test_no_match_is_a_valid_result(self):
        response = self.client.post("/", self.form_values(weight_kg="900"))
        self.assertContains(response, "No demo trips fit this shipment")
        self.assertEqual(response.context["matches"], [])

    def test_invalid_data_preserves_form_errors_without_results(self):
        response = self.client.post("/", self.form_values(dropoff=OKARA, weight_kg="0"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("dropoff", response.context["form"].errors)
        self.assertIn("weight_kg", response.context["form"].errors)
        self.assertNotContains(response, "Estimated mandi proceeds")

    def test_post_requires_csrf_token(self):
        response = Client(enforce_csrf_checks=True).post("/", self.form_values())
        self.assertEqual(response.status_code, 403)
