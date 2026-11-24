"""Core chess logic and engine interfaces (UI-independent)."""

from .board_manager import BoardManager, GameStatus, MoveRecord
from .settings import AppSettings, load_settings, save_settings

__all__ = [
    "AppSettings",
    "BoardManager",
    "GameStatus",
    "MoveRecord",
    "load_settings",
    "save_settings",
]