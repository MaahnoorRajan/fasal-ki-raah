const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync("Open Fasal Ki Raah.html", "utf8");
assert.match(html, /<style>/);
assert.match(html, /1,150\.00/);
assert.doesNotMatch(html, /<script[^>]+src=|<link[^>]+stylesheet|csrfmiddlewaretoken/);
const fixtures = html.match(/id="demo-trips">([\s\S]*?)<\/script>/)[1];
const js = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
const handlers = {};
const dropoff = {
  message: "",
  setCustomValidity(message) { this.message = message; },
  reportValidity() {},
  addEventListener() {},
};
const form = {
  elements: {dropoff, pickup: {addEventListener() {}}},
  addEventListener(event, callback) { handlers[event] = callback; },
};
const summary = {innerHTML: ""};
const ids = {
  "demo-trips": {textContent: fixtures},
  "results": {focus() {}, scrollIntoView() {}},
  "offline-summary": summary,
  "offline-reset": {addEventListener() {}},
};
const fields = new Map(Object.entries({
  pickup: "Okara collection point", dropoff: "Sahiwal mandi",
  latest_arrival: "14:00", weight_kg: "120", farm_price: "8",
  mandi_price: "15", handling_fees: "200",
}));
vm.runInNewContext(js, {
  document: {getElementById: (id) => ids[id], querySelector: () => form},
  FormData: function () { return fields; },
});
const submit = () => handlers.submit({preventDefault() {}});
submit();
assert.match(summary.innerHTML, /\+190\.00/);
assert.match(summary.innerHTML, /-110\.00/);
assert.match(summary.innerHTML, /2 trips fit/);
fields.set("weight_kg", "400");
fields.set("latest_arrival", "12:00");
submit();
assert.match(summary.innerHTML, /1 trip fit/);
assert.match(summary.innerHTML, /<h3>Shared pickup<\/h3>/);
fields.set("weight_kg", "900");
submit();
assert.match(summary.innerHTML, /No demo trips fit/);
fields.set("dropoff", fields.get("pickup"));
submit();
assert.match(dropoff.message, /different from the pickup/);
console.log("Standalone HTML checks passed: example, deadline and capacity filters, no match, and invalid route.");
