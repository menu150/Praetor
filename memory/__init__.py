# memory/__init__.py

from .memory_core import (
    save_message,
    get_connection,
    load_all_skills,
    init_db,
)

# ─── auto-create the messages table on import ──────────────────────
# this runs as soon as anyone does “import memory”
# init_db()  # Needs conn argument — do not run at import time
print("🗄️  memory package imported — running init_db()…")
init_db()
print("✅  init_db() complete.")
