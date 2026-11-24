"""Interactive 8x8 chess board widget rendered with PySide6 & SVG pieces."""

from __future__ import annotations

import math
from typing import Optional

import chess
from PySide6.QtCore import QByteArray, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPen, QPolygonF
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QSizePolicy, QWidget

from src.core import BoardManager
from src.ui.promotion_dialog import PromotionDialog


def _build_piece_svg(symbol: str) -> bytes:
    """Returns clean, scalable SVG bytes for a given FEN piece symbol (e.g. 'K', 'p')."""
    is_white = symbol.isupper()
    fill = "#FFFFFF" if is_white else "#1E242B"
    stroke = "#1E242B" if is_white else "#0B0E11"
    detail = "#1E242B" if is_white else "#E2E8F0"
    kind = symbol.lower()

    if kind == "p":
        body = (
            f'<circle cx="22.5" cy="14" r="5.5" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            f'<path d="M15 35 C15 26 18 22 22.5 22 C27 22 30 26 30 35 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<rect x="12" y="35" width="21" height="4" rx="1.5" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
    elif kind == "r":
        body = (
            f'<path d="M12 11 H16 V15 H20 V11 H25 V15 H29 V11 H33 V19 L30 22 V33 L33 36 H12 L15 33 V22 L12 19 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<rect x="11" y="36" width="23" height="3.5" rx="1" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            f'<line x1="15" y1="22" x2="30" y2="22" stroke="{detail}" stroke-width="1.5"/>'
        )
    elif kind == "n":
        body = (
            f'<path d="M14 36 L16 25 C14 23 12 20 14 16 C16 12 21 10 26 10 L29 7 L30 12 '
            f'C33 14 34 19 32 24 C30 28 28 31 30 36 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="20.5" cy="16" r="1.4" fill="{detail}"/>'
            f'<rect x="11.5" y="36" width="22" height="3.5" rx="1" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
    elif kind == "b":
        body = (
            f'<circle cx="22.5" cy="9" r="2.5" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>'
            f'<path d="M22.5 12 C16 17 15 24 17 31 L14 35 H31 L28 31 C30 24 29 17 22.5 12 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<line x1="19" y1="20" x2="26" y2="27" stroke="{detail}" stroke-width="1.8" stroke-linecap="round"/>'
            f'<line x1="26" y1="20" x2="19" y2="27" stroke="{detail}" stroke-width="1.8" stroke-linecap="round"/>'
            f'<rect x="11.5" y="35" width="22" height="4" rx="1.5" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
    elif kind == "q":
        body = (
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
    else:  # 'k'
        body = (
            f'<line x1="22.5" y1="6.5" x2="22.5" y2="14" stroke="{stroke}" stroke-width="2.4" stroke-linecap="round"/>'
            f'<line x1="18.5" y1="10" x2="26.5" y2="10" stroke="{stroke}" stroke-width="2.4" stroke-linecap="round"/>'
            f'<path d="M13 21 C11 16 17 13 22.5 17 C28 13 34 16 32 21 L29.5 32 H15.5 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-linejoin="round"/>'
            f'<line x1="16" y1="27" x2="29" y2="27" stroke="{detail}" stroke-width="1.6"/>'
            f'<rect x="12" y="32" width="21" height="3.5" rx="1" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            f'<rect x="11" y="35.5" width="23" height="3.5" rx="1" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45">'
        f"{body}"
        "</svg>"
    )
    return svg.encode("utf-8")


class BoardWidget(QWidget):
    """Interactive 8x8 chess board supporting click-to-move and drag-and-drop."""

    board_changed = Signal()
    status_message = Signal(str)

    LIGHT_SQUARE = QColor("#EEEED2")
    DARK_SQUARE = QColor("#769656")
    SELECTED_COLOR = QColor(246, 246, 105, 190)
    LAST_MOVE_COLOR = QColor(246, 246, 105, 120)
    CHECK_COLOR = QColor(235, 64, 52, 180)
    LEGAL_DOT_COLOR = QColor(20, 20, 20, 65)
    USER_HIGHLIGHT_COLOR = QColor(235, 97, 80, 165)
    ARROW_COLOR = QColor(255, 170, 0, 185)
    ARROW_PREVIEW_COLOR = QColor(255, 170, 0, 120)

    def __init__(self, manager: BoardManager, parent=None) -> None:
        super().__init__(parent)
        self._manager = manager
        self._flipped = False
        self._selected_square: Optional[int] = None
        self._legal_targets: set[int] = set()
        self._dragging_square: Optional[int] = None
        self._drag_pos: Optional[QPointF] = None
        self._highlighted_squares: set[int] = set()
        self._arrows: list[tuple[int, int]] = []
        self._right_drag_start: Optional[int] = None
        self._right_drag_current: Optional[int] = None

        self._renderers: dict[str, QSvgRenderer] = {
            sym: QSvgRenderer(QByteArray(_build_piece_svg(sym)))
            for sym in ("P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k")
        }

        self.setMinimumSize(440, 440)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

    def set_flipped(self, flipped: bool) -> None:
        self._flipped = flipped
        self.update()

    def is_flipped(self) -> bool:
        return self._flipped

    def clear_selection(self) -> None:
        self._selected_square = None
        self._legal_targets.clear()
        self._dragging_square = None
        self._drag_pos = None
        self.update()

    def clear_annotations(self) -> None:
        self._highlighted_squares.clear()
        self._arrows.clear()
        self._right_drag_start = None
        self._right_drag_current = None
        self.update()

    def _square_center(self, square: int, ox: float, oy: float, sq: float) -> QPointF:
        row, col = self._square_to_rc(square)
        return QPointF(ox + (col + 0.5) * sq, oy + (row + 0.5) * sq)

    def _draw_arrow(
        self,
        painter: QPainter,
        from_sq: int,
        to_sq: int,
        ox: float,
        oy: float,
        sq: float,
        color: QColor,
    ) -> None:
        df = chess.square_file(to_sq) - chess.square_file(from_sq)
        dr = chess.square_rank(to_sq) - chess.square_rank(from_sq)
        is_knight_move = (abs(df) == 2 and abs(dr) == 1) or (abs(df) == 1 and abs(dr) == 2)

        p1 = self._square_center(from_sq, ox, oy, sq)
        p2 = self._square_center(to_sq, ox, oy, sq)
        head_hw = sq * 0.22
        shaft_hw = sq * 0.085

        if is_knight_move:
            if abs(df) == 2:
                corner_sq = chess.square(chess.square_file(to_sq), chess.square_rank(from_sq))
            else:
                corner_sq = chess.square(chess.square_file(from_sq), chess.square_rank(to_sq))
            corner = self._square_center(corner_sq, ox, oy, sq)

            d1x, d1y = corner.x() - p1.x(), corner.y() - p1.y()
            d2x, d2y = p2.x() - corner.x(), p2.y() - corner.y()
            len1 = math.hypot(d1x, d1y)
            len2 = math.hypot(d2x, d2y)
            if len1 < 1e-3 or len2 < 1e-3:
                return

            u1x, u1y = d1x / len1, d1y / len1
            u2x, u2y = d2x / len2, d2y / len2
            n1x, n1y = -u1y, u1x
            n2x, n2y = -u2y, u2x

            start = QPointF(p1.x() + u1x * (sq * 0.18), p1.y() + u1y * (sq * 0.18))
            tip = QPointF(p2.x() - u2x * (sq * 0.08), p2.y() - u2y * (sq * 0.08))
            head_len = min(sq * 0.36, len2 * 0.55)
            neck = QPointF(tip.x() - u2x * head_len, tip.y() - u2y * head_len)

            poly = QPolygonF(
                [
                    QPointF(start.x() + n1x * shaft_hw, start.y() + n1y * shaft_hw),
                    QPointF(corner.x() + (n1x + n2x) * shaft_hw, corner.y() + (n1y + n2y) * shaft_hw),
                    QPointF(neck.x() + n2x * shaft_hw, neck.y() + n2y * shaft_hw),
                    QPointF(neck.x() + n2x * head_hw, neck.y() + n2y * head_hw),
                    tip,
                    QPointF(neck.x() - n2x * head_hw, neck.y() - n2y * head_hw),
                    QPointF(neck.x() - n2x * shaft_hw, neck.y() - n2y * shaft_hw),
                    QPointF(corner.x() - (n1x + n2x) * shaft_hw, corner.y() - (n1y + n2y) * shaft_hw),
                    QPointF(start.x() - n1x * shaft_hw, start.y() - n1y * shaft_hw),
                ]
            )
        else:
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            dist = math.hypot(dx, dy)
            if dist < 1e-3:
                return

            ux, uy = dx / dist, dy / dist
            px, py = -uy, ux

            start = QPointF(p1.x() + ux * (sq * 0.18), p1.y() + uy * (sq * 0.18))
            tip = QPointF(p2.x() - ux * (sq * 0.08), p2.y() - uy * (sq * 0.08))
            usable_len = math.hypot(tip.x() - start.x(), tip.y() - start.y())
            if usable_len < 1e-3:
                return

            head_len = min(sq * 0.36, usable_len * 0.5)
            neck = QPointF(tip.x() - ux * head_len, tip.y() - uy * head_len)

            poly = QPolygonF(
                [
                    QPointF(start.x() + px * shaft_hw, start.y() + py * shaft_hw),
                    QPointF(neck.x() + px * shaft_hw, neck.y() + py * shaft_hw),
                    QPointF(neck.x() + px * head_hw, neck.y() + py * head_hw),
                    tip,
                    QPointF(neck.x() - px * head_hw, neck.y() - py * head_hw),
                    QPointF(neck.x() - px * shaft_hw, neck.y() - py * shaft_hw),
                    QPointF(start.x() - px * shaft_hw, start.y() - py * shaft_hw),
                ]
            )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawPolygon(poly)

    def _board_geometry(self) -> tuple[float, float, float]:
        """Returns (origin_x, origin_y, square_size) for centered square board."""
        margin = 20.0
        side = max(160.0, min(self.width(), self.height()) - 2 * margin)
        sq = side / 8.0
        ox = (self.width() - side) / 2.0
        oy = (self.height() - side) / 2.0
        return ox, oy, sq

    def _square_to_rc(self, square: int) -> tuple[int, int]:
        file_idx = chess.square_file(square)
        rank_idx = chess.square_rank(square)
        if self._flipped:
            row = rank_idx
            col = 7 - file_idx
        else:
            row = 7 - rank_idx
            col = file_idx
        return row, col

    def _pos_to_square(self, pos: QPointF) -> Optional[int]:
        ox, oy, sq = self._board_geometry()
        col = int((pos.x() - ox) // sq)
        row = int((pos.y() - oy) // sq)
        if not (0 <= col < 8 and 0 <= row < 8):
            return None
        if self._flipped:
            file_idx = 7 - col
            rank_idx = row
        else:
            file_idx = col
            rank_idx = 7 - row
        return chess.square(file_idx, rank_idx)

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        ox, oy, sq = self._board_geometry()
        status = self._manager.get_status()
        last_move = self._manager.get_last_move()
        last_squares = {last_move.from_square, last_move.to_square} if last_move else set()

        coord_font = QFont("Segoe UI", max(8, int(sq * 0.17)), QFont.Weight.DemiBold)
        painter.setFont(coord_font)

        # Draw squares & highlights
        for row in range(8):
            for col in range(8):
                file_idx = 7 - col if self._flipped else col
                rank_idx = row if self._flipped else 7 - row
                square = chess.square(file_idx, rank_idx)
                is_light = (file_idx + rank_idx) % 2 == 1

                rect = QRectF(ox + col * sq, oy + row * sq, sq, sq)
                painter.fillRect(rect, self.LIGHT_SQUARE if is_light else self.DARK_SQUARE)

                if square in last_squares:
                    painter.fillRect(rect, self.LAST_MOVE_COLOR)
                if square in self._highlighted_squares:
                    painter.fillRect(rect, self.USER_HIGHLIGHT_COLOR)
                if square == self._selected_square:
                    painter.fillRect(rect, self.SELECTED_COLOR)
                if status.check_square == square:
                    painter.fillRect(rect, self.CHECK_COLOR)

                # Rank & file labels along edges
                label_color = self.DARK_SQUARE if is_light else self.LIGHT_SQUARE
                painter.setPen(label_color)
                if col == 0:
                    painter.drawText(
                        rect.adjusted(3, 2, 0, 0),
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                        str(rank_idx + 1),
                    )
                if row == 7:
                    painter.drawText(
                        rect.adjusted(0, 0, -4, -2),
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                        chess.FILE_NAMES[file_idx],
                    )

        # Draw legal move indicators
        for target_sq in self._legal_targets:
            row, col = self._square_to_rc(target_sq)
            rect = QRectF(ox + col * sq, oy + row * sq, sq, sq)
            has_piece = self._manager.get_piece_at(target_sq) is not None
            if has_piece:
                pen = QPen(self.LEGAL_DOT_COLOR, max(3.0, sq * 0.08))
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(rect.adjusted(sq * 0.08, sq * 0.08, -sq * 0.08, -sq * 0.08))
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(self.LEGAL_DOT_COLOR)
                r = sq * 0.16
                painter.drawEllipse(rect.center(), r, r)

        # Draw static pieces
        for square, piece in self._manager.get_board_map().items():
            if square == self._dragging_square:
                continue
            row, col = self._square_to_rc(square)
            rect = QRectF(ox + col * sq, oy + row * sq, sq, sq).adjusted(
                sq * 0.06, sq * 0.06, -sq * 0.06, -sq * 0.06
            )
            self._renderers[piece.symbol()].render(painter, rect)

        # Draw dragged piece on top
        if self._dragging_square is not None and self._drag_pos is not None:
            piece = self._manager.get_piece_at(self._dragging_square)
            if piece is not None:
                half = sq * 0.48
                rect = QRectF(
                    self._drag_pos.x() - half,
                    self._drag_pos.y() - half,
                    half * 2,
                    half * 2,
                )
                self._renderers[piece.symbol()].render(painter, rect)

        # Draw user-drawn arrows and active right-drag preview
        for from_sq, to_sq in self._arrows:
            self._draw_arrow(painter, from_sq, to_sq, ox, oy, sq, self.ARROW_COLOR)
        if (
            self._right_drag_start is not None
            and self._right_drag_current is not None
            and self._right_drag_start != self._right_drag_current
        ):
            self._draw_arrow(
                painter,
                self._right_drag_start,
                self._right_drag_current,
                ox,
                oy,
                sq,
                self.ARROW_PREVIEW_COLOR,
            )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            sq = self._pos_to_square(event.position())
            self._right_drag_start = sq
            self._right_drag_current = sq
            return

        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self._highlighted_squares or self._arrows:
            self.clear_annotations()

        sq = self._pos_to_square(event.position())
        if sq is None:
            self.clear_selection()
            return

        # Click on a legal destination of currently selected piece
        if self._selected_square is not None and sq in self._legal_targets:
            self._attempt_move(self._selected_square, sq)
            return

        piece = self._manager.get_piece_at(sq)
        status = self._manager.get_status()
        is_turn_piece = (
            piece is not None
            and not status.is_game_over
            and (
                (piece.color == chess.WHITE and status.turn == "white")
                or (piece.color == chess.BLACK and status.turn == "black")
            )
        )

        if is_turn_piece:
            self._selected_square = sq
            self._legal_targets = {m.to_square for m in self._manager.get_legal_moves_from(sq)}
            self._dragging_square = sq
            self._drag_pos = event.position()
            self.update()
        else:
            self.clear_selection()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._right_drag_start is not None:
            self._right_drag_current = self._pos_to_square(event.position())
            self.update()
        if self._dragging_square is not None:
            self._drag_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton and self._right_drag_start is not None:
            start_sq = self._right_drag_start
            end_sq = self._pos_to_square(event.position())
            self._right_drag_start = None
            self._right_drag_current = None

            if end_sq is not None:
                if end_sq == start_sq:
                    if start_sq in self._highlighted_squares:
                        self._highlighted_squares.remove(start_sq)
                    else:
                        self._highlighted_squares.add(start_sq)
                else:
                    arrow = (start_sq, end_sq)
                    if arrow in self._arrows:
                        self._arrows.remove(arrow)
                    else:
                        self._arrows.append(arrow)
            self.update()
            return

        if event.button() != Qt.MouseButton.LeftButton or self._dragging_square is None:
            return
        from_sq = self._dragging_square
        to_sq = self._pos_to_square(event.position())
        self._dragging_square = None
        self._drag_pos = None

        if to_sq is not None and to_sq != from_sq and to_sq in self._legal_targets:
            self._attempt_move(from_sq, to_sq)
        else:
            self.update()

    def _attempt_move(self, from_sq: int, to_sq: int) -> None:
        promotion: Optional[int] = None
        if self._manager.is_promotion_move(from_sq, to_sq):
            is_white = self._manager.get_status().turn == "white"
            dialog = PromotionDialog(is_white=is_white, parent=self)
            if dialog.exec() != PromotionDialog.DialogCode.Accepted:
                self.clear_selection()
                return
            promotion = dialog.selected_piece

        try:
            self._manager.make_move(from_sq, to_sq, promotion=promotion)
        except ValueError as exc:
            self.status_message.emit(str(exc))
            self.clear_selection()
            return

        self.clear_selection()
        self.board_changed.emit()
