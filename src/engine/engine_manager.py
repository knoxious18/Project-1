"""UI-independent UCI engine manager wrapping python-chess SimpleEngine."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Protocol

import chess
import chess.engine

logger = logging.getLogger(__name__)


def resource_path(relative_path: str) -> Path:
    """Resolves a path relative to the PyInstaller bundle or project root."""
    candidate = Path(relative_path)
    if candidate.is_absolute():
        return candidate
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return base / candidate


def default_thread_count() -> int:
    """Returns a safe default CPU thread count for Stockfish."""
    cpus = os.cpu_count() or 2
    return max(1, min(4, cpus // 2))


@dataclass(frozen=True)
class DifficultyPreset:
    """Configuration for one of the 8 AI difficulty levels."""

    level: int
    name_vi: str
    skill_level: int
    elo_ratio: float
    limit_strength: bool
    movetime_ms: int
    depth: Optional[int]


DIFFICULTY_PRESETS: dict[int, DifficultyPreset] = {
    1: DifficultyPreset(1, "Mức 1 — Mới tập", skill_level=0, elo_ratio=0.00, limit_strength=True, movetime_ms=150, depth=2),
    2: DifficultyPreset(2, "Mức 2 — Cơ bản", skill_level=3, elo_ratio=0.14, limit_strength=True, movetime_ms=200, depth=4),
    3: DifficultyPreset(3, "Mức 3 — Nghiệp dư", skill_level=6, elo_ratio=0.28, limit_strength=True, movetime_ms=300, depth=6),
    4: DifficultyPreset(4, "Mức 4 — Trung bình", skill_level=9, elo_ratio=0.45, limit_strength=True, movetime_ms=450, depth=8),
    5: DifficultyPreset(5, "Mức 5 — Khá", skill_level=12, elo_ratio=0.62, limit_strength=True, movetime_ms=650, depth=10),
    6: DifficultyPreset(6, "Mức 6 — Mạnh", skill_level=15, elo_ratio=0.80, limit_strength=True, movetime_ms=900, depth=13),
    7: DifficultyPreset(7, "Mức 7 — Cao thủ", skill_level=18, elo_ratio=0.94, limit_strength=True, movetime_ms=1200, depth=16),
    8: DifficultyPreset(8, "Mức 8 — Tối đa", skill_level=20, elo_ratio=1.00, limit_strength=False, movetime_ms=1500, depth=None),
}


class PlayStyle(Protocol):
    """Strategy interface for selecting a move from MultiPV candidate lines."""

    name: str

    def select_move(
        self,
        board: chess.Board,
        candidates: list[dict[str, Any]],
        difficulty_level: int,
    ) -> chess.Move:
        """Picks one legal move from engine analysis info dictionaries."""


class StandardPlayStyle:
    """Default play style: always picks the top-scoring engine move."""

    name = "standard"

    def select_move(
        self,
        board: chess.Board,
        candidates: list[dict[str, Any]],
        difficulty_level: int,
    ) -> chess.Move:
        for info in candidates:
            pv = info.get("pv")
            if pv:
                return pv[0]
        raise RuntimeError("Engine không trả về nước đi hợp lệ nào.")


class EngineManager:
    """Manages lifecycle, UCI options, search, and cancellation for Stockfish."""

    def __init__(
        self,
        engine_path: str,
        threads: int = 0,
        hash_mb: int = 64,
        play_style: Optional[PlayStyle] = None,
        engine_factory: Optional[Callable[[str], Any]] = None,
    ) -> None:
        self._raw_path = engine_path
        self._threads = threads if threads > 0 else default_thread_count()
        self._hash_mb = max(16, min(1024, hash_mb))
        self._play_style: PlayStyle = play_style or StandardPlayStyle()
        self._engine_factory = engine_factory or self._default_popen_uci
        self._engine: Any = None
        self._lock = threading.Lock()
        self._active_analysis: Any = None
        self._cancelled = False

    @staticmethod
    def _default_popen_uci(resolved_path: str) -> chess.engine.SimpleEngine:
        kwargs: dict[str, Any] = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        return chess.engine.SimpleEngine.popen_uci(resolved_path, **kwargs)

    def resolved_path(self) -> Path:
        return resource_path(self._raw_path)

    def set_engine_path(self, new_path: str) -> None:
        self._raw_path = new_path

    def update_resources(self, threads: int, hash_mb: int) -> None:
        self._threads = threads if threads > 0 else default_thread_count()
        self._hash_mb = max(16, min(1024, hash_mb))
        if self.is_running():
            self._apply_resource_options()

    def is_running(self) -> bool:
        return self._engine is not None

    def start(self) -> None:
        """Starts the UCI engine process if not already running."""
        if self._engine is not None:
            return
        path = self.resolved_path()
        if not path.is_file():
            raise FileNotFoundError(f"Không tìm thấy tệp engine tại: {path}")

        logger.info("Starting UCI engine: %s", path)
        self._engine = self._engine_factory(str(path))
        self._apply_resource_options()
        logger.info("UCI engine started. Options available: %d", len(self._engine.options))

    def stop(self) -> None:
        """Cancels any running search and terminates the engine process."""
        self.cancel_search()
        if self._engine is not None:
            try:
                self._engine.quit()
            except Exception as exc:
                logger.warning("Error while quitting engine: %s", exc)
            finally:
                self._engine = None

    def restart(self) -> None:
        """Restarts the engine process cleanly."""
        logger.warning("Restarting UCI engine...")
        self.stop()
        self.start()

    def _apply_resource_options(self) -> None:
        if self._engine is None:
            return
        opts: dict[str, Any] = {}
        if "Threads" in self._engine.options:
            opt = self._engine.options["Threads"]
            max_t = opt.max if opt.max is not None else 64
            min_t = opt.min if opt.min is not None else 1
            opts["Threads"] = max(min_t, min(max_t, self._threads))
        if "Hash" in self._engine.options:
            opt = self._engine.options["Hash"]
            max_h = opt.max if opt.max is not None else 2048
            min_h = opt.min if opt.min is not None else 1
            opts["Hash"] = max(min_h, min(max_h, self._hash_mb))
        if opts:
            self._engine.configure(opts)
            logger.debug("Configured engine resources: %s", opts)

    def get_elo_bounds(self) -> tuple[int, int]:
        """Reads UCI_Elo min and max dynamically from engine.options."""
        if self._engine is not None and "UCI_Elo" in self._engine.options:
            opt = self._engine.options["UCI_Elo"]
            elo_min = int(opt.min) if opt.min is not None else 1320
            elo_max = int(opt.max) if opt.max is not None else 3190
            return elo_min, elo_max
        return 1320, 3190

    def map_difficulty_to_options(self, level: int) -> tuple[DifficultyPreset, dict[str, Any]]:
        """Maps difficulty level 1..8 into UCI options using live engine bounds."""
        clamped = max(1, min(8, level))
        preset = DIFFICULTY_PRESETS[clamped]
        elo_min, elo_max = self.get_elo_bounds()
        target_elo = round(elo_min + (elo_max - elo_min) * preset.elo_ratio)
        target_elo = max(elo_min, min(elo_max, target_elo))

        uci_opts: dict[str, Any] = {}
        if self._engine is None or "Skill Level" in self._engine.options:
            uci_opts["Skill Level"] = preset.skill_level
        if self._engine is None or "UCI_LimitStrength" in self._engine.options:
            uci_opts["UCI_LimitStrength"] = preset.limit_strength
        if preset.limit_strength and (self._engine is None or "UCI_Elo" in self._engine.options):
            uci_opts["UCI_Elo"] = target_elo
        return preset, uci_opts

    def cancel_search(self) -> None:
        """Signals any active engine search to stop immediately."""
        self._cancelled = True
        with self._lock:
            analysis = self._active_analysis
        if analysis is not None:
            try:
                analysis.stop()
            except Exception as exc:
                logger.debug("Ignored stop error during cancellation: %s", exc)

    def choose_move(
        self,
        board: chess.Board,
        difficulty_level: int = 4,
        wtime_ms: Optional[int] = None,
        btime_ms: Optional[int] = None,
        winc_ms: int = 0,
        binc_ms: int = 0,
        multipv: int = 1,
    ) -> Optional[chess.Move]:
        """Runs a cancellable UCI search and returns the chosen move (or None if cancelled)."""
        if self._engine is None:
            self.start()

        self._cancelled = False
        preset, uci_opts = self.map_difficulty_to_options(difficulty_level)
        if uci_opts:
            self._engine.configure(uci_opts)

        if wtime_ms is not None and btime_ms is not None:
            # Cap remaining time slightly below actual clock to avoid flagging
            safe_w = max(50, wtime_ms - 50) / 1000.0
            safe_b = max(50, btime_ms - 50) / 1000.0
            limit = chess.engine.Limit(
                white_clock=safe_w,
                black_clock=safe_b,
                white_inc=winc_ms / 1000.0,
                black_inc=binc_ms / 1000.0,
                depth=preset.depth,
            )
        else:
            limit = chess.engine.Limit(
                time=preset.movetime_ms / 1000.0,
                depth=preset.depth,
            )

        logger.debug("Searching move: level=%d multipv=%d limit=%s", difficulty_level, multipv, limit)
        analysis = self._engine.analysis(board, limit, multipv=multipv)
        with self._lock:
            self._active_analysis = analysis

        try:
            analysis.wait()
        finally:
            with self._lock:
                self._active_analysis = None

        if self._cancelled:
            logger.debug("Search result discarded due to cancellation.")
            return None

        raw_info = analysis.info
        candidates = raw_info if isinstance(raw_info, list) else [raw_info]
        return self._play_style.select_move(board, candidates, difficulty_level)
