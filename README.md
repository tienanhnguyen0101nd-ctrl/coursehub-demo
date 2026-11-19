# CourseHub demo

FastAPI + React (Vite) + PostgreSQL. Ghi chú từng buổi nằm trong `docs/`.

## Chạy kiểu phát triển (Buổi 5)

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload      # http://127.0.0.1:8000/docs

cd frontend
npm ci
npm run dev                                          # http://127.0.0.1:5173
```

## Chạy bằng Docker Compose (Buổi 6)

PostgreSQL `coursehub` vẫn chạy trên máy host; Compose chỉ chạy `frontend` (Nginx) và `backend` (FastAPI).

```powershell
# 1. Tạo env cho container từ .env local (KHÔNG commit file này)
Copy-Item backend/.env backend/.env.docker
#    sửa DB_HOST=host.docker.internal (xem backend/.env.docker.example)

# 2. Build và chạy
docker compose config --quiet
docker compose up --build

# 3. Mở
#    http://127.0.0.1:8080        giao diện (Nginx, /api -> backend:8000)
#    http://127.0.0.1:8000/docs   FastAPI trực tiếp

# 4. Dừng (không xóa image, không đụng PostgreSQL trên host)
docker compose down
```

## Kiểm thử

```powershell
python -m pip install -r backend/requirements-dev.txt
pytest backend/tests -q          # contract OpenAPI, không cần DB

cd frontend
npm test
npm run build
```

GitHub Actions (`.github/workflows/ci.yml`) chạy job `backend`, `frontend` song song, sau đó `docker` (compose config + build) khi push lên `main` hoặc mở Pull Request.
