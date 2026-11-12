# Run the Fasal Ki Raah prototype

## Offline demo

Download [Open Fasal Ki Raah.html](../Open%20Fasal%20Ki%20Raah.html) and open it in your browser. The form and fictional trip calculations run in the browser. No server is needed.

## Django development setup

Open a terminal in the project folder. With Python 3.10 or newer available on your PATH, run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8765
```

Open http://127.0.0.1:8765 in your browser. Stop the server with Ctrl+C. This is a local development server using fictional data.

If the browser cannot connect, make sure the server command is still running and open the address in a regular desktop browser. Use the offline demo if you just want to try the workflow.

## Try three scenarios

1. Start with **Punjab · mandi**. A 150 kg load uses 30% of a dedicated 500 kg pickup. The morning van's illustrative PKR 10/kg rate gives PKR 1,500 freight versus the editable PKR 5,000 dedicated quote.
2. Enter 20 kg in **Expected unsold after transport**. The morning van estimate drops from PKR 2,050 to PKR 1,550 after freight and fees. Freight still uses all 150 kg.
3. Switch to **Punjab · warehouse** for a storage drop-off, or **Sindh · mandi** for a separate Karachi–Hyderabad scenario. See the [freight benchmarks](FREIGHT-BENCHMARKS.md) for the origin and limits of the quotes.
4. Select **Prepare carrier message** on a matching trip. Copy the inquiry, or enter a known carrier's number to prepare a WhatsApp draft. The demo has no assigned drivers.

These are example inputs and quotes. The farm-gate offer assumes a buyer collects and pays for the full load. The mandi estimate applies the entered price only to the weight expected to sell; it still deducts the full freight and fees. The planner does not look up market rates, find buyers, reserve space, or confirm delivery.

## Learn by tracing one request

1. The form in **fasal/templates/fasal/planner.html** sends the shipment.
2. **fasal/forms.py** checks the input, then **fasal/views.py** creates a Shipment.
3. **fasal/matching.py** calls the original Python route check and adds weight, deadline and sale calculations.
4. The template shows the outcomes. Change an example shared rate in **fasal/demo_data.py**, predict the difference, and check the result. The contact script prepares a draft locally; it does not send or book.

## Checks

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test fasal
.\.venv\Scripts\python.exe -m unittest discover -s matching_lab
```

If you edit the planner or its fictional trips, rebuild the standalone HTML with `.\.venv\Scripts\python.exe tools/export-fasal-preview.py` and check it with `node tools/check-fasal-preview.cjs`.

The website code was prepared with AI assistance as a learning prototype. Future decisions about a real crop corridor, drivers, buyer availability, and prices need evidence.
