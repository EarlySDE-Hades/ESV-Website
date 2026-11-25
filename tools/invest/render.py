"""Fills the {{…}} placeholders in tools/invest/main.html from links.json. Called by tools/team/build.py."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def render():
    links = json.loads((HERE / "links.json").read_text(encoding="utf-8"))
    return {"{{%s_HREF}}" % key.upper(): links[key] for key in ("syndicate", "partner")}
