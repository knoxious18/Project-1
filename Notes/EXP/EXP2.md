# EXP 2: Hoàn thiện giao diện bàn cờ (Chú thích, Chủ đề & Animation)

- **Phạm vi:** Chú thích trực quan (mũi tên thẳng, mũi tên chữ L, highlight ô), hệ thống chủ đề bàn cờ, kiểu quân cờ, animation di chuyển quân và hộp thoại Cài đặt
- **Commit tham chiếu:** `a4f31db` (highlight & mũi tên), `1e07f83` (mũi tên chữ L), `e9ce8e9` (chủ đề, kiểu quân, animation & cài đặt)

---

## 1. Cơ chế tương tác chuột phải (Mũi tên và Highlight ô)

Toàn bộ thao tác chú thích được xử lý trong `BoardWidget` (`src/ui/board_widget.py`) thông qua ba sự kiện chuột:

1. **`mousePressEvent`:** Khi nhấn chuột phải, ghi nhận ô bắt đầu (`_right_drag_start`) và ô hiện tại (`_right_drag_current`).
2. **`mouseMoveEvent`:** Khi đang giữ chuột phải, liên tục ánh xạ tọa độ con trỏ sang ô cờ đích và kích hoạt vẽ lại (`update()`).
3. **`mouseReleaseEvent`:**
   - Nếu ô thả chuột trùng với ô bắt đầu (`end_sq == start_sq`): bật/tắt trạng thái highlight ô trong tập `_highlighted_squares`.
   - Nếu ô thả chuột khác ô bắt đầu (`end_sq != start_sq`): thêm hoặc xóa cặp `(start_sq, end_sq)` trong danh sách `_arrows`.
4. **Cơ chế xóa chú thích (`clear_annotations`):** Tự động xóa toàn bộ mũi tên và ô highlight khi người dùng nhấn chuột trái trên bàn cờ, hoặc khi thay đổi trạng thái ván đấu (*Ván mới*, *Đi lại*, *Nạp FEN*, *Nạp PGN*).

### Điểm nổi bật: Xem trước mũi tên theo thời gian thực
Khác với một số nền tảng chỉ hiển thị mũi tên sau khi người dùng thả chuột (như Chess.com), `BoardWidget` vẽ lớp mũi tên xem trước (`ARROW_PREVIEW_COLOR`) ngay trong quá trình kéo chuột (`mouseMoveEvent`). Điều này cho phép quan sát trực tiếp hướng đi, điểm dừng và hình dạng chữ L trước khi xác nhận thả tay.

---

## 2. Kỹ thuật dựng hình học mũi tên (Polygon đơn nhất)

Để mũi tên có độ trong suốt (alpha channel) đồng đều mà không xuất hiện vết chồng màu tại điểm nối giữa thân và đầu mũi tên (hoặc tại góc vuông), mỗi mũi tên được dựng thành **một đa giác khép kín duy nhất (`QPolygonF`)** và vẽ bằng `QPainter.drawPolygon()`:

- **Mũi tên thẳng (7 đỉnh):** Tính vector đơn vị dọc theo đường nối tâm hai ô và vector pháp tuyến vuông góc để xác định hai cạnh thân và ba đỉnh đầu mũi tên.
- **Mũi tên quân Mã (hình chữ L, 9 đỉnh):**
  - Điều kiện nhận diện: độ lệch tọa độ thỏa mãn `(abs(df) == 2 and abs(dr) == 1)` hoặc `(abs(df) == 1 and abs(dr) == 2)`.
  - Điểm gãy góc (`corner`) luôn đi theo trục có khoảng cách 2 ô trước, sau đó rẽ vuông góc 90 độ theo trục còn lại.
  - Từ hai vector đơn vị `u1`, `u2` và hai pháp tuyến `n1`, `n2`, tọa độ góc ngoài và góc trong tại `corner` được tính thống nhất theo `corner ± (n1 + n2) * shaft_hw`, áp dụng chính xác cho cả 8 hướng nhảy của quân Mã.

---

## 3. Hệ thống chủ đề, kiểu quân cờ và lưu trữ cấu hình

- **Tách cấu hình khỏi giao diện (`src/core/settings.py`):**
  - `AppSettings` lưu ba tùy chọn: `board_theme`, `piece_style`, `animation_speed`.
  - `load_settings()` và `save_settings()` đọc/ghi tệp cục bộ `settings.json` (đã loại trừ khỏi Git trong `.gitignore`), tự động khôi phục giá trị mặc định nếu tệp chưa tồn tại hoặc lỗi định dạng.
- **Quản lý giao diện (`src/ui/themes.py`):**
  - `BOARD_THEMES`: Định nghĩa bảng màu (`light_square`, `dark_square`, `selected_color`, `last_move_color`) cho 4 chủ đề (*Cổ điển*, *Gỗ ấm*, *Đại dương*, *Tối hiện đại*).
  - `build_piece_svg(symbol, style_id)`: Tạo mã vector SVG cho 3 kiểu quân (*Cổ điển*, *Tối giản*, *Ấm áp*). `BoardWidget.apply_settings()` chỉ tạo lại bộ `QSvgRenderer` khi `piece_style` thực sự thay đổi nhằm tránh chi phí dựng lại không cần thiết.
- **Hộp thoại Cài đặt (`src/ui/settings_dialog.py`):**
  - Mở từ nút bánh răng (`⚙`) trên cửa sổ chính. Phát tín hiệu `settings_applied` mỗi khi người dùng đổi lựa chọn để xem trước trực tiếp trên bàn cờ, và tự động hoàn nguyên về cấu hình ban đầu nếu chọn *Hủy*.

---

## 4. Animation di chuyển quân cờ

- Sử dụng `QVariantAnimation` (nội suy từ `0.0` đến `1.0` với đường cong giảm tốc `QEasingCurve.Type.OutCubic`) trong `BoardWidget` với 4 mức tốc độ: *Tắt (0 ms)*, *Nhanh (120 ms)*, *Trung bình (220 ms)*, *Chậm (380 ms)*.
- Khi hiệu ứng đang chạy, `paintEvent()` bỏ qua việc vẽ quân tĩnh tại ô đích (`_anim_to_sq`) và vẽ quân tại tọa độ nội suy giữa tâm ô nguồn và tâm ô đích.
- Hiệu ứng chỉ kích hoạt với thao tác *click-to-move* (và sẵn sàng tái sử dụng cho nước đi của AI/PGN sau này); thao tác *kéo-thả* đặt quân trực tiếp tại vị trí thả chuột để đảm bảo phản hồi tức thì.

---

## 5. Hủy thao tác giữ quân bằng chuột phải

- Trong `BoardWidget.mousePressEvent()`, nhánh xử lý `Qt.MouseButton.RightButton` kiểm tra `self._dragging_square is not None` trước khi khởi tạo thao tác chú thích.
- Nếu người dùng đang kéo giữ một quân cờ bằng chuột trái và nhấn chuột phải, phương thức gọi `self.clear_selection()` để trả quân về ô xuất phát, hủy trạng thái chọn/kéo và thoát sớm mà không kích hoạt highlight ô hay vẽ mũi tên.

---

## 6. Màn hình Intro và điều hướng chế độ chơi (`QStackedWidget`)

- **Cấu trúc điều hướng (`src/ui/main_window.py`):** `MainWindow` sử dụng `QStackedWidget` làm widget trung tâm gồm hai trang:
  - Trang `0`: `IntroWidget` (`src/ui/intro_widget.py`) hiển thị khi khởi động, cung cấp ba lựa chọn chế độ (*Play with Human*, *Play with AI*, *Analysis*) và nút mở hộp thoại *Cài đặt (⚙)*.
  - Trang `1`: Giao diện bàn cờ và bảng điều khiển, bổ sung nút **← Trang chủ** để quay lại màn hình Intro khi cần.
- Chọn *Play with Human* chuyển trực tiếp sang trang bàn cờ; *Play with AI* và *Analysis* hiện giữ vai trò điểm chờ cho các mốc phát triển tiếp theo.
