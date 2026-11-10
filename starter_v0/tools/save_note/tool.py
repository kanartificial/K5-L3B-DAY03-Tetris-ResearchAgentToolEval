from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from tools._shared import ROOT, err


NOTES_DIR = ROOT / "notes"


def save_note(
    title: str = "",
    content: str = "",
    source_url: str = "",
    confirmed: bool = False,
) -> dict[str, Any]:
    try:
        if not isinstance(confirmed, bool):
            raise ValueError("confirmed must be a boolean")
        if not confirmed:
            return {
                "tool": "save_note",
                "status": "needs_confirmation",
                "message": "Only save after the user explicitly confirms.",
            }
        for name, value in (("title", title), ("content", content), ("source_url", source_url)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        note_id = uuid4().hex
        note = {
            "note_id": note_id,
            "title": title.strip(),
            "content": content.strip(),
            "source_url": source_url.strip(),
        }
        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        with (NOTES_DIR / f"{note_id}.json").open("x", encoding="utf-8") as handle:
            json.dump(note, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        return {"tool": "save_note", "status": "saved", "note_id": note_id}
    except (OSError, TypeError, ValueError) as exc:
        return err("save_note", exc)
