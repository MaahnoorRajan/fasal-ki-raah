"""Build a single-file browser demo from the local Django planner."""
import json
import os
import re
import sys
from dataclasses import asdict
from datetime import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fasal.settings")

import django
from django.test import Client

django.setup()
from fasal.demo_data import DEMO_TRIPS

response = Client().get("/")
assert response.status_code == 200
html = response.content.decode()
css = (PROJECT / "fasal/static/fasal/planner.css").read_text(encoding="utf-8-sig")
script = (PROJECT / "tools/fasal-offline.js").read_text(encoding="utf-8-sig")


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError(f"Unexpected template change: {old!r}")
    return text.replace(old, new, 1)


def encode(value):
    if isinstance(value, time):
        return value.strftime("%H:%M")
    raise TypeError(type(value))


fixtures = json.dumps([asdict(trip) for trip in DEMO_TRIPS], default=encode).replace("<", "\\u003c")
html = replace_once(html, '<link rel="stylesheet" href="/static/fasal/planner.css">', f"<style>\n{css}\n</style>")
html = re.sub(r'<input type="hidden" name="csrfmiddlewaretoken" value="[^"]*">', "", html)
html = replace_once(html, '<form method="post" action="/#results">', '<form action="#results">')
html = replace_once(html, '<a class="brand" href="/"', '<a class="brand" href="#"')
html = replace_once(html, '<a href="/">Reset example</a>', '<a href="#" id="offline-reset">Reset example</a>')
html = replace_once(html, 'id="results" aria-labelledby=', 'id="results" tabindex="-1" aria-labelledby=')
html = replace_once(html, '<div class="baseline">', '<div id="offline-summary" aria-live="polite"><div class="baseline">')
html = replace_once(html, 'outside this estimate.</p>', 'outside this estimate.</p></div>')
html = replace_once(html, "Example only. Routes, vehicle capacity and prices are fictional. No bookings are made.",
                    "Offline demo. Routes, vehicle capacity and prices are fictional. No bookings are made.")
html = replace_once(html, "</body>", f'<script type="application/json" id="demo-trips">{fixtures}</script>\n<script>\n{script}\n</script>\n</body>')
output = PROJECT / "Open Fasal Ki Raah.html"
output.write_text(html, encoding="utf-8")
print(f"Created {output.name} ({output.stat().st_size} bytes)")
