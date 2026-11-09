import unittest

from match_routes import check_route


class RouteMatchingTests(unittest.TestCase):
    stops = ["Korangi", "Saddar", "Clifton"]

    def test_pickup_precedes_dropoff(self):
        self.assertTrue(check_route(self.stops, "Saddar", "Clifton")[0])

    def test_trip_going_the_wrong_direction_is_rejected(self):
        self.assertFalse(check_route(self.stops, "Clifton", "Korangi")[0])

    def test_missing_pickup_is_rejected(self):
        self.assertFalse(check_route(self.stops, "Gulshan", "Clifton")[0])

    def test_missing_dropoff_is_rejected(self):
        self.assertFalse(check_route(self.stops, "Korangi", "Gulshan")[0])

    def test_same_pickup_and_dropoff_is_rejected(self):
        self.assertFalse(check_route(self.stops, "Saddar", "Saddar")[0])


if __name__ == "__main__":
    unittest.main()
