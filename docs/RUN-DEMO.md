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

1. Start with the 120 kg example. Two trips fit. The morning van leaves an estimated PKR 1,150 from a mandi sale versus PKR 960 at the farm gate. The shared pickup fits the trip rules but comes out PKR 110 below the farm-gate example after fees.
2. Change the weight to 400 kg and the deadline to 12:00. Only the shared pickup fits.
3. Change the weight to 900 kg. No demo trip has enough space. Expand the excluded trips section to see the reasons.

These are example inputs and quotes. The planner assumes that the whole load sells at the entered price. It does not look up market rates, find buyers, reserve space, or confirm delivery.

## Learn by tracing one request

1. The form in **fasal/templates/fasal/planner.html** sends the shipment.
2. **fasal/forms.py** checks the input, then **fasal/views.py** creates a Shipment.
3. **fasal/matching.py** calls the original Python route check and adds weight, deadline and sale calculations.
4. The template shows the outcomes. Change an example quote in **fasal/demo_data.py**, predict the difference, and check the result.

## Checks

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test fasal
.\.venv\Scripts\python.exe -m unittest discover -s matching_lab
```

If you edit the planner or its fictional trips, rebuild the standalone HTML with `.\.venv\Scripts\python.exe tools/export-fasal-preview.py` and check it with `node tools/check-fasal-preview.cjs`.

The website code was prepared with AI assistance as a learning prototype. Future decisions about a real crop corridor, drivers, buyer availability, and prices need evidence.
