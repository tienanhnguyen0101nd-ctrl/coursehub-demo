
# BÀI TẬP XII - BÀI 3: TỐI ƯU TRUY VẤN BẰNG COMPOSITE INDEX

**Dự án:** CourseHub  
**Cơ sở dữ liệu:** PostgreSQL  
**Bảng thực hiện:** `enrollment_events`  
**File SQL:** `database/13_exercise12_second_index.sql`  
**Index:** `idx_enrollment_events_class_type_time`

---

## 1. Mục tiêu

- Thiết kế Composite Index thứ hai theo nghiệp vụ.
- Đo hiệu năng truy vấn trước và sau khi tạo Index.
- Sử dụng `EXPLAIN (ANALYZE, BUFFERS)`.
- Phân tích thứ tự các cột trong Index.
- Đánh giá hiệu quả và bảo đảm dữ liệu không bị thay đổi.

## 2. Mô tả nghiệp vụ

Trong hệ thống CourseHub, bảng `enrollment_events` lưu lịch sử đăng ký và hủy đăng ký học phần.

Người quản lý cần tra cứu các sự kiện đăng ký của một lớp học phần theo loại sự kiện và khoảng thời gian.

Truy vấn được lựa chọn:

- Dataset: `performance`
- Lớp học phần: `WEB-02`
- Loại sự kiện: `CREATED`
- Thời gian: từ ngày `2025-12-01`
- Sắp xếp: `occurred_at DESC, id DESC`
- Số dòng tối đa: 50

## 3. Truy vấn kiểm thử

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    id,
    class_section_id,
    event_type,
    occurred_at
FROM enrollment_events
WHERE dataset = 'performance'
  AND class_section_id = 'WEB-02'
  AND event_type = 'CREATED'
  AND occurred_at >= TIMESTAMP '2025-12-01 00:00:00'
ORDER BY occurred_at DESC, id DESC
LIMIT 50;
```

Sử dụng cùng truy vấn để đo trước và sau khi tạo Index.

## 4. Kết quả trước khi tạo Index

| Chỉ số | Kết quả |
|---|---|
| Scan Type | Seq Scan |
| Execution Time | 20.561 ms |
| Planning Time | 4.266 ms |
| Buffers thực thi | shared hit = 2273 |
| Rows Removed by Filter | 98295 |
| Sort Method | Top-N heapsort |
| Sort Memory | 30 kB |
| Số dòng trả về | 50 |

### Nhận xét

PostgreSQL sử dụng `Seq Scan` để quét bảng `enrollment_events`.

Quá trình quét loại bỏ 98.295 dòng không thỏa mãn điều kiện, sau đó sử dụng `Top-N heapsort` để sắp xếp và lấy 50 dòng đầu tiên.

Thời gian thực thi là **20.561 ms**.

## 5. Thiết kế Composite Index

Câu lệnh:

```sql
CREATE INDEX IF NOT EXISTS
    idx_enrollment_events_class_type_time
ON enrollment_events
(
    dataset,
    class_section_id,
    event_type,
    occurred_at DESC,
    id DESC
);

ANALYZE enrollment_events;
```

### Giải thích thứ tự các cột

| Cột | Vai trò |
|---|---|
| `dataset` | Lọc nhóm dữ liệu |
| `class_section_id` | Lọc lớp học phần |
| `event_type` | Lọc loại sự kiện |
| `occurred_at DESC` | Lọc thời gian, sắp xếp mới nhất |
| `id DESC` | Ổn định thứ tự khi trùng thời gian |

Ba cột đầu dùng cho điều kiện so sánh bằng.

Hai cột cuối hỗ trợ lọc theo thời gian và sắp xếp giảm dần.

Index được thiết kế cho truy vấn cụ thể, không tạo Index trên mọi cột.

## 6. Kết quả sau khi tạo Index

| Chỉ số | Kết quả |
|---|---|
| Scan Type | Index Only Scan |
| Index sử dụng | idx_enrollment_events_class_type_time |
| Execution Time | 0.462 ms |
| Planning Time | 3.411 ms |
| Buffers thực thi | shared hit = 1, read = 4 |
| Heap Fetches | 0 |
| Số dòng trả về | 50 |
| Sort Method | Không cần Sort riêng |

### Nhận xét

PostgreSQL sử dụng `Index Only Scan` thông qua Composite Index.

Các điều kiện lọc được xử lý bằng `Index Cond`.

Trong lần đo này, `Heap Fetches = 0`, nghĩa là PostgreSQL không cần lấy thêm dữ liệu từ bảng heap.

Index cũng hỗ trợ thứ tự `ORDER BY`, nên không cần thực hiện bước Sort riêng.

Thời gian thực thi còn **0.462 ms**.

## 7. So sánh trước và sau Index

| Tiêu chí | Trước Index | Sau Index |
|---|---|---|
| Scan Type | Seq Scan | Index Only Scan |
| Execution Time | 20.561 ms | 0.462 ms |
| Planning Time | 4.266 ms | 3.411 ms |
| Buffers thực thi | shared hit=2273 | shared hit=1, read=4 |
| Rows Removed by Filter | 98295 | Không hiển thị |
| Sort | Top-N heapsort | Không cần Sort riêng |
| Heap Fetches | Không áp dụng | 0 |
| Số dòng trả về | 50 | 50 |

### Tỷ lệ cải thiện

Công thức:

**Tỷ lệ giảm thời gian:**

`(20.561 - 0.462) / 20.561 × 100% ≈ 97.75%`

**Hệ số tăng tốc:**

`20.561 / 0.462 ≈ 44.5 lần`

Như vậy, trong hai lần đo, thời gian thực thi giảm khoảng **97,75%**, tương đương nhanh hơn khoảng **44,5 lần**.

## 8. Giải thích hiệu quả

Trước khi có Index chuyên biệt, PostgreSQL phải thực hiện `Seq Scan` và kiểm tra nhiều dòng dữ liệu.

Sau khi tạo Composite Index, PostgreSQL có thể tìm dữ liệu trực tiếp theo các điều kiện lọc.

Ngoài ra:

- Giảm số khối dữ liệu phải truy cập.
- Không cần bước Sort riêng.
- Sử dụng `Index Only Scan`.
- `Heap Fetches = 0` trong lần đo sau Index.

Điều này giúp giảm đáng kể thời gian thực thi.

Tuy nhiên, hiệu năng còn phụ thuộc vào kích thước dữ liệu, độ chọn lọc, thống kê và trạng thái bộ nhớ đệm PostgreSQL.

## 9. Kiểm thử và Rollback

### 9.1. Ca đúng

Truy vấn trả về 50 bản ghi, sử dụng `Index Only Scan` sau khi tạo Index.

### 9.2. Ca không có dữ liệu

Kiểm thử truy vấn với lớp không có dữ liệu phù hợp trong dataset `performance`.

Kết quả mong đợi là 0 dòng.

### 9.3. Rollback Index

File:

`database/13_exercise12_second_index_rollback.sql`

Nội dung:

```sql
DROP INDEX IF EXISTS
    idx_enrollment_events_class_type_time;
```

Rollback chỉ xóa Index, không xóa các bản ghi của bảng `enrollment_events`.

Chưa có minh chứng riêng về việc thực thi rollback Index.


## 10. Kết luận

Bài thực hành đã thiết kế và đánh giá Composite Index thứ hai trên bảng `enrollment_events`.

Kết quả thực tế:

- Trước Index: `Seq Scan`, **20.561 ms**.
- Sau Index: `Index Only Scan`, **0.462 ms**.
- Thời gian thực thi giảm khoảng **97,75%**.
- Hệ số tăng tốc khoảng **44,5 lần**.
- `Heap Fetches = 0` trong lần đo sau Index.

Kết quả cho thấy việc thiết kế Composite Index theo điều kiện lọc và sắp xếp của nghiệp vụ giúp tối ưu hiệu quả truy vấn PostgreSQL.
