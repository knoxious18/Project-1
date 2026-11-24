# EXP 1: Khởi tạo dự án, Bàn cờ, Luật chuẩn & FEN/PGN

- **Phạm vi:** Mốc 1 — Bàn cờ, luật cờ vua chuẩn, nhập/xuất FEN và PGN
- **Commit tham chiếu:** `df74bc0` (`feat: initialize RealChess with core board logic, PySide6 UI, and FEN/PGN support`)

---

## 1. Công nghệ và công cụ sử dụng

| Thành phần | Vai trò kỹ thuật |
| :--- | :--- |
| **Python 3.12** | Ngôn ngữ triển khai chính cho toàn bộ tầng logic và giao diện. |
| **`.venv` (Virtual Environment)** | Cô lập các thư viện phụ thuộc theo từng dự án, tránh xung đột phiên bản với môi trường hệ thống. |
| **`python-chess`** | Thư viện xử lý luật cờ vua chuẩn, sinh nước đi hợp lệ, kiểm tra trạng thái kết thúc ván và phân tích/xuất định dạng FEN, PGN. |
| **`PySide6` (Qt for Python)** | Framework xây dựng giao diện desktop đa nền tảng (widget, hộp thoại, hệ thống sự kiện và đồ họa 2D). |
| **`pytest`** | Framework kiểm thử đơn vị (unit testing) cho tầng logic. |
| **Git & GitHub** | Quản lý phiên bản mã nguồn theo từng mốc phát triển. |

---

## 2. Kiến trúc và chức năng các tệp mã nguồn

### Nguyên tắc tách tầng (`src/core` và `src/ui`)
Hệ thống được chia làm hai lớp độc lập:
- **`src/core/` (Domain Logic):** Chỉ phụ thuộc `python-chess` và thư viện chuẩn Python, hoàn toàn không tham chiếu tới `PySide6`.
- **`src/ui/` (Presentation Layer):** Đọc trạng thái từ `src/core/` để hiển thị và chuyển tiếp thao tác người dùng xuống tầng logic.

Cách tổ chức này cho phép tái sử dụng nguyên vẹn tầng logic khi mở rộng sang AI Stockfish, phân tích ván đấu, hoặc triển khai máy chủ ở giai đoạn online.

### Vai trò từng tệp

- `main.py`: Điểm khởi chạy ứng dụng, khởi tạo `QApplication` và hiển thị `MainWindow`.
- `src/core/board_manager.py`:
  - `BoardManager`: Quản lý trạng thái bàn cờ, xác thực nước đi, hoàn tác (`undo_move`), đọc/xuất FEN và PGN, xác định kết quả ván đấu.
  - `MoveRecord`: Bản ghi bất biến (`dataclass(frozen=True)`) lưu thông tin mỗi nửa nước đi (`ply`, `move_number`, `color`, `uci`, `san`, `fen_after`).
  - `GameStatus`: Bản ghi trạng thái hiện tại của ván đấu (`is_game_over`, `result`, `termination`, `outcome_text`, `turn`, `in_check`, `check_square`).
- `src/ui/board_widget.py`: Widget bàn cờ 8x8, đảm nhận vẽ lưới ô cờ, quân cờ, đánh dấu ô hợp lệ/nước vừa đi/ô bị chiếu và xử lý sự kiện chuột.
- `src/ui/promotion_dialog.py`: Hộp thoại cho phép người dùng chọn quân phong cấp (Hậu, Xe, Tượng, Mã).
- `src/ui/main_window.py`: Cửa sổ chính tích hợp `BoardWidget` với bảng điều khiển (trạng thái ván đấu, nút điều khiển, danh sách nước đi SAN, nhập/xuất FEN và PGN).
- `tests/test_board_manager.py`: Bộ 8 ca kiểm thử đơn vị bao phủ nước đi hợp lệ/bất hợp lệ, nhập thành, bắt tốt qua đường, phong cấp, chiếu hết, các luật hòa, hoàn tác và FEN/PGN.
- `requirements.txt`, `.gitignore`, `README.md`: Khai báo phụ thuộc, loại trừ tệp tạm/môi trường khỏi Git và tài liệu hướng dẫn cơ bản.

---

## 3. Cơ chế hiển thị và tương tác bàn cờ

1. **Vẽ bàn cờ bằng `QPainter`:**
   - Phương thức `BoardWidget.paintEvent()` chia vùng hiển thị thành lưới `8 x 8` ô vuông cân đối theo kích thước cửa sổ.
   - Các lớp hiển thị được vẽ theo thứ tự: nền ô sáng/tối, vùng tô sáng (nước vừa đi, ô đang chọn, vua bị chiếu), chỉ báo nước đi hợp lệ và quân cờ.
   - Chế độ xoay bàn cờ (`_flipped`) đảo ngược phép ánh xạ chỉ số hàng/cột giữa tọa độ màn hình và chỉ số ô cờ `0..63`.

2. **Đồ họa quân cờ bằng SVG nội tuyến:**
   - Hàm `_build_piece_svg(symbol)` tạo mã vector SVG chuẩn hóa trên hệ tọa độ `viewBox="0 0 45 45"` cho 12 loại quân.
   - `QSvgRenderer` kết xuất trực tiếp dữ liệu SVG lên `QPainter`, không phụ thuộc tệp ảnh ngoài và đảm bảo độ nét ở mọi tỷ lệ phóng.

3. **Xử lý thao tác chuột:**
   - Hỗ trợ đồng thời hai cơ chế: chọn rồi nhấp ô đích (click-to-move) và kéo-thả (drag-and-drop) thông qua `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent`.
   - Khi ô đích là nước phong cấp (`is_promotion_move`), giao diện mở `PromotionDialog` để lấy loại quân trước khi gọi `BoardManager.make_move()`.

---

## 4. Định dạng dữ liệu FEN và PGN

- **FEN (Forsyth–Edwards Notation):** Chuỗi mô tả trạng thái tức thời của một thế cờ (vị trí quân, lượt đi, quyền nhập thành, ô bắt tốt qua đường, bộ đếm nửa nước và số nước đi). Dùng làm khóa định danh thế cờ cho phân tích và đồ thị khai cuộc ở các mốc sau.
- **PGN (Portable Game Notation):** Định dạng chuẩn lưu toàn bộ ván đấu gồm thẻ thông tin (`Event`, `White`, `Black`, `Result`, hoặc `FEN` nếu xuất phát từ thế cờ tùy chỉnh) và chuỗi nước đi chuẩn SAN.

---

## 5. Vấn đề kỹ thuật gặp phải và hướng xử lý

- **Hiện tượng:** Ca kiểm thử luật hòa lặp lại 3 lần ném ngoại lệ `ValueError` ở nửa nước đi thứ 8 (trước khi thế cờ lặp lại lần thứ 3 thực sự xuất hiện trên bàn cờ).
- **Nguyên nhân:** `board.outcome(claim_draw=True)` trong `python-chess` kiểm tra điều kiện *có quyền đòi hòa* theo luật FIDE — tức trả về kết quả hòa ngay từ nước trước đó nếu bên đến lượt có một nước đi hợp lệ tạo ra lần lặp thứ 3.
- **Giải pháp:** Trong `BoardManager.get_status()`, tách thành kiểm tra `board.outcome(claim_draw=False)` (chiếu hết, hết nước đi, thiếu lực lượng, 5 lần lặp, 75 nước), sau đó kiểm tra tường minh `board.is_repetition(3)` và `board.is_fifty_moves()`. Nhờ đó trạng thái hòa chỉ kích hoạt sau khi nước đi thứ 3 (hoặc nước thứ 50) được thực hiện trên bàn cờ.
