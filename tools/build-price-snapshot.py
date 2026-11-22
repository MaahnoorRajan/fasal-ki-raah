"""Download pinned public releases and create the reviewed website subset."""
import csv
import hashlib
import io
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data"
TARGET.mkdir(exist_ok=True)
KAGGLE = "https://www.kaggle.com/api/v1/datasets/download/amaanfaheem/pakistan-food-prices-2022?datasetVersionNumber=2"
BANK = "https://microdata.worldbank.org/api/downloads/download/PAK_2021_RTFP_v02_M/361892?filename=PAK_RTFP_mkt_2007_2026-11-17.zip"
SOURCES = {
    "kaggle": {
        "name": "Kaggle · Pakistan Food Prices 2022",
        "url": "https://www.kaggle.com/datasets/amaanfaheem/pakistan-food-prices-2022",
        "download_url": KAGGLE, "version": "Version 2 · November 2022", "retrieved": "2026-11-22",
        "license": "Uploader lists CC0. Original WFP/FAO attribution is retained.",
        "description": "Amaan Faheem's public snapshot. Selected retail rice/wheat records from Karachi, Lahore and Multan since 2018, and national annual producer averages since 2007. Producer prices are converted from PKR/tonne. Potato producer observations end in 2010.",
        "price_types": ["Historical retail observation", "National producer average"],
    },
    "worldbank": {
        "name": "World Bank · Pakistan food-price estimates",
        "url": "https://microdata.worldbank.org/catalog/8667",
        "download_url": BANK, "version": "Release 2026-11-17", "retrieved": "2026-11-22",
        "license": "World Bank dataset terms apply. Attribution: Bo Pieter Johannes Andree, Real Time Food Prices, PAK_2021_RTFP_v02_M.",
        "terms_url": "https://microdata.worldbank.org/catalog/8667/get-microdata",
        "description": "Selected monthly wheat closing estimates for Karachi, Lahore and Multan since January 2024. Values are in PKR/kg and include statistical modelling.",
        "price_types": ["Modelled monthly estimate"],
    },
}


def download(url):
    with urlopen(url, timeout=60) as response:
        return response.read()


def read_csv(archive, name):
    return csv.DictReader(io.StringIO(archive.read(name).decode("utf-8-sig")))


records = {}


def add(source, crop, market, period, frequency, price_type, price, unit):
    value = Decimal(price)
    if not value.is_finite() or value <= 0:
        raise ValueError("Invalid source price")
    key = (source, crop, market, period, price_type)
    row = dict(source=source, crop=crop, market=market, period=period, frequency=frequency,
               price_type=price_type, original_price=str(value), original_unit=unit)
    if key in records and records[key] != row:
        raise ValueError(f"Conflicting source observations: {key}")
    records[key] = row


archives = {}
for source, metadata in SOURCES.items():
    content = download(metadata["download_url"])
    metadata["archive_sha256"] = hashlib.sha256(content).hexdigest()
    archives[source] = ZipFile(io.BytesIO(content))

for row in read_csv(archives["kaggle"], "Pakistan - Food Prices_2022.csv"):
    if not row.get("date"):
        continue
    observed = datetime.strptime(row["date"], "%m/%d/%Y").date()
    if (observed.year >= 2018 and row["City market"] in ("Karachi", "Lahore", "Multan")
            and row["commodity"].startswith(("Rice", "Wheat")) and row["unit"] == "KG"
            and row["currency"] == "PKR" and row["price type"] == "Retail"
            and row["price flag"] == "actual"):
        add("kaggle", row["commodity"], row["City market"], observed.replace(day=1).isoformat(),
            "monthly", "Historical retail observation", row["price"], "PKR/kg")

for row in read_csv(archives["kaggle"], "producer-prices_pak.csv"):
    if (row.get("Year", "").isdigit() and int(row["Year"]) >= 2007
            and row["Item"] in ("Potatoes", "Wheat", "Rice", "Maize (corn)")
            and row["Element"] == "Producer Price (LCU/tonne)" and row["Months"] == "Annual value"
            and row["Value"]):
        add("kaggle", row["Item"], "Pakistan (national)", row["Year"] + "-01-01",
            "annual", "National producer average", row["Value"], "PKR/tonne")

for row in read_csv(archives["worldbank"], "PAK_RTFP_mkt_2007_2026-11-17.csv"):
    if (row["ISO3"] == "PAK" and row["currency"] == "PKR" and int(row["year"]) >= 2024
            and row["mkt_name"] in ("Karachi", "Lahore", "Multan") and row["c_wheat"]):
        add("worldbank", "Wheat", row["mkt_name"], row["price_date"], "monthly",
            "Modelled monthly estimate", row["c_wheat"], "PKR/kg")

ordered = [records[key] for key in sorted(records)]
with (TARGET / "market_prices.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(ordered[0]))
    writer.writeheader()
    writer.writerows(ordered)
(TARGET / "sources.json").write_text(json.dumps(SOURCES, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Built {len(ordered)} public price observations.")
