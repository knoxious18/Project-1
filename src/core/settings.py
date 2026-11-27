"""Application settings persistence (UI-independent)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_SETTINGS_PATH = Path("settings.json")


@dataclass
class AppSettings:
    """User-configurable appearance and animation preferences."""

    ui_mode: str = "light"
    board_theme: str = "classic_green"
    piece_style: str = "classic"
    animation_speed: str = "fast"


def load_settings(path: Path = DEFAULT_SETTINGS_PATH) -> AppSettings:
    """Loads settings from JSON file, falling back to defaults on error."""
    if not path.exists():
        return AppSettings()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        defaults = AppSettings()
        return AppSettings(
            ui_mode=str(data.get("ui_mode", defaults.ui_mode)),
            board_theme=str(data.get("board_theme", defaults.board_theme)),
            piece_style=str(data.get("piece_style", defaults.piece_style)),
            animation_speed=str(data.get("animation_speed", defaults.animation_speed)),
        )
    except (OSError, ValueError, TypeError):
        return AppSettings()


def save_settings(settings: AppSettings, path: Path = DEFAULT_SETTINGS_PATH) -> None:
    """Persists settings to JSON file."""
    path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
