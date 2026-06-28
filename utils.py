"""Shared utility functions for NoteBot Pro."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any


def build_chat_export(history: list[dict[str, Any]]) -> str:
    """Convert one chat's history into a downloadable text document."""
    lines = [
        "NoteBot Pro — Chat Export",
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        "=" * 50,
    ]

    for entry in history:
        message = str(entry.get("message", ""))

        if entry.get("role") == "user":
            lines.extend(["", "🧑 YOU:", message])
            continue

        mode = "[PDF]" if entry.get("mode") == "pdf" else "[General]"
        lines.extend(["", f"🤖 NOTEBOT {mode}:", message])

        sources = entry.get("sources", [])
        if sources:
            lines.append("📍 Sources: " + " | ".join(sources[:3]))

    return "\n".join(lines) + "\n"


def html_text(value: Any) -> str:
    """Safely display text inside the application's HTML chat cards."""
    return escape(str(value), quote=True).replace("\n", "<br>")


def make_chat_title(message: str, limit: int = 40) -> str:
    """Create a sidebar title from the first user message."""
    normalized = " ".join(message.split())

    if not normalized:
        return "New Chat"

    if len(normalized) <= limit:
        return normalized

    return normalized[:limit].rstrip() + "..."


def current_time() -> str:
    """Return a compact timestamp for sidebar chat metadata."""
    return datetime.now().strftime("%H:%M")


def current_iso_time() -> str:
    """Return an ISO timestamp suitable for sorting chat records."""
    return datetime.now().isoformat()