const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync("Open Fasal Ki Raah.html", "utf8");
assert.match(html, /<style>/);
assert.match(html, /2,050\.00/);
assert.doesNotMatch(html, /<script[^>]+src=|<link[^>]+stylesheet|csrfmiddlewaretoken/);
const fixtures = html.match(/id="demo-trips">([\s\S]*?)<\/script>/)[1];
const js = html.match(/<script id="offline-planner">\s*([\s\S]*?)<\/script>/)[1];
const handlers = {};
const dropoff = {
  message: "",
  setCustomValidity(message) { this.message = message; },
  reportValidity() {},
  addEventListener() {},
};
const unsold = {...dropoff};
const form = {
  elements: {dropoff, unsold_kg: unsold, pickup: {addEventListener() {}}, weight_kg: {addEventListener() {}}},
  addEventListener(event, callback) { handlers[event] = callback; },
};
const summary = {innerHTML: ""};
const ids = {
  "demo-trips": {textContent: fixtures},
  "demo-cases": {textContent: html.match(/id="demo-cases">([\s\S]*?)<\/script>/)[1]},
  "results": {focus() {}, scrollIntoView() {}},
  "offline-summary": summary,
  "offline-reset": {addEventListener() {}},
};
const fields = new Map(Object.entries({
  pickup: "Okara collection point", dropoff: "Sahiwal mandi",
  latest_arrival: "14:00", weight_kg: "150", farm_price: "8",
  mandi_price: "25", handling_fees: "200", hire_quote: "5000",
}));
vm.runInNewContext(js, {
  document: {getElementById: (id) => ids[id], querySelector: () => form, querySelectorAll: () => []},
  FormData: function () { return fields; },
});
const submit = () => handlers.submit({preventDefault() {}});
submit();
assert.match(summary.innerHTML, /\+850\.00/);
assert.match(summary.innerHTML, /3,500\.00 less than whole hire/);
assert.match(summary.innerHTML, /350 kg of capacity would be unused/);
assert.match(summary.innerHTML, /2 trips fit/);
fields.set("unsold_kg", "20");
submit();
assert.match(summary.innerHTML, /130 kg expected to sell/);
assert.match(summary.innerHTML, /PKR 1,550\.00/);
assert.match(summary.innerHTML, /PKR 1,200\.00/);
fields.set("unsold_kg", "150");
submit();
assert.match(summary.innerHTML, /PKR -1,700\.00/);
fields.set("unsold_kg", "150.01");
submit();
assert.match(unsold.message, /cannot exceed the load weight/);
fields.set("unsold_kg", "");
fields.set("weight_kg", "550");
fields.set("latest_arrival", "12:00");
submit();
assert.match(summary.innerHTML, /1 trip fit/);
assert.match(summary.innerHTML, /<h3>Shared pickup<\/h3>/);
assert.doesNotMatch(summary.innerHTML, /less than whole hire/);
fields.set("weight_kg", "900");
submit();
assert.match(summary.innerHTML, /No demo trips fit/);
fields.set("dropoff", fields.get("pickup"));
submit();
assert.match(dropoff.message, /different from the pickup/);

const carrierEvents = {};
const control = (name) => ({
  value: "", setCustomValidity(message) { this.error = message; }, reportValidity() {},
  addEventListener(event, callback) { carrierEvents[name + ":" + event] = callback; },
  removeAttribute(attribute) { delete this[attribute]; }, focus() {},
});
const carrierIds = Object.fromEntries(
  ["carrier-dialog", "carrier-form", "carrier-message", "carrier-number", "carrier-link",
    "copy-status", "close-carrier", "copy-inquiry"].map((name) => [name, control(name)]),
);
carrierIds["carrier-form"].reset = () => {};
carrierIds["carrier-dialog"].showModal = () => {};
vm.runInNewContext(html.match(/<script>\s*([\s\S]*?)<\/script>/)[1], {
  document: {
    getElementById: (id) => carrierIds[id],
    addEventListener(event, callback) { carrierEvents[event] = callback; },
  },
});
carrierEvents.click({target: {closest: () => ({dataset: {
  weight: "150", pickup: "Okara collection point", dropoff: "Sahiwal warehouse", arrival: "14:00",
}})}});
assert.match(carrierIds["carrier-message"].value, /150 kg.*Sahiwal warehouse/);
assert.equal(carrierIds["carrier-link"].hidden, true);
const submitCarrier = () => carrierEvents["carrier-form:submit"]({preventDefault() {}});
carrierIds["carrier-number"].value = "123";
submitCarrier();
assert.match(carrierIds["carrier-number"].error, /Pakistan mobile number/);
assert.equal(carrierIds["carrier-link"].hidden, true);
carrierIds["carrier-number"].value = "0300 0000000";
submitCarrier();
assert.match(carrierIds["carrier-link"].href, /^https:\/\/wa\.me\/923000000000\?text=/);
carrierEvents["carrier-message:input"]();
assert.equal(carrierIds["carrier-link"].hidden, true);
assert.equal(carrierIds["carrier-link"].href, undefined);
console.log("Offline checks passed: price comparison, load filters, and editable carrier inquiry and link validation.");
