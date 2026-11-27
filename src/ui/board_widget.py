"""Interactive 8x8 chess board widget rendered with PySide6 & SVG pieces."""

from __future__ import annotations

import math
from typing import Optional

import chess
from PySide6.QtCore import QByteArray, QEasingCurve, QPointF, QRectF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPen, QPolygonF
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QSizePolicy, QWidget

from src.core import AppSettings, BoardManager
from src.ui.promotion_dialog import PromotionDialog
from src.ui.themes import ANIMATION_SPEEDS, BOARD_THEMES, BoardTheme, build_piece_svg


class BoardWidget(QWidget):
    """Interactive 8x8 chess board supporting click-to-move and drag-and-drop."""

    board_changed = Signal()
    status_message = Signal(str)

    CHECK_COLOR = QColor(235, 64, 52, 180)
    LEGAL_DOT_COLOR = QColor(20, 20, 20, 65)
    USER_HIGHLIGHT_COLOR = QColor(235, 97, 80, 165)
    ARROW_COLOR = QColor(255, 170, 0, 185)
    ARROW_PREVIEW_COLOR = QColor(255, 170, 0, 120)

    def __init__(self, manager: BoardManager, settings: Optional[AppSettings] = None, parent=None) -> None:
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

        self._theme: BoardTheme = BOARD_THEMES["classic_green"]
        self._piece_style: str = ""
        self._anim_duration_ms: int = 120
        self._renderers: dict[str, QSvgRenderer] = {}

        self._anim_from_sq: Optional[int] = None
        self._anim_to_sq: Optional[int] = None
        self._anim_piece_symbol: Optional[str] = None
        self._anim_progress: float = 1.0
        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_anim_value)
        self._anim.finished.connect(self._on_anim_finished)

        self.apply_settings(settings or AppSettings())

        self.setMinimumSize(440, 440)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

    def apply_settings(self, settings: AppSettings) -> None:
        """Applies board theme, piece style, and animation speed."""
        self._theme = BOARD_THEMES.get(settings.board_theme, BOARD_THEMES["classic_green"])
        _label, duration = ANIMATION_SPEEDS.get(settings.animation_speed, ANIMATION_SPEEDS["fast"])
        self._anim_duration_ms = duration

        if settings.piece_style != self._piece_style:
            self._piece_style = settings.piece_style
            self._renderers = {
                sym: QSvgRenderer(QByteArray(build_piece_svg(sym, self._piece_style)))
                for sym in ("P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k")
            }
        self.update()

    def _on_anim_value(self, value: float) -> None:
        self._anim_progress = float(value)
        self.update()

    def _on_anim_finished(self) -> None:
        self._anim_from_sq = None
        self._anim_to_sq = None
        self._anim_piece_symbol = None
        self._anim_progress = 1.0
        self.update()

    def start_move_animation(self, from_sq: int, to_sq: int, piece_symbol: str) -> None:
        """Animates a piece sliding from from_sq to to_sq if animation is enabled."""
        if self._anim_duration_ms <= 0:
            return
        self._anim.stop()
        self._anim_from_sq = from_sq
        self._anim_to_sq = to_sq
        self._anim_piece_symbol = piece_symbol
        self._anim_progress = 0.0
        self._anim.setDuration(self._anim_duration_ms)
        self._anim.start()

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
                painter.fillRect(rect, self._theme.light_square if is_light else self._theme.dark_square)

                if square in last_squares:
                    painter.fillRect(rect, self._theme.last_move_color)
                if square in self._highlighted_squares:
                    painter.fillRect(rect, self.USER_HIGHLIGHT_COLOR)
                if square == self._selected_square:
                    painter.fillRect(rect, self._theme.selected_color)
                if status.check_square == square:
                    painter.fillRect(rect, self.CHECK_COLOR)

                # Rank & file labels along edges
                label_color = self._theme.dark_square if is_light else self._theme.light_square
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
            if square == self._dragging_square or square == self._anim_to_sq:
                continue
            row, col = self._square_to_rc(square)
            rect = QRectF(ox + col * sq, oy + row * sq, sq, sq).adjusted(
                sq * 0.06, sq * 0.06, -sq * 0.06, -sq * 0.06
            )
            self._renderers[piece.symbol()].render(painter, rect)

        # Draw animated moving piece
        if (
            self._anim_from_sq is not None
            and self._anim_to_sq is not None
            and self._anim_piece_symbol is not None
        ):
            p1 = self._square_center(self._anim_from_sq, ox, oy, sq)
            p2 = self._square_center(self._anim_to_sq, ox, oy, sq)
            cx = p1.x() + (p2.x() - p1.x()) * self._anim_progress
            cy = p1.y() + (p2.y() - p1.y()) * self._anim_progress
            half = sq * 0.44
            rect = QRectF(cx - half, cy - half, half * 2, half * 2)
            self._renderers[self._anim_piece_symbol].render(painter, rect)

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
            if self._dragging_square is not None:
                self.clear_selection()
                return
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
            self._attempt_move(from_sq, to_sq, animate=False)
        else:
            self.update()

    def _attempt_move(self, from_sq: int, to_sq: int, animate: bool = True) -> None:
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

        moved_piece = self._manager.get_piece_at(to_sq)
        self.clear_selection()
        if animate and moved_piece is not None:
            self.start_move_animation(from_sq, to_sq, moved_piece.symbol())
        self.board_changed.emit()
