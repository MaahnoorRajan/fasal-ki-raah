# ReturnLoad matching lab: stop order

This is a small Python learning exercise. The trips use familiar Karachi place names as fictional fixtures. They do not represent verified road routes, operators, customer demand, or an approved pilot corridor.

## Run the example

In a terminal opened in this folder, with Python 3.10 or newer available:

~~~powershell
python match_routes.py
python -m unittest -v
~~~

Expected result: Trip A matches, Trip B fails because it travels in the wrong direction, and Trip C fails because it does not reach the drop-off.

If Windows opens the Store or reports no installed Python, you can read the script and work through the first exercise below while you set up your Python environment. The bundled Codex runtime is enough to verify the files here.

## Your next 30-minute exercise: check weight

1. Read check_route and explain in your own words why checking for both place names is insufficient.
2. Write a function named fits_weight(shipment_kg, available_kg). For this exercise, assume both inputs are already valid positive numbers. Return whether there is enough remaining capacity.
3. Check three cases for a 5 kg shipment: 8 kg available should pass; 5 kg should also pass; 4 kg should fail.
4. Try adding the check to the demo after the route check. Make sure a trip that passes weight still fails if it travels in the wrong direction.

Weight is one more filter. Package dimensions, delivery time, and reservations are outside this exercise. Keep the numbers fictional. The route check assumes exact stop names and no repeated stops.

If the checks pass, this is a candidate for your first implementation commit: Add weight checks to the ReturnLoad matching lab. The base route matcher and its tests were prepared with AI assistance.

## Keep discovery moving

In a separate short session, ask a friend, classmate, or relative for one introduction to a Karachi sender or driver. See the [interview kit](../docs/DISCOVERY.md). Code that works with fictional trips is useful practice; it does not validate the delivery problem.
