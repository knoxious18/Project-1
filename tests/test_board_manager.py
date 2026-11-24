"""Unit tests for BoardManager (chess rules, FEN, PGN, undo)."""

import chess
import pytest

from src.core import BoardManager


def test_initial_state() -> None:
    bm = BoardManager()
    assert bm.get_fen() == chess.STARTING_FEN
    status = bm.get_status()
    assert not status.is_game_over
    assert status.turn == "white"
    assert not status.in_check
    assert bm.get_move_history() == []


def test_legal_moves_and_history() -> None:
    bm = BoardManager()
    e2_moves = bm.get_legal_moves_from(chess.E2)
    assert {m.to_square for m in e2_moves} == {chess.E3, chess.E4}

    rec1 = bm.make_move(chess.E2, chess.E4)
    assert rec1.san == "e4"
    assert rec1.uci == "e2e4"
    assert rec1.color == "white"
    assert rec1.move_number == 1

    rec2 = bm.make_move(chess.E7, chess.E5)
    assert rec2.san == "e5"
    assert rec2.color == "black"
    assert len(bm.get_move_history()) == 2


def test_illegal_move_raises() -> None:
    bm = BoardManager()
    with pytest.raises(ValueError):
        bm.make_move(chess.E2, chess.E5)


def test_castling_and_en_passant() -> None:
    # Castling position
    bm = BoardManager("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    rec = bm.make_move(chess.E1, chess.G1)
    assert rec.san == "O-O"
    assert bm.get_piece_at(chess.F1) == chess.Piece(chess.ROOK, chess.WHITE)

    # En passant position
    bm.load_fen("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
    rec_ep = bm.make_move(chess.E5, chess.D6)
    assert rec_ep.san == "exd6"
    assert bm.get_piece_at(chess.D5) is None


def test_promotion_requires_piece_and_executes() -> None:
    bm = BoardManager("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
    assert bm.is_promotion_move(chess.A7, chess.A8)
    with pytest.raises(ValueError):
        bm.make_move(chess.A7, chess.A8)

    rec = bm.make_move(chess.A7, chess.A8, promotion=chess.QUEEN)
    assert rec.san == "a8=Q+"
    assert bm.get_piece_at(chess.A8) == chess.Piece(chess.QUEEN, chess.WHITE)


def test_checkmate_and_draw_rules() -> None:
    # Fool's mate
    bm = BoardManager()
    for uci in ("f2f3", "e7e5", "g2g4", "d8h4"):
        bm.make_uci_move(uci)
    status = bm.get_status()
    assert status.is_game_over
    assert status.result == "0-1"
    assert status.termination == "Chiếu hết"
    assert status.in_check

    # Stalemate
    bm.load_fen("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    st = bm.get_status()
    assert st.is_game_over
    assert st.result == "1/2-1/2"
    assert st.termination == "Hết nước đi (Hòa)"

    # Insufficient material (K+B vs K)
    bm.load_fen("4k3/8/8/8/8/8/4B3/4K3 w - - 0 1")
    ins = bm.get_status()
    assert ins.is_game_over
    assert ins.result == "1/2-1/2"
    assert ins.termination == "Thiếu lực lượng (Hòa)"

    # Threefold repetition
    bm.reset()
    for uci in ("g1f3", "g8f6", "f3g1", "f6g8", "g1f3", "g8f6", "f3g1", "f6g8"):
        bm.make_uci_move(uci)
    rep = bm.get_status()
    assert rep.is_game_over
    assert rep.result == "1/2-1/2"
    assert rep.termination == "Lặp lại 3 lần (Hòa)"


def test_undo_and_pgn_roundtrip() -> None:
    bm = BoardManager()
    bm.make_uci_move("e2e4")
    bm.make_uci_move("c7c5")
    bm.make_uci_move("g1f3")

    undone = bm.undo_move()
    assert undone is not None
    assert undone.san == "Nf3"
    assert len(bm.get_move_history()) == 2

    pgn = bm.export_pgn(white="Kien", black="Friend")
    bm2 = BoardManager()
    bm2.load_pgn(pgn)
    assert bm2.get_fen() == bm.get_fen()
    assert [m.san for m in bm2.get_move_history()] == ["e4", "c5"]


def test_invalid_fen_and_pgn_raise() -> None:
    bm = BoardManager()
    with pytest.raises(ValueError):
        bm.load_fen("not a valid fen")
    with pytest.raises(ValueError):
        bm.load_pgn("")
