# Buổi 6 - Docker, Testing, CI

## Môi trường
- OS: Windows 11 Home Single Language
- Docker version: Docker 29.2.1, Docker Compose v5.0.2 (Docker Desktop)
- Python / Node version: Python 3.14 (venv và image `python:3.14-slim`), Node v24.21.0 trên máy, image build dùng `node:22-alpine`

## Kết quả local
- pytest backend/tests -q: 3 passed. Em thêm `pytest.ini` để pytest chỉ lấy file `test_*.py`, vì mấy file `*_test.py` cũ của Buổi 4 gọi API thật ngay khi import.
- npm test: pass 8/8
- npm run build: build được, file js khoảng 150 kB
- docker compose up --build: build được 2 image, backend lên `healthy`, frontend chạy ở 8080. Mở `/health` cổng 8000 và `/api/health` cổng 8080 đều ra `database: connected`.

## Một luồng tích hợp đã kiểm tra
- Request: gọi qua cổng 8080 (Nginx chuyển `/api` sang backend):
  - `POST /api/enrollments` với sinh viên 22000004, lớp WEB-01
  - đăng ký lại lần nữa
  - đăng ký với mã SV 99999999
  - `DELETE /api/enrollments/22000004/WEB-01`
- HTTP status: 201 → 409 (đã đăng ký) → 404 (không có SV) → 204. Log backend có đủ các request này nhưng path không còn `/api`, đúng như cấu hình `proxy_pass`. Em thử thêm lớp RACE-01 (1 chỗ): người đầu đăng ký được 201, người sau bị 409 "het cho", xong em hủy để trả lại dữ liệu.
- SQL xác nhận: trong `enrollment_events` có 2 dòng CREATED và CANCELLED của 22000004 / WEB-01. `enrollments` không còn dòng đó, `v_section_summary` của WEB-01 về lại 3 / 2 / 1 như lúc đầu.

## Debug / AI
- Lỗi gặp phải:
  - `npm run build` báo không tìm thấy `./components/StudentForm.jsx`. Lỗi do code exercise15 em đang sửa dở, không phải do Docker. Em `git stash` phần đó lại rồi mới làm Buổi 6. Lúc push thì thấy `main` trên GitHub đã có exercise15 rồi nên em rebase nhánh lên `main` mới nhất và chạy lại test.
  - Thử để `DB_HOST=127.0.0.1` trong env của container thì `/health` trả 503.
  - `database.py` báo lỗi khi thiếu biến `DB_*` nên trên CI không import được app. Em đặt biến giả trong job backend (contract test không kết nối DB).
- Bằng chứng đã xem: `docker compose ps`, `docker compose logs backend` (có dòng `GET /health 503` kèm lỗi kết nối SQLAlchemy), kiểm tra `host.docker.internal` trong container ra `192.168.65.254`. `127.0.0.1` trong container là chính container backend chứ không phải PostgreSQL trên máy, nên phải dùng `host.docker.internal`.
- Nếu dùng AI: em dùng AI để soạn Dockerfile, compose và workflow theo tài liệu, và để đọc log mấy lỗi trên. Em tự chạy lại pytest, npm test/build, compose up, gọi API bằng curl và truy vấn SQL để kiểm tra. Em cũng mở thử bên trong image để chắc là không có file `.env` nào bị copy vào.

## Pull Request / CI
- PR: https://github.com/tienanhnguyen0101nd-ctrl/coursehub-demo/pull/13 (`week06-docker-ci` → `main`)
- Reviewer: (chưa có, nhờ bạn trong nhóm review)
- CI run:
  - Lần đầu: pass cả 3 job backend, frontend, docker.
  - Bài 1: đổi `/sections` thành `/sectionz` trong test → job backend **fail** ở step "Test backend contract" (`KeyError: '/sectionz'`), job docker bị skip vì có `needs`. Khôi phục lại thì backend pass.
  - Bài 4: bỏ dòng `backend/.env.docker` khỏi `.dockerignore` → job docker **fail** ở step "Check backend image has no env/secret file", log in ra `SECRET FILE IN IMAGE: /app/backend/.env.docker`. Khôi phục lại thì pass.
  - CI chỉ chạy `compose config` và `compose build`, không chạy `up` vì database nằm trên máy em, GitHub runner không có.

## Bài tập tự thực hành
- Bài 1: thêm `test_sections_get_method_is_registered` kiểm tra `GET /sections`. Đã thử làm CI đỏ rồi khôi phục (xem ở trên).
- Bài 2: lỗi `DB_HOST=127.0.0.1`. Log có `GET /health 503`, nghĩa là request đã tới FastAPI nhưng không kết nối được DB. Sửa lại `host.docker.internal` thì `/health` 200. Không đụng tới database.
- Bài 3: làm trên repo Project nhóm (chưa làm).
- Bài 4: thêm step kiểm tra image backend không chứa `.env` / `.env.docker`. Step này bắt được lỗi sửa nhầm `.dockerignore` làm file mật khẩu DB bị copy vào image. Lỗi này pytest hay npm test đều không phát hiện được.
