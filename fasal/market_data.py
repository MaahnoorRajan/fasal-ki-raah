"""Versioned source descriptions shared by imports and the public reference page."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SOURCES = json.loads((DATA_DIR / "sources.json").read_text(encoding="utf-8"))
