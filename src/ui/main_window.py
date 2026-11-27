"""Main desktop window for RealChess."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.core import AppSettings, BoardManager, load_settings, save_settings
from src.ui.board_widget import BoardWidget
from src.ui.intro_widget import IntroWidget
from src.ui.settings_dialog import SettingsDialog


class PgnDialog(QDialog):
    """Dialog for importing or exporting PGN text."""

    def __init__(self, initial_pgn: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nhập / Xuất PGN")
        self.resize(520, 380)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Dán PGN vào ô dưới để nhập, hoặc sao chép PGN hiện tại:"))

        self.editor = QPlainTextEdit()
        self.editor.setPlainText(initial_pgn)
        layout.addWidget(self.editor)

        btn_row = QHBoxLayout()
        copy_btn = QPushButton("Sao chép")
        copy_btn.clicked.connect(self._copy)
        load_btn = QPushButton("Nạp PGN này")
        load_btn.clicked.connect(self.accept)
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.reject)

        btn_row.addWidget(copy_btn)
        btn_row.addStretch()
        btn_row.addWidget(load_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _copy(self) -> None:
        QApplication.clipboard().setText(self.editor.toPlainText())


class MainWindow(QMainWindow):
    """Primary application window hosting the board and move/FEN/PGN controls."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("RealChess — Bàn cờ & Luật chuẩn")
        self.resize(980, 680)

        self._manager = BoardManager()
        self._settings = load_settings()

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # Page 0: Intro / Mode selection
        self._intro_widget = IntroWidget(ui_mode=self._settings.ui_mode)
        self._intro_widget.play_human_clicked.connect(self._on_play_human)
        self._intro_widget.play_ai_clicked.connect(self._on_play_ai)
        self._intro_widget.analysis_clicked.connect(self._on_analysis)
        self._intro_widget.settings_clicked.connect(self._on_settings)
        self._stack.addWidget(self._intro_widget)

        # Page 1: Chess board workspace
        self._game_page = QWidget()
        self._game_page.setObjectName("GamePage")
        main_layout = QHBoxLayout(self._game_page)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(16)
        self._stack.addWidget(self._game_page)

        # Left: Chess board
        self._board_widget = BoardWidget(self._manager, settings=self._settings)
        self._board_widget.board_changed.connect(self._refresh_ui)
        self._board_widget.status_message.connect(self._show_error)
        main_layout.addWidget(self._board_widget, stretch=3)

        # Right: Control panel
        side_panel = QVBoxLayout()
        side_panel.setSpacing(10)
        main_layout.addLayout(side_panel, stretch=2)

        self._status_label = QLabel()
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet(
            "font-size: 16px; font-weight: 700; padding: 8px; "
            "background: #23272E; color: #F8FAFC; border-radius: 6px;"
        )
        side_panel.addWidget(self._status_label)

        # Action buttons
        actions_row = QHBoxLayout()
        home_btn = QPushButton("← Trang chủ")
        home_btn.clicked.connect(self._on_back_to_intro)
        new_btn = QPushButton("Ván mới")
        new_btn.clicked.connect(self._on_new_game)
        undo_btn = QPushButton("Đi lại")
        undo_btn.clicked.connect(self._on_undo)
        flip_btn = QPushButton("Xoay bàn cờ")
        flip_btn.clicked.connect(self._on_flip)
        settings_btn = QPushButton("⚙")
        settings_btn.setToolTip("Cài đặt giao diện")
        settings_btn.setFixedWidth(40)
        settings_btn.setStyleSheet("font-size: 16px;")
        settings_btn.clicked.connect(self._on_settings)
        for btn in (home_btn, new_btn, undo_btn, flip_btn, settings_btn):
            btn.setMinimumHeight(34)
            actions_row.addWidget(btn)
        side_panel.addLayout(actions_row)

        # Move history
        side_panel.addWidget(QLabel("Lịch sử nước đi:"))
        self._moves_view = QPlainTextEdit()
        self._moves_view.setReadOnly(True)
        self._moves_view.setStyleSheet("font-family: Consolas, monospace; font-size: 13px;")
        side_panel.addWidget(self._moves_view, stretch=1)

        # FEN controls
        side_panel.addWidget(QLabel("FEN:"))
        fen_row = QHBoxLayout()
        self._fen_input = QLineEdit()
        load_fen_btn = QPushButton("Nạp FEN")
        load_fen_btn.clicked.connect(self._on_load_fen)
        copy_fen_btn = QPushButton("Copy")
        copy_fen_btn.clicked.connect(self._on_copy_fen)
        fen_row.addWidget(self._fen_input, stretch=1)
        fen_row.addWidget(load_fen_btn)
        fen_row.addWidget(copy_fen_btn)
        side_panel.addLayout(fen_row)

        # PGN button
        pgn_btn = QPushButton("Nhập / Xuất PGN...")
        pgn_btn.setMinimumHeight(34)
        pgn_btn.clicked.connect(self._on_pgn_dialog)
        side_panel.addWidget(pgn_btn)

        self._apply_ui_mode(self._settings.ui_mode)
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        status = self._manager.get_status()
        self._status_label.setText(status.outcome_text)
        self._fen_input.setText(self._manager.get_fen())
        self._moves_view.setPlainText(self._format_moves())
        self._board_widget.update()

    def _format_moves(self) -> str:
        history = self._manager.get_move_history()
        if not history:
            return "(Chưa có nước đi nào)"
        lines: list[str] = []
        i = 0
        while i < len(history):
            white_rec = history[i]
            if white_rec.color == "black":
                lines.append(f"{white_rec.move_number}... {white_rec.san}")
                i += 1
                continue
            black_part = ""
            if i + 1 < len(history) and history[i + 1].color == "black":
                black_part = f"  {history[i + 1].san}"
                i += 2
            else:
                i += 1
            lines.append(f"{white_rec.move_number}. {white_rec.san}{black_part}")
        return "\n".join(lines)

    def _on_play_human(self) -> None:
        self._stack.setCurrentIndex(1)

    def _on_play_ai(self) -> None:
        QMessageBox.information(
            self,
            "Chơi với AI",
            "Tính năng đấu với Stockfish AI sẽ được triển khai ở mốc tiếp theo.",
        )

    def _on_analysis(self) -> None:
        QMessageBox.information(
            self,
            "Phân tích ván cờ",
            "Tính năng Phân tích ván cờ sẽ được triển khai ở các mốc tiếp theo.",
        )

    def _on_back_to_intro(self) -> None:
        self._stack.setCurrentIndex(0)

    def _on_new_game(self) -> None:
        self._manager.reset()
        self._board_widget.clear_selection()
        self._board_widget.clear_annotations()
        self._refresh_ui()

    def _on_undo(self) -> None:
        self._manager.undo_move()
        self._board_widget.clear_selection()
        self._board_widget.clear_annotations()
        self._refresh_ui()

    def _on_flip(self) -> None:
        self._board_widget.set_flipped(not self._board_widget.is_flipped())

    def _on_settings(self) -> None:
        dialog = SettingsDialog(self._settings, parent=self)
        dialog.settings_applied.connect(self._apply_all_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._settings = dialog.current_settings()
            self._apply_all_settings(self._settings)
            save_settings(self._settings)

    def _apply_all_settings(self, settings: AppSettings) -> None:
        self._board_widget.apply_settings(settings)
        self._intro_widget.apply_ui_mode(settings.ui_mode)
        self._apply_ui_mode(settings.ui_mode)

    def _apply_ui_mode(self, mode: str) -> None:
        if mode == "dark":
            self.setStyleSheet(
                "QMainWindow, #GamePage { background-color: #16191D; color: #F3F4F6; }"
                "QLabel { color: #F3F4F6; }"
                "QPushButton { background-color: #1E2329; color: #F3F4F6; "
                "border: 1px solid #2D333B; border-radius: 6px; padding: 4px 10px; }"
                "QPushButton:hover { border-color: #5B8C3A; }"
                "QPlainTextEdit, QLineEdit { background-color: #1E2329; color: #F3F4F6; "
                "border: 1px solid #2D333B; border-radius: 6px; padding: 4px; }"
            )
        else:
            self.setStyleSheet(
                "QMainWindow, #GamePage { background-color: #F7F8FA; color: #111827; }"
                "QLabel { color: #111827; }"
                "QPushButton { background-color: #FFFFFF; color: #111827; "
                "border: 1px solid #E5E7EB; border-radius: 6px; padding: 4px 10px; }"
                "QPushButton:hover { border-color: #5B8C3A; }"
                "QPlainTextEdit, QLineEdit { background-color: #FFFFFF; color: #111827; "
                "border: 1px solid #E5E7EB; border-radius: 6px; padding: 4px; }"
            )

    def _on_load_fen(self) -> None:
        try:
            self._manager.load_fen(self._fen_input.text())
        except ValueError as exc:
            self._show_error(str(exc))
            return
        self._board_widget.clear_selection()
        self._board_widget.clear_annotations()
        self._refresh_ui()

    def _on_copy_fen(self) -> None:
        QApplication.clipboard().setText(self._manager.get_fen())

    def _on_pgn_dialog(self) -> None:
        dialog = PgnDialog(self._manager.export_pgn(), parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self._manager.load_pgn(dialog.editor.toPlainText())
            except ValueError as exc:
                self._show_error(str(exc))
                return
            self._board_widget.clear_selection()
            self._board_widget.clear_annotations()
            self._refresh_ui()

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Thông báo", message)
