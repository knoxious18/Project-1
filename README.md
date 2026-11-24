# RealChess (ChessMind)

Phần mềm chơi và phân tích cờ vua desktop viết bằng Python, tách biệt rõ ràng giữa tầng logic (`src/core`) và tầng giao diện (`src/ui`) để dễ dàng mở rộng sang AI Stockfish, phân tích ván đấu, đồ thị khai cuộc và chế độ online sau này.

## Cấu trúc dự án

- `src/core/`: Logic cờ vua thuần (không phụ thuộc UI) — quản lý bàn cờ, luật cờ đầy đủ, lịch sử nước đi, nhập/xuất FEN & PGN.
- `src/ui/`: Giao diện desktop bằng PySide6 (Qt).
- `tests/`: Unit test cho tầng logic (`pytest`).

## Cài đặt và chạy

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Chạy kiểm thử

```powershell
pytest
```
