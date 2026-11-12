(() => {
  "use strict";
  const trips = JSON.parse(document.getElementById("demo-trips").textContent);
  const form = document.querySelector("form");
  const results = document.getElementById("results");
  const summary = document.getElementById("offline-summary");
  const currency = new Intl.NumberFormat("en-PK", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  const kilos = new Intl.NumberFormat("en-PK", {maximumFractionDigits: 2});
  const number = (value) => currency.format(value / 10000);
  const scaled = (value) => Math.round(Number(value) * 100);

  // Same demo checks as the Django version. Prices and weights are scaled
  // integers so a comparison is exact even when the form uses decimals.
  function evaluate(data, trip) {
    const pickup = trip.stops.findIndex((stop) => stop.name === data.pickup);
    const dropoff = trip.stops.findIndex((stop) => stop.name === data.dropoff);
    let rejection = "";
    if (pickup === -1) rejection = "Pickup is not on this trip.";
    else if (dropoff === -1) rejection = "Drop-off is not on this trip.";
    else if (pickup > dropoff) rejection = "This trip reaches the drop-off before the pickup.";
    else if (data.weight > trip.spare_kg * 100) rejection = "Not enough spare weight capacity.";
    else if (trip.stops[dropoff].arrival > data.deadline) rejection = "Reaches the destination after your deadline.";
    if (rejection) return {trip, rejection};
    const mandi = data.saleable * data.mandiPrice - trip.quote * 10000 - data.handling * 100;
    return {trip, arrival: trip.stops[dropoff].arrival, mandi, difference: mandi - data.farmNet};
  }

  function tripCard({trip, arrival, mandi, difference}) {
    return `<article class="trip">
      <div class="trip-head"><h3>${trip.name}</h3><span class="fit">Route fits</span></div>
      <p>Arrives ${arrival} · ${trip.spare_kg} kg spare · PKR ${trip.quote} freight</p>
      <div class="trip-estimate">
        <div><small>Estimated mandi proceeds</small><strong>PKR ${number(mandi)}</strong></div>
        <span class="delta ${difference < 0 ? "lower" : ""}">${difference > 0 ? "+" : ""}${number(difference)} vs farm gate</span>
      </div></article>`;
  }

  function showResults(data) {
    const checked = trips.map((trip) => evaluate(data, trip));
    const matches = checked.filter((row) => !row.rejection).sort((a, b) => b.mandi - a.mandi);
    const rejected = checked.filter((row) => row.rejection);
    const count = (total) => `${total} trip${total === 1 ? "" : "s"}`;
    // Only the fixed, bundled demo dataset and formatted numbers enter this HTML.
    summary.innerHTML = `
      <div class="baseline"><div><strong>Farm-gate sale</strong><small>Buyer collects the whole load</small></div>
      <strong>PKR ${number(data.farmNet)}</strong></div>
      <p class="sale-weight">${kilos.format(data.saleable / 100)} kg expected to sell at the mandi · ${kilos.format(data.unsold / 100)} kg unsold</p>
      ${matches.length ? `<p class="results-count">${count(matches.length)} fit · highest estimated proceeds first</p>
      <div class="trips">${matches.map(tripCard).join("")}</div>` :
      '<p class="empty">No demo trips fit this shipment. Check the route, try a smaller load, or adjust the deadline.</p>'}
      ${rejected.length ? `<details class="rejected"><summary>${count(rejected.length)} excluded · see why</summary><ul>
      ${rejected.map(({trip, rejection}) => `<li><strong>${trip.name}</strong><span>${rejection}</span></li>`).join("")}
      </ul></details>` : ""}
      <p class="calculation-note">Mandi estimate = value of sold produce − freight − loading and market fees. Freight covers the whole load. Production costs and buyer availability are outside this estimate.</p>`;
  }

  const dropoffInput = form.elements.dropoff;
  const clearError = () => dropoffInput.setCustomValidity("");
  form.elements.pickup.addEventListener("change", clearError);
  dropoffInput.addEventListener("change", clearError);
  const unsoldInput = form.elements.unsold_kg;
  const clearWeightError = () => unsoldInput.setCustomValidity("");
  unsoldInput.addEventListener("input", clearWeightError);
  form.elements.weight_kg.addEventListener("input", clearWeightError);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const fields = new FormData(form);
    if (fields.get("pickup") === fields.get("dropoff")) {
      dropoffInput.setCustomValidity("Choose a destination different from the pickup point.");
      dropoffInput.reportValidity();
      return;
    }
    const weight = scaled(fields.get("weight_kg"));
    const unsold = scaled(fields.get("unsold_kg") || 0);
    if (unsold > weight) {
      unsoldInput.setCustomValidity("Unsold weight cannot exceed the load weight.");
      unsoldInput.reportValidity();
      return;
    }
    showResults({
      pickup: fields.get("pickup"),
      dropoff: fields.get("dropoff"),
      deadline: fields.get("latest_arrival"),
      weight,
      unsold,
      saleable: weight - unsold,
      farmNet: weight * scaled(fields.get("farm_price")),
      mandiPrice: scaled(fields.get("mandi_price")),
      handling: scaled(fields.get("handling_fees")),
    });
    results.focus();
    results.scrollIntoView({block: "nearest"});
  });
  document.getElementById("offline-reset").addEventListener("click", (event) => {
    event.preventDefault();
    location.reload();
  });
})();
