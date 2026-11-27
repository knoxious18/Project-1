"""Setup dialog for starting a Play with AI match."""

from __future__ import annotations

import random
from dataclasses import dataclass

import chess
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.engine import DIFFICULTY_PRESETS


@dataclass(frozen=True)
class AiSetupChoice:
    """User selections from AiSetupDialog."""

    human_color: chess.Color
    difficulty_level: int


class AiSetupDialog(QDialog):
    """Modal dialog for configuring color and difficulty before playing Stockfish."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Thiết lập ván đấu với AI")
        self.setModal(True)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self._color_combo = QComboBox()
        self._color_combo.addItem("Trắng (Đi trước)", "white")
        self._color_combo.addItem("Đen (Đi sau)", "black")
        self._color_combo.addItem("Ngẫu nhiên", "random")
        form.addRow("Chọn quân:", self._color_combo)

        self._difficulty_combo = QComboBox()
        for level, preset in DIFFICULTY_PRESETS.items():
            self._difficulty_combo.addItem(preset.name_vi, level)
        self._difficulty_combo.setCurrentIndex(3)  # Default: Level 4
        form.addRow("Độ khó:", self._difficulty_combo)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        start_btn = QPushButton("Bắt đầu")
        start_btn.setDefault(True)
        start_btn.clicked.connect(self.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(start_btn)
        layout.addLayout(btn_row)

    def get_choice(self) -> AiSetupChoice:
        raw_color = self._color_combo.currentData()
        if raw_color == "white":
            color = chess.WHITE
        elif raw_color == "black":
            color = chess.BLACK
        else:
            color = random.choice([chess.WHITE, chess.BLACK])

        return AiSetupChoice(
            human_color=color,
            difficulty_level=int(self._difficulty_combo.currentData()),
        )
