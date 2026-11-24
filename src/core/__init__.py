"""Core chess logic and engine interfaces (UI-independent)."""

from .board_manager import BoardManager, GameStatus, MoveRecord

__all__ = ["BoardManager", "GameStatus", "MoveRecord"]
