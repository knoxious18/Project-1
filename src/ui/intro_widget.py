"""Intro / home screen widget for choosing game mode (Light Theme)."""

from __future__ import annotations

from PySide6.QtCore import QByteArray, QEvent, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QKeyEvent, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------------------------
# Theme Constants (Chỉnh nhanh màu sắc, kích thước thẻ, độ bo góc tại đây)
# ---------------------------------------------------------------------------
BG_COLOR = "#F7F8FA"
CARD_BG = "#FFFFFF"
CARD_PRESSED_BG = "#F1F3F5"
BORDER_COLOR = "#E5E7EB"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
ACCENT_COLOR = "#5B8C3A"
ACCENT_HOVER_COLOR = "#4C7A2E"

CARD_WIDTH = 200
CARD_HEIGHT = 220
CARD_RADIUS = 14
SMALL_BTN_RADIUS = 10

INTRO_QSS = f"""
#IntroWidget {{
    background-color: {BG_COLOR};
    font-family: "Segoe UI", "Inter", sans-serif;
}}

#AppTitle {{
    color: {TEXT_PRIMARY};
    font-size: 40px;
    font-weight: 700;
    letter-spacing: -0.5px;
    background: transparent;
}}

#AppSubtitle {{
    color: {TEXT_SECONDARY};
    font-size: 14px;
    font-weight: 400;
    background: transparent;
}}

#SettingsButton {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: 20px;
}}
#SettingsButton:hover {{
    border: 1.5px solid {ACCENT_COLOR};
    background-color: {CARD_BG};
}}
#SettingsButton:pressed {{
    background-color: {CARD_PRESSED_BG};
}}
#SettingsButton:focus {{
    border: 2px solid {ACCENT_COLOR};
    outline: none;
}}

#ModeCard {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER_COLOR};
    border-radius: {CARD_RADIUS}px;
    text-align: center;
}}
#ModeCard:hover {{
    border: 1.5px solid {ACCENT_COLOR};
}}
#ModeCard:pressed {{
    background-color: {CARD_PRESSED_BG};
    border: 1.5px solid {ACCENT_HOVER_COLOR};
}}
#ModeCard:focus {{
    border: 2px solid {ACCENT_COLOR};
    outline: none;
}}

#CardTitle {{
    color: {TEXT_PRIMARY};
    font-size: 16px;
    font-weight: 700;
    background: transparent;
}}

#CardDesc {{
    color: {TEXT_SECONDARY};
    font-size: 12.5px;
    font-weight: 400;
    background: transparent;
}}
"""


def _svg_to_pixmap(svg_markup: str, size: int) -> QPixmap:
    """Renders inline SVG markup into a high-DPI friendly QPixmap."""
    renderer = QSvgRenderer(QByteArray(svg_markup.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def _gear_icon_svg(color: str = TEXT_PRIMARY) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f'<circle cx="12" cy="12" r="3"/>'
        f'<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06'
        f'a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09'
        f'A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83'
        f'l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09'
        f'A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83'
        f'l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09'
        f'a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83'
        f'l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09'
        f'a1.65 1.65 0 0 0-1.51 1z"/>'
        f"</svg>"
    )


def _human_icon_svg(color: str = ACCENT_COLOR) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="none" '
        f'stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<circle cx="18" cy="16" r="6"/>'
        f'<path d="M7 38c0-6.1 4.9-11 11-11s11 4.9 11 11"/>'
        f'<circle cx="33" cy="18" r="4.5"/>'
        f'<path d="M33 27c4.8 0 8.5 3.6 8.5 8.5"/>'
        f"</svg>"
    )


def _ai_icon_svg(color: str = ACCENT_COLOR) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="none" '
        f'stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<rect x="13" y="13" width="22" height="22" rx="4"/>'
        f'<rect x="19" y="19" width="10" height="10" rx="1.5"/>'
        f'<line x1="19" y1="7" x2="19" y2="13"/>'
        f'<line x1="29" y1="7" x2="29" y2="13"/>'
        f'<line x1="19" y1="35" x2="19" y2="41"/>'
        f'<line x1="29" y1="35" x2="29" y2="41"/>'
        f'<line x1="7" y1="19" x2="13" y2="19"/>'
        f'<line x1="7" y1="29" x2="13" y2="29"/>'
        f'<line x1="35" y1="19" x2="41" y2="19"/>'
        f'<line x1="35" y1="29" x2="41" y2="29"/>'
        f"</svg>"
    )


def _analysis_icon_svg(color: str = ACCENT_COLOR) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="none" '
        f'stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M8 38h32"/>'
        f'<rect x="12" y="25" width="5" height="13" rx="1"/>'
        f'<rect x="21.5" y="18" width="5" height="20" rx="1"/>'
        f'<rect x="31" y="11" width="5" height="27" rx="1"/>'
        f'<path d="M12 18l9-6 6 4 9-8"/>'
        f"</svg>"
    )


class ModeCard(QPushButton):
    """Reusable interactive card button for selecting a game mode."""

    def __init__(
        self,
        icon_svg: str,
        title: str,
        description: str,
        tooltip: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("ModeCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setToolTip(tooltip)
        self.setMinimumSize(180, CARD_HEIGHT)
        self.setMaximumSize(240, 250)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.resize(CARD_WIDTH, CARD_HEIGHT)

        # Subtle drop shadow; intensifies on hover
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(24)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QColor(17, 24, 39, 18))
        self.setGraphicsEffect(self._shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 20)
        layout.setSpacing(8)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setPixmap(_svg_to_pixmap(icon_svg, 48))
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(icon_label)

        layout.addSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setObjectName("CardDesc")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(desc_label)

        layout.addStretch()

    def enterEvent(self, event: QEvent) -> None:
        self._shadow.setColor(QColor(17, 24, 39, 36))
        self._shadow.setOffset(0, 6)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._shadow.setColor(QColor(17, 24, 39, 18))
        self._shadow.setOffset(0, 4)
        super().leaveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.click()
            return
        super().keyPressEvent(event)


class IntroWidget(QWidget):
    """Minimalist light-theme landing screen for RealChess."""

    play_human_clicked = Signal()
    play_ai_clicked = Signal()
    analysis_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("IntroWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(INTRO_QSS)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 24, 32, 32)
        outer.setSpacing(0)

        # Top-right circular settings button
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        settings_btn = QPushButton()
        settings_btn.setObjectName("SettingsButton")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        settings_btn.setToolTip("Cài đặt giao diện và animation")
        settings_btn.setIcon(QIcon(_svg_to_pixmap(_gear_icon_svg(), 20)))
        settings_btn.setIconSize(QSize(20, 20))
        settings_btn.clicked.connect(self.settings_clicked.emit)
        top_bar.addWidget(settings_btn)
        outer.addLayout(top_bar)

        outer.addStretch(2)

        # Center header
        title = QLabel("RealChess")
        title.setObjectName("AppTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(title)

        outer.addSpacing(8)

        subtitle = QLabel("Chơi, luyện tập và phân tích ván cờ của bạn")
        subtitle.setObjectName("AppSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(subtitle)

        outer.addSpacing(32)

        # Horizontal mode cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        cards_row.addStretch(1)

        human_card = ModeCard(
            icon_svg=_human_icon_svg(),
            title="Play with Human",
            description="Đấu 2 người trực tiếp trên cùng một máy",
            tooltip="Mở bàn cờ đấu đối kháng 2 người",
        )
        human_card.clicked.connect(self.play_human_clicked.emit)

        ai_card = ModeCard(
            icon_svg=_ai_icon_svg(),
            title="Play with AI",
            description="Thử sức với engine Stockfish (sắp ra mắt)",
            tooltip="Chế độ đấu với máy Stockfish",
        )
        ai_card.clicked.connect(self.play_ai_clicked.emit)

        analysis_card = ModeCard(
            icon_svg=_analysis_icon_svg(),
            title="Analysis",
            description="Đánh giá nước đi và biểu đồ thế cờ",
            tooltip="Chế độ phân tích ván đấu",
        )
        analysis_card.clicked.connect(self.analysis_clicked.emit)

        for card in (human_card, ai_card, analysis_card):
            cards_row.addWidget(card)

        cards_row.addStretch(1)
        outer.addLayout(cards_row)
        outer.addStretch(3)
