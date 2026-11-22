"""Create a consistent SQLite backup before a deployment migration."""
import os
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from uuid import uuid4

database = Path(os.environ["FASAL_DATABASE_PATH"]).resolve()
if database.exists():
    folder = database.parent / "backups"
    folder.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = folder / f"fasal-{stamp}-{uuid4().hex[:8]}.sqlite3"
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as source:
        with sqlite3.connect(target) as backup:
            source.backup(backup)
            if backup.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("Backup integrity check failed")
    print(f"Database backup created: {target.name}")
