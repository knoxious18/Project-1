# Phần mềm: REALCHESS / ChessMind
Ý tưởng: làm 1 phần mềm chơi cờ vua
Điểm hay: giao diện tốt, đồ hoạ đẹp, ... Chưa nghĩ ra thêm(?)
Điểm hay hơn: chạy được offline và online; tích hợp AI Stockfish
Điểm hay nhất: phân tích ván cờ miễn phí không mất tiền như chess.com
*Tính năng được in nghiêng là tính năng khó / chưa nghĩ ra cách*

Mong muốn: phần mềm cài trên máy (file .exe?), không làm web app để có thể triển khai được phân tích offline(phần 3)

## 1. Giao diện
- [ ] Bàn cờ cơ bản: quân cờ và đầy đủ tất cả các luật. 
- [ ] Hiển thị nước đi hợp lệ, mũi tên chỉ hướng, animation di chuyển quân
- [ ] Nâng cấp thêm chủ đề và kiểu quân khác nhau
- [ ] Đồng hồ tính giờ, chia các chế độ (rapid 10p blitz 5p, bullet 1p,...)
- [ ] Lưu lại nước đi, *lưu lại ván đấu*
- [ ] Nhập / xuất PGN và FEN
## 2. Gameplay
### a. Với AI (offline)
- [ ] Engine AI (lấy mã nguồn Stockfish), có thể chọn độ khó khác nhau
- [ ] Có / không tính giờ
- [ ] Tuỳ chọn gợi ý / đi lại
- [ ] *AI khác nhau có phong cách chơi khác nhau*
### b. Với người
#### Offline local 
- [ ] Như chơi với AI nhưng mà thay AI bằng người
- [ ] *Phát triển chơi qua mạng LAN, mục đích là 2 máy tiện thao tác hơn (dùng trong thi đấu, tính giờ và tắt gợi ý, tắt đi lại*
#### Online
- [ ] *Yêu cầu phải tạo tài khoản (sử dụng cơ sở dữ liệu). Dùng SSMS?*
- [ ] Chơi như thi đấu
- [ ] *Hệ thống ghép trận / tính elo* (Yêu cầu số lượng người chơi phải lớn)
## 3. *Hệ thống phân tích (khó thật nên chess.com mới tính tiền)
- Sử dụng Stockfish làm engine phân tích
- [ ] Accuracy (Tính như nào?)
- [ ] Phân loại move (best / excellent / good / inaccuracy / mistake / blunder / miss)
- [ ] Đồ thị evaluation
	![[Pasted image 20261125004351.png|529]] 
## 4. Thư viện khai cuộc (chess.com cũng tính tiền)
- [ ] Tạo cơ sở dữ liệu lưu trữ khai cuộc
- [ ] Lưu trữ sâu hơn chess.com (sâu hơn 3 nước đầu tiên)
- [ ] ==🔵**Ý tưởng đột phá: tạo ra kho lưu trữ để người dùng tự phát triển các biến đi quen thuộc với bản thân. *Làm sao để có thể lưu trữ được thư viện này dưới dạng đồ thị (2D/3D), vì khai cuộc có rất nhiều biến đúng sai, có những điểm có thể trùng nhau/ giao nhau, và cần phải tìm ra những con đường chính xác ít ỏi để dẫn đến chiến thắng chính xác.***==
## 5. Các tính năng phát triển sau
- [ ] Puzzle (không có nguồn, không thể gen AI ra câu hỏi?)
- [ ] Bạn bè, cộng đồng / tournament (yêu cầu lượng người chơi lớn)
- [ ] Khoá học (Tốn nhiều thời gian lên giáo trình)