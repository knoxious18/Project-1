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
        settings_btn = QPushButton("⚙")
        settings_btn.setToolTip("Cài đặt giao diện")
        settings_btn.setFixedSize(36, 36)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setStyleSheet(
            "QPushButton { background-color: #FFFFFF; color: #111827; "
            "border: 1px solid #D1D5DB; border-radius: 0px; font-size: 16px; }"
            "QPushButton:hover { background-color: #F3F4F6; border-color: #111827; }"
        )
        settings_btn.clicked.connect(self.settings_clicked.emit)
        top_bar.addWidget(settings_btn)
        outer.addLayout(top_bar)

        outer.addStretch(1)

        title = QLabel("RealChess")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: 800; margin-bottom: 18px;")
        outer.addWidget(title)

        buttons_col = QVBoxLayout()
        buttons_col.setSpacing(12)
        buttons_col.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        modes = [
            ("Play with\nHuman", self.play_human_clicked.emit),
            ("Play with\nAI", self.play_ai_clicked.emit),
            ("Analysis", self.analysis_clicked.emit),
        ]

        button_style = (
            "QPushButton {"
            "  background-color: #FFFFFF;"
            "  color: #111827;"
            "  border: 1px solid #D1D5DB;"
            "  border-radius: 0px;"
            "  font-size: 15px;"
            "  font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "  background-color: #F3F4F6;"
            "  border: 1px solid #111827;"
            "}"
        )

        for label, handler in modes:
            btn = QPushButton(label)
            btn.setFixedSize(136, 136)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(button_style)
            btn.clicked.connect(handler)
            buttons_col.addWidget(btn)

        outer.addLayout(buttons_col)
        outer.addStretch(2)
