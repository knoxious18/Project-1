"""Intro / home screen widget for choosing game mode."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class IntroWidget(QWidget):
    """Landing screen offering Play with Human, Play with AI, and Analysis modes."""

    play_human_clicked = Signal()
    play_ai_clicked = Signal()
    analysis_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 24, 32, 24)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        settings_btn = QPushButton("⚙ Cài đặt")
        settings_btn.setMinimumHeight(34)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.settings_clicked.emit)
        top_bar.addWidget(settings_btn)
        outer.addLayout(top_bar)

        outer.addStretch(1)

        title = QLabel("RealChess")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 40px; font-weight: 800; letter-spacing: 1px;")
        outer.addWidget(title)

        subtitle = QLabel("Chọn chế độ để bắt đầu")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 15px; color: #94A3B8; margin-bottom: 18px;")
        outer.addWidget(subtitle)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(18)
        cards_row.addStretch(1)

        modes = [
            (
                "Play with Human",
                "Chơi đối kháng 2 người trên cùng máy",
                "#769656",
                self.play_human_clicked.emit,
            ),
            (
                "Play with AI",
                "Đấu với máy Stockfish (Sắp ra mắt)",
                "#3B82F6",
                self.play_ai_clicked.emit,
            ),
            (
                "Analysis",
                "Phân tích ván đấu & đánh giá nước đi (Sắp ra mắt)",
                "#8B5CF6",
                self.analysis_clicked.emit,
            ),
        ]

        for heading, desc, accent, handler in modes:
            btn = QPushButton(f"{heading}\n\n{desc}")
            btn.setFixedSize(230, 150)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background-color: #1E242B;"
                f"  color: #F8FAFC;"
                f"  border: 2px solid {accent};"
                f"  border-radius: 12px;"
                f"  font-size: 15px;"
                f"  font-weight: 700;"
                f"  padding: 14px;"
                f"}}"
                f"QPushButton:hover {{"
                f"  background-color: {accent};"
                f"  color: #FFFFFF;"
                f"}}"
            )
            btn.clicked.connect(handler)
            cards_row.addWidget(btn)

        cards_row.addStretch(1)
        outer.addLayout(cards_row)
        outer.addStretch(2)
