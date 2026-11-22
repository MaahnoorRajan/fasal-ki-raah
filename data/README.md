# Public price snapshot

The bundled market_prices.csv contains a reviewed subset from two public downloads. sources.json records publisher links, release versions, retrieval date, archive hashes, units and reuse notes. Rebuild with python tools/build-price-snapshot.py.

- Kaggle's Pakistan Food Prices 2022, by Amaan Faheem, version 2. The uploader lists CC0. The source files include WFP food-price observations and FAO producer prices, and original-source attribution is retained. Retail observations cover selected rice/wheat products in Karachi, Lahore and Multan from 2018 through September 2022. National producer averages use selected annual records from 2007 onwards.
- World Bank Real Time Food Prices, Pakistan, release 2026-11-17, by Bo Pieter Johannes Andree. The subset uses c_wheat, the monthly closing estimate, in PKR/kg for Karachi, Lahore and Multan since 2024. Estimates include statistical modelling and are subject to the World Bank dataset terms.

These are different price series. Retail records, national producer averages and modelled estimates retain separate labels. Potato producer prices in the downloaded files end in 2010. Crop price indices are excluded because an index is not a price in rupees.

The importer converts PKR/tonne by dividing by 1,000, retains the original value and unit, and stores PKR/kg to four decimal places. Annual and monthly observation periods are displayed separately. It rejects invalid units, negative prices and duplicate observation keys before writing. A transaction covers the import, and importing the same snapshot again updates the existing observations.

The website's Price reference page supports crop, market and source filters. It provides context for learning and research. Farmers enter a current buyer quote into the shipment calculator.

AMIS retrieval failed during this integration, so the release contains no AMIS rows. Links to PBS crop statistics and OpenStreetMap Pakistan extracts are provided as further research resources. District production data and geographic routing have not been imported.

Sources are [Kaggle](https://www.kaggle.com/datasets/amaanfaheem/pakistan-food-prices-2022) and [World Bank](https://microdata.worldbank.org/catalog/8667). Consult each source's reuse terms before redistributing a broader dataset.
