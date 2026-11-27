"""Board themes, piece styles, and animation speed presets."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor


@dataclass(frozen=True)
class BoardTheme:
    """Color palette for an 8x8 chess board."""

    id: str
    name: str
    light_square: QColor
    dark_square: QColor
    selected_color: QColor
    last_move_color: QColor


BOARD_THEMES: dict[str, BoardTheme] = {
    "classic_green": BoardTheme(
        id="classic_green",
        name="Cổ điển (Xanh lá)",
        light_square=QColor("#EEEED2"),
        dark_square=QColor("#769656"),
        selected_color=QColor(246, 246, 105, 190),
        last_move_color=QColor(246, 246, 105, 120),
    ),
    "warm_wood": BoardTheme(
        id="warm_wood",
        name="Gỗ ấm (Wood)",
        light_square=QColor("#F0D9B5"),
        dark_square=QColor("#B58863"),
        selected_color=QColor(255, 224, 102, 185),
        last_move_color=QColor(205, 210, 106, 140),
    ),
    "ocean_blue": BoardTheme(
        id="ocean_blue",
        name="Đại dương (Xanh dương)",
        light_square=QColor("#DEE3E6"),
        dark_square=QColor("#8CA2AD"),
        selected_color=QColor(125, 211, 252, 185),
        last_move_color=QColor(147, 197, 253, 130),
    ),
    "dark_slate": BoardTheme(
        id="dark_slate",
        name="Tối hiện đại (Dark Slate)",
        light_square=QColor("#7A828C"),
        dark_square=QColor("#4A5058"),
        selected_color=QColor(250, 204, 21, 165),
        last_move_color=QColor(250, 204, 21, 95),
    ),
}

UI_MODES: dict[str, str] = {
    "light": "Sáng (Light Mode)",
    "dark": "Tối (Dark Mode)",
}

PIECE_STYLES: dict[str, str] = {
    "classic": "Cổ điển (Trắng - Đen)",
    "minimal": "Tối giản (Hình học phẳng)",
    "neo_warm": "Ấm áp (Vàng kem - Đỏ đô)",
}

ANIMATION_SPEEDS: dict[str, tuple[str, int]] = {
    "none": ("Tắt (Tức thì)", 0),
    "fast": ("Nhanh (120 ms)", 120),
    "medium": ("Trung bình (220 ms)", 220),
    "slow": ("Chậm (380 ms)", 380),
}


def build_piece_svg(symbol: str, style_id: str = "classic") -> bytes:
    """Returns scalable SVG bytes for a FEN piece symbol in the requested style."""
    is_white = symbol.isupper()
    kind = symbol.lower()

    if style_id == "minimal":
        fill = "#F8FAFC" if is_white else "#1E293B"
        stroke = "#334155" if is_white else "#0F172A"
        accent = "#64748B" if is_white else "#94A3B8"
        body = _minimal_piece_body(kind, fill, stroke, accent)
    else:
        if style_id == "neo_warm":
            fill = "#FFF3C4" if is_white else "#7F1D1D"
            stroke = "#7C2D12" if is_white else "#2A0A0A"
            detail = "#7C2D12" if is_white else "#FDE68A"
        else:  # classic
            fill = "#FFFFFF" if is_white else "#1E242B"
            stroke = "#1E242B" if is_white else "#0B0E11"
            detail = "#1E242B" if is_white else "#E2E8F0"
        body = _classic_piece_body(kind, fill, stroke, detail)

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">'
        f"{body}"
        "</svg>"
    )
    return svg.encode("utf-8")


def _classic_piece_body(kind: str, fill: str, stroke: str, detail: str) -> str:
    if kind == "p":
        return (
            f'<circle cx="22.5" cy="14" r="5.5" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            f'<path d="M15 35 C15 26 18 22 22.5 22 C27 22 30 26 30 35 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<rect x="12" y="35" width="21" height="4" rx="1.5" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
    if kind == "r":
        return (
            f'<path d="M12 11 H16 V15 H20 V11 H25 V15 H29 V11 H33 V19 L30 22 V33 L33 36 H12 L15 33 V22 L12 19 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<rect x="11" y="36" width="23" height="3.5" rx="1" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            f'<line x1="15" y1="22" x2="30" y2="22" stroke="{detail}" stroke-width="1.5"/>'
        )
    if kind == "n":
        return (
            f'<path d="M14 36 L16 25 C14 23 12 20 14 16 C16 12 21 10 26 10 L29 7 L30 12 '
            f'C33 14 34 19 32 24 C30 28 28 31 30 36 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="20.5" cy="16" r="1.4" fill="{detail}"/>'
            f'<rect x="11.5" y="36" width="22" height="3.5" rx="1" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
    if kind == "b":
        return (
            f'<circle cx="22.5" cy="9" r="2.5" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>'
            f'<path d="M22.5 12 C16 17 15 24 17 31 L14 35 H31 L28 31 C30 24 29 17 22.5 12 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<line x1="19" y1="20" x2="26" y2="27" stroke="{detail}" stroke-width="1.8" stroke-linecap="round"/>'
            f'<line x1="26" y1="20" x2="19" y2="27" stroke="{detail}" stroke-width="1.8" stroke-linecap="round"/>'
            f'<rect x="11.5" y="35" width="22" height="4" rx="1.5" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
    if kind == "q":
        return (
            f'<circle cx="9.5" cy="14" r="2.2" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
            f'<circle cx="16" cy="10.5" r="2.2" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
            f'<circle cx="22.5" cy="9" r="2.4" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
            f'<circle cx="29" cy="10.5" r="2.2" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
            f'<circle cx="35.5" cy="14" r="2.2" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
            f'<path d="M10.5 16.5 L15 29 H30 L34.5 16.5 L28 24 L29 13 L22.5 23 L16 13 L17 24 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M14 29 L12.5 35.5 H32.5 L31 29 Z" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<rect x="11.5" y="35.5" width="22" height="3.5" rx="1" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
    return (
        f'<line x1="22.5" y1="6.5" x2="22.5" y2="14" stroke="{stroke}" stroke-width="2.4" stroke-linecap="round"/>'
        f'<line x1="18.5" y1="10" x2="26.5" y2="10" stroke="{stroke}" stroke-width="2.4" stroke-linecap="round"/>'
        f'<path d="M13 21 C11 16 17 13 22.5 17 C28 13 34 16 32 21 L29.5 32 H15.5 Z" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
        f'<line x1="16" y1="27" x2="29" y2="27" stroke="{detail}" stroke-width="1.6"/>'
        f'<rect x="12" y="32" width="21" height="3.5" rx="1" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        f'<rect x="11" y="35.5" width="23" height="3.5" rx="1" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    )


def _minimal_piece_body(kind: str, fill: str, stroke: str, accent: str) -> str:
    if kind == "p":
        return (
            f'<circle cx="22.5" cy="16" r="5" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
            f'<polygon points="15,37 30,37 25,22 20,22" fill="{fill}" stroke="{stroke}" stroke-width="1.6" stroke-linejoin="round"/>'
        )
    if kind == "r":
        return (
            f'<rect x="14" y="12" width="17" height="25" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
            f'<rect x="17" y="16" width="11" height="3" fill="{accent}"/>'
        )
    if kind == "n":
        return (
            f'<polygon points="14,37 31,37 29,12 19,10 13,20 20,22" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.6" stroke-linejoin="round"/>'
        )
    if kind == "b":
        return (
            f'<polygon points="22.5,9 31,26 27,37 18,37 14,26" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<circle cx="22.5" cy="22" r="2.3" fill="{accent}"/>'
        )
    if kind == "q":
        return (
            f'<polygon points="10,14 17,24 22.5,10 28,24 35,14 31,37 14,37" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.6" stroke-linejoin="round"/>'
        )
    return (
        f'<rect x="20.5" y="7" width="4" height="9" fill="{stroke}"/>'
        f'<rect x="18" y="9.5" width="9" height="4" fill="{stroke}"/>'
        f'<polygon points="13,18 32,18 29,37 16,37" fill="{fill}" stroke="{stroke}" stroke-width="1.6" stroke-linejoin="round"/>'
    )
