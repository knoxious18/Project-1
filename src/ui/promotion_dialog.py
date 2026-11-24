"""Dialog for choosing a pawn promotion piece."""

from __future__ import annotations

import chess
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class PromotionDialog(QDialog):
    """Modal dialog letting the user pick Queen, Rook, Bishop, or Knight."""

    def __init__(self, is_white: bool, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Phong cấp tốt")
        self.setModal(True)
        self.selected_piece: int = chess.QUEEN

        layout = QVBoxLayout(self)
        label = QLabel("Chọn quân muốn phong cấp:")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        btn_row = QHBoxLayout()
        options = [
            (chess.QUEEN, "♕ Hậu" if is_white else "♛ Hậu"),
            (chess.ROOK, "♖ Xe" if is_white else "♜ Xe"),
            (chess.BISHOP, "♗ Tượng" if is_white else "♝ Tượng"),
            (chess.KNIGHT, "♘ Mã" if is_white else "♞ Mã"),
        ]
        for piece_type, text in options:
            btn = QPushButton(text)
            btn.setMinimumSize(90, 48)
            btn.setStyleSheet("font-size: 15px; font-weight: 600; padding: 6px 10px;")
            btn.clicked.connect(lambda _checked=False, pt=piece_type: self._choose(pt))
            btn_row.addWidget(btn)

        layout.addLayout(btn_row)

    def _choose(self, piece_type: int) -> None:
        self.selected_piece = piece_type
        self.accept()
