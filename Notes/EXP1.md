# EXP 1: Khởi tạo dự án, Bàn cờ, Luật chuẩn & FEN/PGN

> **Mốc thực hiện:** Mốc 1 (Bàn cờ + Luật chuẩn + Nhập/Xuất FEN & PGN)  
> **Commit tham chiếu:** `df74bc0` (`feat: initialize RealChess with core board logic, PySide6 UI, and FEN/PGN support`)

---

## 1. Đặt tên `EXP1` theo từng mốc / commit có ổn không?

**Rất hợp lý**, đặc biệt khi bạn muốn học từ chính quá trình làm dự án:
- Mỗi khi xong một tính năng lớn (hoặc một cụm commit), bạn có 1 ghi chú `EXP1`, `EXP2`, `EXP3`... gắn với mã commit.
- Sau này quên vì sao mình viết file đó hoặc gặp lại lỗi tương tự, chỉ cần mở đúng `EXP` của mốc đó (hoặc tra theo commit) là nhớ lại ngay toàn bộ bối cảnh.

---

## 2. Những công nghệ & công cụ đã dùng trong Mốc 1

| Thành phần | Nó là gì (nói dễ hiểu)? | Dùng để làm gì trong dự án này? |
| :--- | :--- | :--- |
| **Python 3.12** | Ngôn ngữ lập trình chính | Viết toàn bộ logic và giao diện phần mềm |
| **`.venv` (Virtual Environment)** | Một "hộp cát" chứa thư viện riêng cho dự án | Giúp cài `PySide6`, `python-chess` gọn trong thư mục `Project 1`, không làm rối các dự án Python khác trên máy |
| **`python-chess`** | Thư viện cờ vua có sẵn rất uy tín | Xử lý toàn bộ luật cờ (nước đi hợp lệ, nhập thành, bắt tốt qua đường, phong cấp, chiếu hết, hòa...) và đọc/ghi FEN, PGN |
| **`PySide6` (Qt for Python)** | Bộ công cụ làm giao diện phần mềm desktop (`.exe`) | Vẽ cửa sổ, nút bấm, hộp thoại, và tự vẽ bàn cờ 8x8 + quân cờ |
| **`pytest`** | Công cụ chạy kiểm thử tự động | Tự động kiểm tra xem logic cờ (`BoardManager`) có chạy đúng không sau mỗi lần sửa code |
| **Git & GitHub** | Hệ thống lưu lịch sử code & đồng bộ lên mạng | Lưu từng phiên bản code theo từng tính năng (`commit` & `push`) |

---

## 3. Ý nghĩa từng file và thư mục vừa tạo

### Kiến trúc tổng thể: Tách riêng **Logic (`src/core`)** và **Giao diện (`src/ui`)**
Tại sao phải tách làm 2 thư mục như vậy thay vì viết chung vào 1 file?
- **`src/core/` (Bộ não):** Chỉ lo luật cờ, tính toán, lưu lịch sử. Nó **không biết gì về nút bấm hay màn hình**.
- **`src/ui/` (Mặt tiền):** Chỉ lo vẽ bàn cờ lên màn hình, nhận cú click/kéo chuột của người chơi rồi hỏi `src/core/` xem nước đó có hợp lệ không.
- **Lợi ích sau này:** Khi bạn làm thêm AI Stockfish, phân tích ván đấu, hoặc chuyển sang chơi **Online** (nơi logic phải chạy trên Server chứ không có màn hình), bạn giữ nguyên `src/core/` mà không phải đập đi viết lại.

### Chi tiết từng file

- `main.py` — **Cửa chính để bật app.** Khi chạy `python main.py`, file này khởi động Qt (`QApplication`) và mở cửa sổ chính `MainWindow`.
- `src/core/board_manager.py` — **Trái tim của Mốc 1.** Chứa:
  - `BoardManager`: Lớp quản lý bàn cờ, kiểm tra nước đi hợp lệ, đi lại (`undo_move`), đọc/xuất FEN và PGN, kiểm tra kết thúc ván (chiếu hết, hòa...).
  - `MoveRecord`: Lưu thông tin 1 nước đi đã đánh (số thứ tự nước, bên đi, ký hiệu `e4`, ký hiệu máy `e2e4`, FEN sau nước đi).
  - `GameStatus`: Tóm tắt tình trạng hiện tại của ván cờ (đến lượt ai, có đang bị chiếu không, đã kết thúc chưa, kết quả `1-0` / `0-1` / `1/2-1/2`).
- `src/ui/board_widget.py` — **Bàn cờ tương tác 8x8.** Lo việc vẽ 64 ô cờ, vẽ quân cờ, tô màu nước vừa đi, chấm tròn gợi ý nước hợp lệ, và xử lý thao tác chuột (click để đi hoặc kéo-thả).
- `src/ui/promotion_dialog.py` — **Hộp thoại phong cấp.** Hiện ra khi Tốt đi đến hàng cuối để người chơi chọn Hậu, Xe, Tượng hoặc Mã.
- `src/ui/main_window.py` — **Cửa sổ chính của phần mềm.** Ghép `BoardWidget` ở bên trái với bảng điều khiển ở bên phải (trạng thái lượt đi, nút *Ván mới / Đi lại / Xoay bàn cờ*, lịch sử nước đi, ô nhập/copy FEN và hộp thoại PGN).
- `tests/test_board_manager.py` — **Bài kiểm tra tự động.** Chạy 8 kịch bản test (đi quân, nhập thành, bắt tốt qua đường, phong cấp, chiếu bí kiểu Fool's Mate, hòa 3 lần lặp, undo, FEN/PGN).
- `requirements.txt` — Danh sách thư viện cần cài (`python-chess`, `PySide6`, `pytest`) để sau này sang máy khác chỉ cần 1 lệnh là cài đủ.
- `.gitignore` — Danh sách các file/thư mục **không đẩy lên GitHub** (ví dụ `.venv/`, file rác `__pycache__/`, file tạm của hệ thống) để repo luôn nhẹ và sạch.
- `README.md` — Trang giới thiệu dự án và hướng dẫn cài đặt, chạy thử trên GitHub.

---

## 4. Giao diện bàn cờ được vẽ như thế nào? Quân cờ lấy ở đâu?

Nhiều người mới nghĩ làm game cờ phải tải 12 file ảnh `.png` về rồi ghép lên màn hình. Ở đây mình dùng cách gọn và nét hơn:

1. **Vẽ bàn cờ bằng `QPainter` (cọ vẽ của Qt):**
   - Trong `BoardWidget.paintEvent()`, code chia vùng vẽ thành lưới `8 x 8` ô vuông bằng nhau.
   - Mỗi ô được tô màu sáng (`#EEEED2`) hoặc tối (`#769656`), cộng thêm các lớp màu bán trong suốt nếu ô đó là: ô đang chọn, nước vừa đi, hoặc ô Vua đang bị chiếu.
   - Khi bấm **"Xoay bàn cờ"**, biến `_flipped` đổi sang `True`, công thức tính hàng/cột tự đảo ngược lại (từ góc nhìn quân Đen).

2. **Quân cờ lấy ở đâu? — Tự dựng bằng SVG ngay trong code:**
   - Thay vì phụ thuộc file ảnh ngoài (dễ lỗi đường dẫn khi đóng gói `.exe`), hàm `_build_piece_svg(symbol)` tạo ra **mã vector SVG** cho cả 12 quân cờ (6 quân Trắng, 6 quân Đen).
   - `QSvgRenderer` đọc trực tiếp chuỗi SVG đó và vẽ lên bàn cờ.
   - **Ưu điểm:** Vì là vector SVG nên bạn có phóng to cửa sổ ra màn hình 2K/4K thì quân cờ vẫn sắc nét, không bao giờ bị vỡ hạt.

3. **Thao tác chuột (Click-to-move & Drag-and-drop):**
   - Khi nhấn chuột xuống một quân đúng lượt (`mousePressEvent`), `BoardWidget` hỏi `BoardManager.get_legal_moves_from(square)` để lấy danh sách các ô hợp lệ rồi vẽ chấm tròn gợi ý.
   - Nếu bạn **kéo chuột** (`mouseMoveEvent`), quân cờ đi theo con trỏ; khi **thả chuột** (`mouseReleaseEvent`) vào ô hợp lệ thì nước đi được thực hiện.
   - Nếu bạn chỉ **click 1 lần** vào quân rồi **click tiếp** vào ô đích, nước đi cũng được thực hiện bình thường.

---

## 5. FEN và PGN là gì? (Nền tảng cho mọi tính năng sau)

- **FEN (Forsyth–Edwards Notation):** Là một dòng chữ ngắn mô tả **ảnh chụp 1 thế cờ tại 1 thời điểm** (vị trí các quân, đến lượt ai, còn quyền nhập thành không, có ô bắt tốt qua đường không...).
  - *Ví dụ FEN xuất phát:* `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
  - *Dùng để làm gì:* Lưu thế cờ nhanh, làm bài tập Puzzle, hoặc làm **nút (node)** trong đồ thị khai cuộc ở Mốc 4!
- **PGN (Portable Game Notation):** Là định dạng chuẩn lưu **cả một ván cờ từ đầu đến cuối** (tên người chơi, kết quả, toàn bộ chuỗi nước đi `1. e4 e5 2. Nf3...`).
  - *Dùng để làm gì:* Xuất ván vừa chơi để chia sẻ, hoặc nạp ván đấu tải từ Chess.com / Lichess vào phần mềm để phân tích ở Mốc 3.

---

## 6. Một bài học thực tế ngay trong Mốc 1 (Lỗi đã gặp & cách sửa)

Trong lúc viết test cho luật **Hòa do lặp lại thế cờ 3 lần**, bài test bị lỗi ngay trước nước đi cuối cùng:
- **Nguyên nhân:** Hàm `board.outcome(claim_draw=True)` của thư viện `python-chess` kiểm tra xem *"người chơi có quyền đòi hòa không"*. Theo luật FIDE, bạn có quyền đòi hòa ngay cả khi thế cờ sắp lặp lần thứ 3 **ở nước đi tiếp theo** (chỉ cần chỉ ra nước đi đó). Vì vậy app tưởng ván đã kết thúc sớm hơn 1 nước!
- **Cách sửa:** Tách rõ ra trong `BoardManager.get_status()`:
  1. Kiểm tra `board.outcome(claim_draw=False)` (chiếu hết, hết nước đi, thiếu lực lượng, 5 lần lặp, 75 nước).
  2. Kiểm tra trực tiếp `board.is_repetition(3)` và `board.is_fifty_moves()` để chỉ báo hòa **sau khi nước đi thứ 3 thực sự được đi trên bàn cờ** (giống trải nghiệm trên Lichess / Chess.com).
- **Bài học rút ra:** Đừng tin 100% rằng thư viện chạy đúng ý mình cho tới khi tự viết `pytest` kiểm tra các trường hợp biên (edge cases) như lặp lại 3 lần hay phong cấp.

---

## 7. Bước tiếp theo
Sau khi bạn chạy thử `.\.venv\Scripts\python.exe main.py` và kiểm tra ổn các thao tác (đi quân, phong cấp, đi lại, nạp/xuất FEN & PGN), chúng ta sẽ bước sang **Mốc 2: Tích hợp engine AI Stockfish** (chọn độ khó, chơi với máy).
