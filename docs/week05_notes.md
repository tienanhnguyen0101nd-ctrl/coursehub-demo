# COURSEHUB - BÁO CÁO THỰC HÀNH BUỔI 5

**Chủ đề:** Xây dựng Frontend với React – kết nối giao diện CourseHub với FastAPI

**Repository:** https://github.com/tienanhnguyen0101nd-ctrl/coursehub-demo

**Nhánh Git:** `week05-frontend-react` (tạo từ nhánh đã chứa mã Buổi 4 và các bài XII-1…XII-4, giữ nguyên row lock và `enrollment_events`)

**Phiên bản:** Backend `0.4.0` (chỉ bổ sung CORS) · Frontend `0.5.0`

---

## 1. Mục tiêu

- Bổ sung thư mục `frontend/` (React 18.2.0 + Vite 7.1.7) vào repository CourseHub hiện có.
- Cấu hình CORS ở Backend để trình duyệt tại cổng 5173 gọi được API cổng 8000.
- Hiển thị danh sách lớp, đăng ký (POST), hủy đăng ký (DELETE); xử lý trạng thái đang tải / rỗng / thành công / lỗi.
- Đối chiếu kết quả với PostgreSQL bằng `database/13_week05_verify.sql`.

## 2. Thay đổi Backend

File: `backend/app/main.py`

- Thêm `from fastapi.middleware.cors import CORSMiddleware`.
- Ngay sau `app = FastAPI(...)` thêm `app.add_middleware(CORSMiddleware, ...)` với:
  - `allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]`
  - `allow_credentials = False`
  - `allow_methods = ["GET", "POST", "DELETE"]`
  - `allow_headers = ["Content-Type"]`
- Không thay đổi nghiệp vụ: POST vẫn `SELECT ... FOR UPDATE` và ghi `enrollment_events` trong cùng transaction; phiên bản giữ `0.4.0`.

## 3. Cấu trúc Frontend

```text
frontend/
├── package.json
├── package-lock.json
├── vite.config.js
├── index.html
├── .env.example          # VITE_API_BASE_URL=http://127.0.0.1:8000
├── .env.local            # tạo tại máy, không commit
├── tests/api.test.mjs    # 8 tình huống HTTP giả lập cho api.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── api.js
    ├── styles.css
    └── components/
        ├── Notice.jsx
        ├── SectionTable.jsx
        └── EnrollmentList.jsx
```

| Thao tác trên trang | API sử dụng |
|---|---|
| Tải tên học phần và danh sách lớp | `GET /courses`, `GET /sections` |
| Xem các lớp của một sinh viên | `GET /students/{student_id}/enrollments` |
| Đăng ký lớp | `POST /enrollments` |
| Hủy đăng ký | `DELETE /enrollments/{student_id}/{class_section_id}` |

`.gitignore` bổ sung: `.env.local`, `node_modules/`, `dist/`.

## 4. Cách chạy

| Thành phần | Thư mục | Lệnh |
|---|---|---|
| Backend | `coursehub-demo` | `python -m uvicorn backend.app.main:app --reload` |
| Frontend | `coursehub-demo/frontend` | `npm install` (lần đầu) rồi `npm run dev` |
| Kiểm thử api.js | `coursehub-demo/frontend` | `npm test` |
| Build | `coursehub-demo/frontend` | `npm run build` |

Mở http://127.0.0.1:5173/ (không double-click `index.html`).

## 5. Bản phác giao diện (wireframe)

Link Figma: _(dán link thiết kế "CourseHub – Buổi 5" tại đây)_

Bố cục: tiêu đề → vùng **1. Chọn sinh viên** (ô mã SV, nút Xem đăng ký, Tải lại dữ liệu) → hai cột: **2. Danh sách lớp học phần** (tìm kiếm, lọc còn chỗ, bảng lớp với nút Đăng ký / Đã đăng ký / Hết chỗ) và **3. Lớp đã đăng ký** (nút Hủy đăng ký). Có trạng thái đăng ký thành công và lớp hết chỗ (RACE-01).

## 6. Kết quả kiểm thử

### 6.1. Kiểm thử tự động

```text
> npm test
✔ 1. GET 200 tra ve JSON va goi dung URL mac dinh
✔ 2. POST 201 gui JSON body va Content-Type
✔ 3. DELETE 204 tra null, khong doc JSON
✔ 4. 404 nem loi kem status va detail
✔ 5. 409 nem loi xung dot
✔ 6. 422 ghep danh sach detail thanh chuoi
✔ 7. Phan hoi khong phai JSON bao loi ro rang
✔ 8. Loi mang bao kiem tra Backend/CORS; AbortError giu nguyen
ℹ tests 8 · pass 8 · fail 0

> npm run build
vite v7.1.7 building for production...
✓ 31 modules transformed.
✓ built
```

Các test này chỉ kiểm tra `api.js` với `fetch` giả lập; không thay thế kiểm thử PostgreSQL hoặc test concurrency của Buổi 4.

### 6.2. Luồng thực hành trên trình duyệt (điền kết quả thực tế)

| Trường hợp | Kết quả mong đợi | Kết quả thực tế |
|---|---|---|
| 22000004 đăng ký WEB-01 | 201, WEB-01 hiện "Đã đăng ký", remaining = 0 | |
| Reload trang | Đăng ký vẫn còn (đã ghi CSDL) | |
| Hủy WEB-01 | 204, WEB-01 trở lại enrolled = 2, remaining = 1 | |
| Mã 99999999 | HTTP 404, không hiện nút ghi trên dữ liệu cũ | |
| Mã ngắn hơn 8 chữ số | Form báo lỗi trước khi đổi sinh viên | |
| Tạm dừng Backend rồi tải lại | Hiện lỗi kết nối, không báo thành công giả | |
| Hai cửa sổ cùng lấy suất cuối RACE-01 | A nhận 201, B nhận 409 rồi hiển thị "Hết chỗ" | |
| DevTools Network – POST payload | `{"student_id": "22000004", "class_section_id": "WEB-01"}` | |
| Màn hình 390 px | Một cột, bảng cuộn ngang trong vùng bảng | |

### 6.3. Đối chiếu SQL

Chạy từng truy vấn trong `database/13_week05_verify.sql` bằng Query Tool (database `coursehub`):

- Sau POST 201: có cặp `22000004 / WEB-01` trong `enrollments`, `remaining = 0`, thêm một sự kiện `CREATED` (dataset = demo).
- Sau DELETE 204: cặp đăng ký không còn, `remaining = 1`, thêm sự kiện `CANCELLED`; sự kiện `CREATED` cũ vẫn giữ.

## 7. Lưu ý an toàn

- `backend/.env` (mật khẩu CSDL) và `frontend/.env.local` không được commit.
- Biến `VITE_*` chỉ chứa URL API công khai, không đặt mật khẩu/token.
- Ô mã sinh viên chỉ chọn dữ liệu demo, không phải đăng nhập.
- Không dùng `mode: "no-cors"`; mọi lỗi 404/409 được hiển thị đúng như Backend trả về.
- Sau mỗi thao tác ghi (thành công hay lỗi), giao diện đọc lại dữ liệu từ API; không tự cộng/trừ số chỗ.

