(() => {
  const dialog = document.getElementById("carrier-dialog");
  const form = document.getElementById("carrier-form");
  const message = document.getElementById("carrier-message");
  const phone = document.getElementById("carrier-number");
  const link = document.getElementById("carrier-link");
  const status = document.getElementById("copy-status");
  const note = document.getElementById("carrier-note");
  const demoNote = note.textContent;
  function clearLink() {
    link.hidden = true;
    link.removeAttribute("href");
    phone.setCustomValidity("");
  }
  document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-contact]");
    if (!button) return;
    const {pickup, dropoff, weight, arrival, phone: listedPhone, date} = button.dataset;
    form.reset();
    clearLink();
    status.textContent = "";
    phone.value = listedPhone || "";
    phone.readOnly = Boolean(listedPhone);
    note.textContent = listedPhone ? "This driver chose to share their number. Review your inquiry before opening WhatsApp." : demoNote;
    message.value = `Assalam-o-alaikum. Do you have room for ${weight} kg of potatoes from ${pickup} to ${dropoff}? I need arrival by ${arrival} Pakistan time${date ? " on " + date : ""}. Please confirm the date, available space, pickup point and total freight in PKR, including any loading charges.`;
    dialog.showModal();
  });
  document.getElementById("close-carrier").addEventListener("click", () => dialog.close());
  document.getElementById("copy-inquiry").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(message.value);
      status.textContent = "Inquiry copied.";
    } catch {
      message.select();
      status.textContent = "Inquiry selected. Use your device’s Copy command.";
    }
  });
  phone.addEventListener("input", clearLink);
  message.addEventListener("input", clearLink);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    clearLink();
    const entered = phone.value.trim().replace(/[\s()-]/g, "");
    if (!/^(?:\+92|92|0)3\d{9}$/.test(entered)) {
      phone.setCustomValidity("Enter a Pakistan mobile number beginning with 03 or +923.");
      phone.reportValidity();
      return;
    }
    const number = entered.startsWith("0") ? "92" + entered.slice(1) : entered.replace(/^\+/, "");
    link.href = `https://wa.me/${number}?text=${encodeURIComponent(message.value)}`;
    link.hidden = false;
    link.focus();
  });
})();
