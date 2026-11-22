import csv
from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db import transaction

from fasal.market_data import DATA_DIR, SOURCES
from fasal.models import MarketPrice


class Command(BaseCommand):
    help = "Validate and import the bundled public price snapshot atomically."

    def add_arguments(self, parser):
        parser.add_argument("--file", default=str(DATA_DIR / "market_prices.csv"))

    def handle(self, *args, **options):
        records = []
        seen = set()
        try:
            with open(options["file"], encoding="utf-8", newline="") as stream:
                for row in csv.DictReader(stream):
                    original = Decimal(row["original_price"])
                    unit = row["original_unit"]
                    normal = original / {"PKR/kg": 1, "PKR/tonne": 1000}[unit]
                    key = tuple(row[name] for name in ("source", "crop", "market", "period", "price_type"))
                    source = SOURCES[row["source"]]
                    if (key in seen or not original.is_finite() or original <= 0
                            or row["frequency"] not in ("annual", "monthly")
                            or row["price_type"] not in source["price_types"]
                            or not row["crop"].strip() or not row["market"].strip()):
                        raise ValueError("Duplicate or invalid observation")
                    seen.add(key)
                    item = MarketPrice(
                        **{name: row[name] for name in ("source", "crop", "market", "frequency", "price_type")},
                        period=date.fromisoformat(row["period"]), original_price=original,
                        original_unit=unit, pkr_per_kg=normal.quantize(Decimal("0.0001")),
                    )
                    item.full_clean(validate_unique=False, validate_constraints=False)
                    records.append(item)
        except (OSError, KeyError, ValueError, InvalidOperation, ValidationError) as error:
            raise CommandError(f"Price import failed: {error}") from error
        if not records:
            raise CommandError("Price import failed: no observations found.")
        with transaction.atomic():
            for item in records:
                MarketPrice.objects.update_or_create(
                    source=item.source, crop=item.crop, market=item.market,
                    period=item.period, price_type=item.price_type,
                    defaults={name: getattr(item, name) for name in (
                        "frequency", "original_price", "original_unit", "pkr_per_kg",
                    )},
                )
        self.stdout.write(self.style.SUCCESS(f"Imported {len(records)} price observations."))
