# COURSEHUB - BÁO CÁO THỰC HÀNH BUỔI 5

**Chủ đề:** Xây dựng Frontend với React – kết nối giao diện CourseHub với FastAPI

**Repository:** https://github.com/tienanhnguyen0101nd-ctrl/coursehub-demo

**Nhánh Git:** `week05-frontend-react`

**Phiên bản:** Backend `0.4.0` (chỉ bổ sung CORS) · Frontend `0.5.0`

---

## 1. Mục tiêu

- Bổ sung thư mục `frontend/` (React `18.2.0` + Vite `7.1.7`) vào repository CourseHub hiện có.
- Cấu hình CORS ở Backend để trình duyệt tại cổng `5173` gọi được API cổng `8000`.
- Hiển thị danh sách lớp, đăng ký (`POST`), hủy đăng ký (`DELETE`); xử lý trạng thái đang tải / rỗng / thành công / lỗi.
- Đối chiếu kết quả với PostgreSQL bằng `database/13_week05_verify.sql`.

## 2. Kiểm tra điều kiện trước bài (Mục II)

- Node.js: `v24.21.0` (`>= 22.12.0`).
- `schema_migrations`: đã có phiên bản `001`.
- Trạng thái ban đầu trong `v_section_summary`:
  - `WEB-01`: `capacity = 3`, `enrolled = 2`, `remaining = 1`
  - `RACE-01`: `capacity = 1`
  - Sinh viên `22000004` chưa đăng ký `WEB-01`.

## 3. Thay đổi Backend (Mục III)

File: `backend/app/main.py`

- Thêm `from fastapi.middleware.cors import CORSMiddleware`.
- Ngay sau `app = FastAPI(...)` thêm `app.add_middleware(CORSMiddleware, ...)` với:
  - `allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]`
  - `allow_credentials = False`
  - `allow_methods = ["GET", "POST", "DELETE"]`
  - `allow_headers = ["Content-Type"]`
- Không thay đổi nghiệp vụ: `POST /enrollments` vẫn giữ `SELECT ... FOR UPDATE` và ghi `enrollment_events` trong cùng transaction; phiên bản giữ `0.4.0`.

## 4. Cấu trúc Frontend (Mục IV, VII, VIII, IX)

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

## 5. Cách chạy

| Thành phần | Thư mục | Lệnh |
|---|---|---|
| Backend | `coursehub-demo` | `python -m uvicorn backend.app.main:app --reload` |
| Frontend | `coursehub-demo/frontend` | `npm install` (lần đầu) rồi `npm run dev` |
| Kiểm thử `api.js` | `coursehub-demo/frontend` | `npm test` |
| Build | `coursehub-demo/frontend` | `npm run build` |

Mở `http://127.0.0.1:5173/` (không double-click `index.html`).

## 6. Bản phác giao diện (Mục V)

Bố cục bám đúng dữ liệu API:
- Tiêu đề **CourseHub — Tra cứu và đăng ký lớp học phần** (`React → FastAPI → PostgreSQL`).
- Vùng **1. Chọn sinh viên**: ô nhập mã sinh viên 8 chữ số, nút **Xem đăng ký**, nút **Tải lại dữ liệu**.
- Hai cột trong `.workspace`:
  - **2. Danh sách lớp học phần**: ô tìm lớp/học phần, checkbox **Chỉ hiện lớp còn chỗ**, bảng lớp (`class_id`, `course_name`, `course_code`, `capacity`, `enrolled`, `remaining`, nút **Đăng ký** / **Đã đăng ký** / **Hết chỗ**).
  - **3. Lớp đã đăng ký**: danh sách lớp của sinh viên đang xem kèm nút **Hủy đăng ký** (hoặc thông báo rỗng).
- Vùng thông báo `Notice`: đang tải, thành công (`201`/`204`), lỗi (`404`/`409`/lỗi kết nối).

## 7. Kết quả thực hành & đối chiếu PostgreSQL (Mục X, XI, XII, XIV)

### 7.1. Kiểm thử `api.js` và tạo bản build (`npm test` & `npm run build`)

```text
> coursehub-frontend@0.5.0 test
> node --test tests/api.test.mjs

✔ 1. GET 200 tra ve JSON va goi dung URL mac dinh
✔ 2. POST 201 gui JSON body va Content-Type
✔ 3. DELETE 204 tra null, khong doc JSON
✔ 4. 404 nem loi kem status va detail
✔ 5. 409 nem loi xung dot
✔ 6. 422 ghep danh sach detail thanh chuoi
✔ 7. Phan hoi khong phai JSON bao loi ro rang
✔ 8. Loi mang bao kiem tra Backend/CORS; AbortError giu nguyen
ℹ tests 8 · pass 8 · fail 0

> coursehub-frontend@0.5.0 build
> vite build
vite v7.1.7 building for production...
✓ 31 modules transformed.
✓ built
```

### 7.2. Đối chiếu SQL với `database/13_week05_verify.sql`

1. **Sau khi `22000004` đăng ký `WEB-01` (`POST /enrollments` → `201 Created`):**
   - Payload gửi: `{"student_id": "22000004", "class_section_id": "WEB-01"}`
   - `v_section_summary`: `('WEB-01', capacity=3, enrolled=3, remaining=0)`
   - `enrollments` của `22000004`: `[('22000004', 'WEB-01')]`
   - `enrollment_events` (`dataset = 'demo'`): ghi nhận bản ghi mới `id = 200007`, `event_type = 'CREATED'`, `occurred_at = 2026-11-10 13:40:00.218766`.

2. **Sau khi hủy đăng ký `WEB-01` (`DELETE /enrollments/22000004/WEB-01` → `204 No Content`):**
   - `v_section_summary`: `('WEB-01', capacity=3, enrolled=2, remaining=1)`
   - `enrollments` của `22000004`: `[]` (rỗng)
   - `enrollment_events` (`dataset = 'demo'`): thêm bản ghi `id = 200008`, `event_type = 'CANCELLED'`, `occurred_at = 2026-11-10 13:40:00.262047` (giữ nguyên sự kiện `CREATED` `id = 200007` trước đó).

3. **Các trường hợp biên và xung đột suất cuối `RACE-01`:**

| Trường hợp | Kết quả thực tế |
|---|---|
| Sinh viên `22000004` chưa đăng ký lớp | Hiển thị `"Sinh viên chưa đăng ký lớp nào."` (không phải lỗi 404) |
| Mã sinh viên `99999999` | `HTTP 404: Khong tim thay sinh vien`; ẩn vùng bảng/nút ghi trên dữ liệu cũ |
| Mã ngắn hơn 8 chữ số | Form chặn trước khi gọi API và báo `"Mã demo phải gồm 8 chữ số."` |
| Hai cửa sổ cùng lấy suất cuối `RACE-01` (làm sạch về `enrolled = 0`, `remaining = 1`) | Cửa sổ A (`22000002`) nhận `201 Created`; Cửa sổ B (`22000004`) bấm nút cũ nhận `HTTP 409: Lop hoc phan da het cho`, tự tải lại dữ liệu và đổi nút thành `Hết chỗ`; sau khi thử đã hủy đăng ký để trả `RACE-01` về `enrolled = 0, remaining = 1` |
| Màn hình nhỏ `390 px` | Media query `@media (max-width: 900px)` và `560px` xếp thành 1 cột; bảng cuộn ngang trong `.table-scroll` |

## 8. Lưu ý an toàn

- `backend/.env` và `frontend/.env.local` đã được `.gitignore` chặn, kiểm tra bằng `git check-ignore -v`.
- Không đặt mật khẩu CSDL hay khóa bí mật vào biến `VITE_*`.
- Sau cả thành công và lỗi của thao tác ghi, giao diện đều tăng `refresh` để đọc lại dữ liệu từ API và PostgreSQL.
