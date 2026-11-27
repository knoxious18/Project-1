"""Settings dialog for board theme, piece style, and move animation speed."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)

from src.core import AppSettings
from src.ui.themes import ANIMATION_SPEEDS, BOARD_THEMES, PIECE_STYLES, UI_MODES


class SettingsDialog(QDialog):
    """Modal settings dialog triggered by the gear button."""

    settings_applied = Signal(AppSettings)

    def __init__(self, current: AppSettings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cài đặt giao diện")
        self.setModal(True)
        self.setMinimumWidth(360)

        self._initial = AppSettings(
            ui_mode=current.ui_mode,
            board_theme=current.board_theme,
            piece_style=current.piece_style,
            animation_speed=current.animation_speed,
        )

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self._mode_combo = QComboBox()
        for mode_id, label in UI_MODES.items():
            self._mode_combo.addItem(label, mode_id)
        self._select_by_data(self._mode_combo, current.ui_mode)
        self._mode_combo.currentIndexChanged.connect(self._emit_live)
        form.addRow("Chế độ giao diện:", self._mode_combo)

        self._theme_combo = QComboBox()
        for theme_id, theme in BOARD_THEMES.items():
            self._theme_combo.addItem(theme.name, theme_id)
        self._select_by_data(self._theme_combo, current.board_theme)
        self._theme_combo.currentIndexChanged.connect(self._emit_live)
        form.addRow("Chủ đề bàn cờ:", self._theme_combo)

        self._piece_combo = QComboBox()
        for style_id, label in PIECE_STYLES.items():
            self._piece_combo.addItem(label, style_id)
        self._select_by_data(self._piece_combo, current.piece_style)
        self._piece_combo.currentIndexChanged.connect(self._emit_live)
        form.addRow("Kiểu quân cờ:", self._piece_combo)

        self._anim_combo = QComboBox()
        for speed_id, (label, _ms) in ANIMATION_SPEEDS.items():
            self._anim_combo.addItem(label, speed_id)
        self._select_by_data(self._anim_combo, current.animation_speed)
        self._anim_combo.currentIndexChanged.connect(self._emit_live)
        form.addRow("Tốc độ animation:", self._anim_combo)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self._on_cancel)
        ok_btn = QPushButton("Lưu")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

    @staticmethod
    def _select_by_data(combo: QComboBox, value: str) -> None:
        idx = combo.findData(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def current_settings(self) -> AppSettings:
        return AppSettings(
            ui_mode=self._mode_combo.currentData(),
            board_theme=self._theme_combo.currentData(),
            piece_style=self._piece_combo.currentData(),
            animation_speed=self._anim_combo.currentData(),
        )

    def _emit_live(self) -> None:
        self.settings_applied.emit(self.current_settings())

    def _on_cancel(self) -> None:
        self.settings_applied.emit(self._initial)
        self.reject()
