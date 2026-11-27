"""Qt background thread wrapper for non-blocking Stockfish search."""

from __future__ import annotations

import logging
from typing import Optional

import chess
import chess.engine
from PySide6.QtCore import QObject, QThread, Signal, Slot

from src.engine.engine_manager import EngineManager

logger = logging.getLogger(__name__)


class _EngineWorker(QObject):
    """Worker living inside a dedicated QThread."""

    move_ready = Signal(str, int)
    engine_error = Signal(str)
    thinking_changed = Signal(bool)

    def __init__(self, manager: EngineManager) -> None:
        super().__init__()
        self._manager = manager

    @Slot(str, int, object, object, int, int, int, int)
    def run_search(
        self,
        fen: str,
        difficulty_level: int,
        wtime_ms: Optional[int],
        btime_ms: Optional[int],
        winc_ms: int,
        binc_ms: int,
        multipv: int,
        request_id: int,
    ) -> None:
        self.thinking_changed.emit(True)
        try:
            board = chess.Board(fen)
            move = self._search_with_recovery(
                board=board,
                difficulty_level=difficulty_level,
                wtime_ms=wtime_ms,
                btime_ms=btime_ms,
                winc_ms=winc_ms,
                binc_ms=binc_ms,
                multipv=multipv,
            )
            if move is not None:
                self.move_ready.emit(move.uci(), request_id)
        except FileNotFoundError as exc:
            self.engine_error.emit(str(exc))
        except Exception as exc:
            logger.exception("Engine search failed")
            self.engine_error.emit(f"Lỗi engine Stockfish: {exc}")
        finally:
            self.thinking_changed.emit(False)

    def _search_with_recovery(
        self,
        board: chess.Board,
        difficulty_level: int,
        wtime_ms: Optional[int],
        btime_ms: Optional[int],
        winc_ms: int,
        binc_ms: int,
        multipv: int,
    ) -> Optional[chess.Move]:
        try:
            return self._manager.choose_move(
                board=board,
                difficulty_level=difficulty_level,
                wtime_ms=wtime_ms,
                btime_ms=btime_ms,
                winc_ms=winc_ms,
                binc_ms=binc_ms,
                multipv=multipv,
            )
        except chess.engine.EngineTerminatedError:
            logger.warning("Engine terminated unexpectedly; attempting auto-restart.")
            self._manager.restart()
            return self._manager.choose_move(
                board=board,
                difficulty_level=difficulty_level,
                wtime_ms=wtime_ms,
                btime_ms=btime_ms,
                winc_ms=winc_ms,
                binc_ms=binc_ms,
                multipv=multipv,
            )

    @Slot()
    def shutdown(self) -> None:
        self._manager.stop()


class EngineService(QObject):
    """UI-facing controller owning the EngineManager and its QThread."""

    move_ready = Signal(str, int)
    engine_error = Signal(str)
    thinking_changed = Signal(bool)
    _search_requested = Signal(str, int, object, object, int, int, int, int)
    _shutdown_requested = Signal()

    def __init__(self, manager: EngineManager, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._manager = manager
        self._thread = QThread(self)
        self._worker = _EngineWorker(manager)
        self._worker.moveToThread(self._thread)

        self._search_requested.connect(self._worker.run_search)
        self._shutdown_requested.connect(self._worker.shutdown)
        self._worker.move_ready.connect(self.move_ready)
        self._worker.engine_error.connect(self.engine_error)
        self._worker.thinking_changed.connect(self.thinking_changed)

        self._thread.start()

    @property
    def manager(self) -> EngineManager:
        return self._manager

    def request_move(
        self,
        fen: str,
        difficulty_level: int,
        request_id: int,
        wtime_ms: Optional[int] = None,
        btime_ms: Optional[int] = None,
        winc_ms: int = 0,
        binc_ms: int = 0,
        multipv: int = 1,
    ) -> None:
        """Queues a non-blocking AI move search on the worker thread."""
        self._search_requested.emit(
            fen,
            difficulty_level,
            wtime_ms,
            btime_ms,
            winc_ms,
            binc_ms,
            multipv,
            request_id,
        )

    def cancel_search(self) -> None:
        """Cancels any ongoing engine search immediately."""
        self._manager.cancel_search()

    def shutdown(self) -> None:
        """Stops any active search, quits the engine, and joins the worker thread."""
        self._manager.cancel_search()
        if self._thread.isRunning():
            self._shutdown_requested.emit()
            self._thread.quit()
            self._thread.wait(2000)
        self._manager.stop()
