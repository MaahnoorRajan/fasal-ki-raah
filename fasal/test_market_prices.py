import csv
from decimal import Decimal
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from .models import MarketPrice


class MarketPriceTests(TestCase):
    def test_bundled_import_is_repeatable_and_keeps_unit_conversions(self):
        call_command("import_market_prices", stdout=StringIO())
        count = MarketPrice.objects.count()
        self.assertGreater(count, 600)
        call_command("import_market_prices", stdout=StringIO())
        self.assertEqual(MarketPrice.objects.count(), count)
        potato = MarketPrice.objects.filter(crop="Potatoes").first()
        self.assertEqual(potato.original_unit, "PKR/tonne")
        self.assertEqual(potato.pkr_per_kg, (potato.original_price / 1000).quantize(Decimal(".0001")))
        self.assertEqual(potato.frequency, "annual")
        wheat = MarketPrice.objects.filter(source="worldbank", market="Karachi").first()
        self.assertEqual(wheat.price_type, "Modelled monthly estimate")
        self.assertEqual(wheat.original_price, wheat.pkr_per_kg)
        page = self.client.get(reverse("market-prices"), {"crop": "Potatoes", "market": "Pakistan (national)"})
        self.assertContains(page, "National producer average")
        self.assertContains(page, "PKR/tonne")
        self.assertNotContains(page, "<h2>Wheat")
        self.assertContains(self.client.get("/"), "Price reference")
        self.assertEqual(self.client.get(reverse("health")).status_code, 200)
        self.assertContains(self.client.get(reverse("market-prices"), {"page": "invalid"}), "Pakistan price reference")

    def test_invalid_import_leaves_existing_prices_intact(self):
        fields = ["source", "crop", "market", "period", "frequency", "price_type", "original_price", "original_unit"]
        valid = ["kaggle", "Wheat", "Karachi", "2022-01-01", "monthly", "Historical retail observation", "100", "PKR/kg"]
        with TemporaryDirectory() as folder:
            path = Path(folder) / "prices.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(fields)
                writer.writerow(valid)
                writer.writerow([*valid[:6], "-1", valid[-1]])
            with self.assertRaises(CommandError):
                call_command("import_market_prices", file=str(path))
        self.assertFalse(MarketPrice.objects.exists())
        self.assertEqual(self.client.get(reverse("health")).status_code, 503)
