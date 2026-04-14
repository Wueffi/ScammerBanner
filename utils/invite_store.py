import json
from pathlib import Path

INVITE_FILE = Path("invite_store.json")

def load_invites() -> set[str]:
    if not INVITE_FILE.exists():
        return set()
    return set(json.loads(INVITE_FILE.read_text()))

def save_invites(invites: set[str]) -> None:
    INVITE_FILE.write_text(json.dumps(list(invites), indent=2))