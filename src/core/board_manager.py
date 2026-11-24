"""UI-independent chess game state, rules, and FEN/PGN manager."""

from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Optional

import chess
import chess.pgn


@dataclass(frozen=True)
class MoveRecord:
    """Represents a single half-move (ply) in the game history."""

    ply: int
    move_number: int
    color: str
    uci: str
    san: str
    fen_after: str


@dataclass(frozen=True)
class GameStatus:
    """Snapshot of the current game state and outcome."""

    is_game_over: bool
    result: str
    termination: str
    outcome_text: str
    turn: str
    in_check: bool
    check_square: Optional[int]


_TERMINATION_LABELS = {
    chess.Termination.CHECKMATE: "Chiếu hết",
    chess.Termination.STALEMATE: "Hết nước đi (Hòa)",
    chess.Termination.INSUFFICIENT_MATERIAL: "Thiếu lực lượng (Hòa)",
    chess.Termination.SEVENTYFIVE_MOVES: "Luật 75 nước (Hòa)",
    chess.Termination.FIVEFOLD_REPETITION: "Lặp lại 5 lần (Hòa)",
    chess.Termination.FIFTY_MOVES: "Luật 50 nước (Hòa)",
    chess.Termination.THREEFOLD_REPETITION: "Lặp lại 3 lần (Hòa)",
}


class BoardManager:
    """Manages chess rules, move history, and FEN/PGN import & export."""

    def __init__(self, fen: Optional[str] = None) -> None:
        self._board = chess.Board()
        self._initial_fen = chess.STARTING_FEN
        self._history: list[MoveRecord] = []
        if fen is not None:
            self.load_fen(fen)

    @property
    def board(self) -> chess.Board:
        """Returns the underlying python-chess Board (read-only usage recommended)."""
        return self._board

    def reset(self, fen: Optional[str] = None) -> None:
        """Resets the board to the starting position or a custom FEN."""
        if fen is None:
            self._board = chess.Board()
            self._initial_fen = chess.STARTING_FEN
            self._history.clear()
        else:
            self.load_fen(fen)

    def get_fen(self) -> str:
        """Returns the current board position as a FEN string."""
        return self._board.fen()

    def load_fen(self, fen: str) -> None:
        """Loads a board position from a FEN string and clears move history."""
        cleaned = fen.strip()
        if not cleaned:
            raise ValueError("Chuỗi FEN không được để trống.")
        try:
            new_board = chess.Board(cleaned)
        except ValueError as exc:
            raise ValueError(f"FEN không hợp lệ: {exc}") from exc

        self._board = new_board
        self._initial_fen = new_board.fen()
        self._history.clear()

    def export_pgn(
        self,
        white: str = "White",
        black: str = "Black",
        event: str = "RealChess Local Game",
    ) -> str:
        """Exports the current game (including custom starting FEN if any) as PGN."""
        game = chess.pgn.Game()
        game.headers["Event"] = event
        game.headers["Site"] = "Local"
        game.headers["White"] = white
        game.headers["Black"] = black

        status = self.get_status()
        game.headers["Result"] = status.result

        if self._initial_fen != chess.STARTING_FEN:
            game.setup(chess.Board(self._initial_fen))

        node: chess.pgn.GameNode = game
        for move in self._board.move_stack:
            node = node.add_variation(move)

        exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
        return game.accept(exporter)

    def load_pgn(self, pgn_text: str) -> None:
        """Loads a game from PGN text and replays its mainline moves."""
        cleaned = pgn_text.strip()
        if not cleaned:
            raise ValueError("Nội dung PGN không được để trống.")

        game = chess.pgn.read_game(io.StringIO(cleaned))
        if game is None:
            raise ValueError("Không thể đọc dữ liệu PGN.")
        if game.errors:
            raise ValueError(f"PGN có lỗi: {game.errors[0]}")

        start_board = game.board()
        self._board = start_board
        self._initial_fen = start_board.fen()
        self._history.clear()

        for move in game.mainline_moves():
            self._push_move(move)

    def get_legal_moves_from(self, square: int) -> list[chess.Move]:
        """Returns all legal moves originating from the given square."""
        if self.get_status().is_game_over:
            return []
        return [m for m in self._board.legal_moves if m.from_square == square]

    def is_promotion_move(self, from_square: int, to_square: int) -> bool:
        """Checks whether moving from_square -> to_square requires a pawn promotion."""
        if self.get_status().is_game_over:
            return False
        return any(
            m.from_square == from_square
            and m.to_square == to_square
            and m.promotion is not None
            for m in self._board.legal_moves
        )

    def make_move(
        self,
        from_square: int,
        to_square: int,
        promotion: Optional[int] = None,
    ) -> MoveRecord:
        """Validates and executes a move on the board."""
        if self.get_status().is_game_over:
            raise ValueError("Ván đấu đã kết thúc.")

        if promotion is None and self.is_promotion_move(from_square, to_square):
            raise ValueError("Nước phong cấp cần chọn quân (Hậu, Xe, Tượng, Mã).")

        move = chess.Move(from_square, to_square, promotion=promotion)
        if move not in self._board.legal_moves:
            raise ValueError(f"Nước đi không hợp lệ: {move.uci()}")

        return self._push_move(move)

    def make_uci_move(self, uci: str) -> MoveRecord:
        """Validates and executes a move given in UCI notation (e.g. 'e2e4', 'e7e8q')."""
        if self.get_status().is_game_over:
            raise ValueError("Ván đấu đã kết thúc.")
        try:
            move = chess.Move.from_uci(uci.strip())
        except ValueError as exc:
            raise ValueError(f"Ký hiệu UCI không hợp lệ: {uci}") from exc

        if move not in self._board.legal_moves:
            raise ValueError(f"Nước đi không hợp lệ: {uci}")

        return self._push_move(move)

    def _push_move(self, move: chess.Move) -> MoveRecord:
        """Internal helper to record SAN and push a validated move."""
        color = "white" if self._board.turn == chess.WHITE else "black"
        move_number = self._board.fullmove_number
        san = self._board.san(move)
        self._board.push(move)

        record = MoveRecord(
            ply=len(self._history) + 1,
            move_number=move_number,
            color=color,
            uci=move.uci(),
            san=san,
            fen_after=self._board.fen(),
        )
        self._history.append(record)
        return record

    def undo_move(self) -> Optional[MoveRecord]:
        """Undoes the last move and returns its MoveRecord, or None if at start."""
        if not self._board.move_stack:
            return None
        self._board.pop()
        return self._history.pop()

    def get_piece_at(self, square: int) -> Optional[chess.Piece]:
        """Returns the piece on the given square, or None if empty."""
        return self._board.piece_at(square)

    def get_board_map(self) -> dict[int, chess.Piece]:
        """Returns a mapping of occupied squares to Piece objects."""
        return self._board.piece_map()

    def get_move_history(self) -> list[MoveRecord]:
        """Returns a copy of the move history."""
        return list(self._history)

    def get_last_move(self) -> Optional[chess.Move]:
        """Returns the most recently played Move, or None."""
        if not self._board.move_stack:
            return None
        return self._board.peek()

    def get_status(self) -> GameStatus:
        """Computes the current game status, including 3-fold repetition and 50-move rule."""
        turn = "white" if self._board.turn == chess.WHITE else "black"
        in_check = self._board.is_check()
        check_square = self._board.king(self._board.turn) if in_check else None

        outcome = self._board.outcome(claim_draw=False)
        if outcome is not None:
            term_label = _TERMINATION_LABELS.get(outcome.termination, "Kết thúc")
            if outcome.winner is chess.WHITE:
                winner_text = "Trắng thắng"
            elif outcome.winner is chess.BLACK:
                winner_text = "Đen thắng"
            else:
                winner_text = "Hòa"

            return GameStatus(
                is_game_over=True,
                result=outcome.result(),
                termination=term_label,
                outcome_text=f"{winner_text} — {term_label} ({outcome.result()})",
                turn=turn,
                in_check=in_check,
                check_square=check_square,
            )

        if self._board.is_repetition(3):
            term_label = _TERMINATION_LABELS[chess.Termination.THREEFOLD_REPETITION]
            return GameStatus(
                is_game_over=True,
                result="1/2-1/2",
                termination=term_label,
                outcome_text=f"Hòa — {term_label} (1/2-1/2)",
                turn=turn,
                in_check=in_check,
                check_square=check_square,
            )

        if self._board.is_fifty_moves():
            term_label = _TERMINATION_LABELS[chess.Termination.FIFTY_MOVES]
            return GameStatus(
                is_game_over=True,
                result="1/2-1/2",
                termination=term_label,
                outcome_text=f"Hòa — {term_label} (1/2-1/2)",
                turn=turn,
                in_check=in_check,
                check_square=check_square,
            )

        turn_vi = "Trắng" if turn == "white" else "Đen"
        check_suffix = " (Đang bị chiếu!)" if in_check else ""
        return GameStatus(
            is_game_over=False,
            result="*",
            termination="Đang diễn ra",
            outcome_text=f"Lượt {turn_vi}{check_suffix}",
            turn=turn,
            in_check=in_check,
            check_square=check_square,
        )
