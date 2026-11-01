
# COURSEHUB - BÁO CÁO THỰC HÀNH BUỔI 4

**Chủ đề:** Transaction, xử lý đồng thời, Database Migration và tối ưu truy vấn trong CourseHub

**Repository:** https://github.com/tienanhnguyen0101nd-ctrl/coursehub-demo

**Nhánh Git:** `week04-transaction-index`

**Phiên bản API:** `0.4.0`

---

## 1. MỤC TIÊU THỰC HÀNH

Buổi thực hành tập trung vào việc bảo đảm tính nhất quán dữ liệu khi có nhiều yêu cầu đồng thời và cải thiện hiệu năng truy vấn PostgreSQL.

Các mục tiêu chính:

- Hiểu Transaction, COMMIT, ROLLBACK và các tính chất ACID.
- Tìm hiểu Race Condition khi nhiều sinh viên đăng ký cùng một lớp học phần.
- Sử dụng SELECT FOR UPDATE để khóa dòng dữ liệu.
- Thực hiện Database Migration có phiên bản.
- Ghi lại lịch sử đăng ký và hủy đăng ký bằng bảng enrollment_events.
- Cập nhật API POST và DELETE trong FastAPI.
- Kiểm thử hai HTTP request đồng thời.
- Sinh 100.000 bản ghi để đánh giá hiệu năng.
- Sử dụng EXPLAIN (ANALYZE, BUFFERS) và Composite Index.
- Tìm hiểu nguy cơ SQL Injection và cách phòng tránh.

## 2. MÔI TRƯỜNG THỰC HÀNH

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python |
| Backend | FastAPI |
| Database | PostgreSQL |
| Công cụ quản lý CSDL | pgAdmin 4 |
| Thư viện kết nối | SQLAlchemy, psycopg |
| HTTP Client | requests |
| IDE | Visual Studio Code |
| Quản lý mã nguồn | Git và GitHub |
| API Version | 0.4.0 |
| Git Branch | week04-transaction-index |

Dự án CourseHub được phát triển tiếp từ kết quả của Buổi 3. Các chức năng cũ được giữ lại và bổ sung xử lý Transaction, Concurrency và Audit Events.

## 3. DATABASE MIGRATION

### 3.1. Mục đích

Migration giúp thay đổi cấu trúc CSDL có phiên bản mà không phải xóa và tạo lại database.

Trong Buổi 4, Migration 001 bổ sung hai bảng:

- schema_migrations: quản lý lịch sử phiên bản schema.
- enrollment_events: lưu lịch sử các sự kiện đăng ký và hủy đăng ký.

File thực hiện:

`database/migrations/001_add_enrollment_events.sql`

File rollback:

`database/migrations/001_add_enrollment_events_rollback.sql`

### 3.2. Cấu trúc bảng enrollment_events

| Cột | Kiểu dữ liệu | Chức năng |
|---|---|---|
| id | BIGINT | Khóa chính |
| student_id | VARCHAR(8) | Mã sinh viên |
| class_section_id | VARCHAR(20) | Mã lớp học phần |
| event_type | VARCHAR(20) | CREATED hoặc CANCELLED |
| source | VARCHAR(20) | Nguồn tạo sự kiện |
| dataset | VARCHAR(20) | demo hoặc performance |
| occurred_at | TIMESTAMP | Thời điểm xảy ra sự kiện |

Các ràng buộc CHECK bảo đảm event_type và dataset chỉ nhận những giá trị hợp lệ.

### 3.3. Kiểm tra Migration

Câu lệnh:

```sql
SELECT version, description, applied_at
FROM schema_migrations
ORDER BY version;

SELECT COUNT(*) AS total_events
FROM enrollment_events;
```

Kết quả đã ghi nhận:

- Migration Version: 001.
- Description: Add enrollment event audit table.
- Thời điểm áp dụng: 01/11/2026, 19:20:36.
- Migration đã được áp dụng thành công.

Tại thời điểm kiểm tra sau khi tạo dữ liệu hiệu năng, bảng enrollment_events có tổng cộng 100.003 sự kiện.

Trong đó:

- performance: 100.000 sự kiện.
- demo: 3 sự kiện.

**Nhận xét:** Việc tạo Migration giúp mở rộng cấu trúc CSDL mà vẫn duy trì dữ liệu của các buổi trước.

## 4. THỰC HÀNH RACE CONDITION

### 4.1. Mô tả tình huống

Lớp học phần RACE-01 có sức chứa:

`capacity = 1`

Hai sinh viên thực hiện đăng ký:

- Sinh viên 22000002.
- Sinh viên 22000004.

Khi không có cơ chế khóa, hai transaction có thể cùng đọc trạng thái lớp còn một chỗ và cùng thực hiện INSERT.

Điều này có thể dẫn đến số đăng ký vượt sức chứa.

### 4.2. Cách thực hiện

Sử dụng file:

`database/09_week04_race_condition_unsafe.sql`

Thực hiện với hai Query Tool độc lập trong pgAdmin:

1. Tab A đọc số lượng đăng ký và chờ bằng pg_sleep(8).
2. Tab B đọc số lượng đăng ký và thực hiện INSERT.
3. Tab A tiếp tục INSERT.
4. Kiểm tra trạng thái cuối của lớp RACE-01.

### 4.3. Kết quả cần quan sát

Nếu Race Condition được tái hiện thành công:

| class_id | capacity | enrolled | remaining |
|---|---|---|---|
| RACE-01 | 1 | 2 | -1 |

Đây là kết quả minh họa lỗi đăng ký vượt sức chứa.

**Trạng thái database đã được xác nhận sau khi triển khai xử lý an toàn:**

| class_id | capacity | enrolled | remaining |
|---|---|---|---|
| RACE-01 | 1 | 1 | 0 |

Chưa có log độc lập xác nhận thí nghiệm unsafe tạo được enrolled = 2.

### 4.4. Nhận xét

Race Condition xảy ra khi các transaction đồng thời đọc dữ liệu trước khi một transaction khác hoàn tất cập nhật.

Việc sử dụng Transaction đơn thuần chưa đủ để ngăn hai request cùng nhận định lớp còn chỗ.

Cần sử dụng cơ chế khóa dòng để kiểm soát thao tác đồng thời.

## 5. ROW LOCK - SELECT FOR UPDATE

### 5.1. Mục đích

SELECT FOR UPDATE được sử dụng để khóa dòng dữ liệu trong một transaction.

Nếu transaction khác yêu cầu khóa cùng dòng, transaction đó phải chờ đến khi khóa được giải phóng.

### 5.2. Câu lệnh sử dụng

```sql
BEGIN;

SELECT id, capacity
FROM class_sections
WHERE id = 'RACE-01'
FOR UPDATE;

SELECT pg_sleep(8);

COMMIT;
```

Một transaction khác thực hiện:

```sql
BEGIN;

SELECT id, capacity
FROM class_sections
WHERE id = 'RACE-01'
FOR UPDATE;

ROLLBACK;
```

### 5.3. Kết quả mong đợi

- Transaction A khóa dòng RACE-01.
- Transaction B yêu cầu cùng khóa.
- Transaction B chờ Transaction A COMMIT.
- Sau khi A giải phóng khóa, B tiếp tục.

Kết quả trực tiếp của thí nghiệm hai Query Tool chưa được đính kèm đầy đủ.

### 5.4. Nhận xét

Row Lock giúp các request đăng ký vào cùng lớp được xử lý lần lượt.

Cơ chế này giúp hạn chế Race Condition và bảo đảm dữ liệu đăng ký không vượt quá sức chứa khi các thao tác liên quan tuân thủ cùng quy trình khóa.

## 6. CẬP NHẬT FASTAPI VÀ TRANSACTION

### 6.1. Cập nhật API

File chỉnh sửa:

`backend/app/main.py`

Phiên bản API:

`0.4.0`

Hai endpoint được cập nhật:

- POST /enrollments
- DELETE /enrollments/{student_id}/{class_section_id}

### 6.2. Endpoint POST /enrollments

Quy trình xử lý:

1. Kiểm tra sinh viên tồn tại.
2. Khóa dòng class_sections bằng SELECT FOR UPDATE.
3. Kiểm tra sinh viên đã đăng ký lớp hay chưa.
4. Đếm số lượng đăng ký hiện tại.
5. So sánh với sức chứa.
6. INSERT vào enrollments.
7. INSERT sự kiện CREATED vào enrollment_events.
8. COMMIT transaction.

Hai thao tác INSERT được đặt trong cùng transaction.

Nếu có lỗi xảy ra trước khi transaction hoàn thành, các thay đổi chưa COMMIT sẽ được ROLLBACK.

### 6.3. Endpoint DELETE /enrollments

Quy trình:

1. Khóa dòng lớp học phần.
2. Xóa đăng ký bằng DELETE RETURNING.
3. Ghi sự kiện CANCELLED vào enrollment_events.
4. COMMIT transaction.

Việc xóa đăng ký và ghi lịch sử được thực hiện trong cùng transaction.

### 6.4. Kết quả HTTP cần kiểm tra tuần tự

| Thao tác | HTTP mong đợi |
|---|---|
| POST sinh viên 22000004 vào RACE-01 | 201 Created |
| POST sinh viên 22000002 khi lớp đầy | 409 Conflict |
| DELETE sinh viên 22000004 khỏi RACE-01 | 204 No Content |

Chưa có đủ log Swagger độc lập để xác nhận toàn bộ chuỗi kiểm thử tuần tự trên.

### 6.5. Kiểm tra Audit Events

Câu lệnh:

```sql
SELECT id, student_id, class_section_id,
       event_type, source, dataset, occurred_at
FROM enrollment_events
WHERE class_section_id = 'RACE-01'
ORDER BY id;
```

Ảnh kiểm tra đã ghi nhận các sự kiện CREATED và CANCELLED.

Các sự kiện này biểu diễn lịch sử nghiệp vụ, không phải số sinh viên đang đăng ký tại thời điểm hiện tại.

## 7. CONCURRENCY TEST

### 7.1. Mục đích

Kiểm thử hai request HTTP đăng ký gần như đồng thời vào lớp RACE-01 có sức chứa bằng 1.

### 7.2. Công cụ

File kiểm thử:

`backend/tests/week04_concurrency_test.py`

Script sử dụng:

- concurrent.futures.ThreadPoolExecutor
- threading.Barrier
- requests

Lệnh chạy:

```powershell
python backend/tests/week04_concurrency_test.py
```

### 7.3. Kết quả mong đợi

- Một request nhận HTTP 201 Created.
- Một request nhận HTTP 409 Conflict.
- Capacity = 1.
- Enrolled = 1.
- Remaining = 0.

### 7.4. Kết quả thực tế

Kết quả Terminal:

```text
22000002 201 {'message': 'Dang ky thanh cong',
'student_id': '22000002',
'class_section_id': 'RACE-01'}

22000004 409 {'detail': 'Lop hoc phan da het cho'}

PASS: chi mot request dang ky thanh cong cho lop co 1 cho.

{'class_id': 'RACE-01',
'course_code': 'INT2204',
'capacity': 1,
'enrolled': 1,
'remaining': 0}
```

Bảng tổng hợp:

| Tiêu chí | Kết quả |
|---|---|
| Sinh viên 22000002 | HTTP 201 |
| Sinh viên 22000004 | HTTP 409 |
| Capacity | 1 |
| Enrolled | 1 |
| Remaining | 0 |
| Kết quả kiểm thử | PASS |

### 7.5. Nhận xét

Hai request được gửi gần như đồng thời thông qua ThreadPoolExecutor và threading.Barrier.

Kết quả chỉ có một sinh viên đăng ký thành công. Sinh viên còn lại nhận HTTP 409 Conflict vì lớp đã hết chỗ.

Row Lock bằng SELECT FOR UPDATE giúp kiểm soát việc đăng ký đồng thời vào cùng lớp học phần.

Trong lần kiểm thử này, hệ thống không xảy ra tình trạng đăng ký vượt sức chứa.

Bài kiểm thử xác nhận quy tắc nghiệp vụ được duy trì trong kịch bản hai request đồng thời.

## 8. SINH DỮ LIỆU VÀ TỐI ƯU TRUY VẤN

### 8.1. Sinh dữ liệu lớn

File thực hiện:

`database/11_generate_performance_events.sql`

Sử dụng generate_series để tạo 100.000 bản ghi trong bảng enrollment_events.

Dữ liệu được gắn:

`dataset = 'performance'`

để phân biệt với dữ liệu lịch sử thực hành API.

Kết quả thực tế:

| Dataset | Số lượng |
|---|---|
| performance | 100000 |
| demo | 3 |
| Tổng cộng | 100003 |

### 8.2. Truy vấn kiểm tra hiệu năng

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, student_id, class_section_id,
       event_type, occurred_at
FROM enrollment_events
WHERE dataset = 'performance'
  AND student_id = '22000001'
  AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
ORDER BY occurred_at DESC
LIMIT 50;
```

Truy vấn tìm các sự kiện gần nhất của một sinh viên trong bộ dữ liệu performance.

### 8.3. Composite Index

Tên Index:

`idx_enrollment_events_dataset_student_time`

Câu lệnh:

```sql
CREATE INDEX idx_enrollment_events_dataset_student_time
ON enrollment_events
(dataset, student_id, occurred_at DESC);
```

Composite Index được xây dựng theo thứ tự:

1. dataset: lọc theo loại dữ liệu.
2. student_id: lọc theo sinh viên.
3. occurred_at DESC: hỗ trợ lọc và sắp xếp thời gian.

Index đã tồn tại trong database khi kiểm tra.

### 8.4. Kết quả so sánh

| Tiêu chí | Lần đo Seq Scan | Lần đo Index Scan |
|---|---|---|
| Scan Type | Seq Scan | Index Scan |
| Execution Time | 6.730 ms | 0.272 ms |
| Planning Time | 0.124 ms | 3.062 ms |
| Buffers thực thi | shared hit=2273 | shared hit=50, read=3 |
| Rows Removed by Filter | 99183 | Không hiển thị |
| Sort Method | Top-N heapsort | Không cần Sort riêng |

Lưu ý: Index đã tồn tại tại một thời điểm kiểm tra, do đó cần phân biệt kết quả của hai kế hoạch thực thi với bằng chứng xác nhận thời điểm tạo Index.

### 8.5. Nhận xét

Trong hai lần đo, PostgreSQL sử dụng hai kế hoạch khác nhau: Seq Scan và Index Scan.

Thời gian thực thi giảm từ 6.730 ms xuống 0.272 ms, tương đương giảm khoảng 95,96% và nhanh hơn khoảng 24,7 lần trong hai lần đo này.

Với Seq Scan, PostgreSQL quét bảng và loại bỏ 99.183 dòng không thỏa mãn điều kiện.

Với Index Scan, PostgreSQL sử dụng chỉ mục để tìm dữ liệu theo các điều kiện dataset, student_id và occurred_at.

Số Buffers phục vụ thực thi cũng giảm đáng kể trong hai lần đo.

Kết quả cho thấy Composite Index phù hợp với truy vấn kiểm thử.

Tuy nhiên, hiệu năng thực tế còn phụ thuộc vào kích thước dữ liệu, độ chọn lọc của điều kiện, thống kê PostgreSQL và trạng thái bộ nhớ đệm.

Không phải mọi truy vấn đều được PostgreSQL thực thi nhanh hơn bằng Index Scan.

## 9. AN TOÀN TRUY VẤN VÀ SQL INJECTION

### 9.1. Nguy cơ

SQL Injection có thể xảy ra khi dữ liệu người dùng được ghép trực tiếp vào chuỗi SQL.

Ký tự đặc biệt trong input có thể làm thay đổi cấu trúc truy vấn nếu không được xử lý an toàn.

### 9.2. Cách phòng tránh

CourseHub sử dụng bind parameter thông qua SQLAlchemy.

Ví dụ:

```python
parameters["keyword"] = f"%{keyword}%"

rows = connection.execute(
    text(sql),
    parameters
).mappings().all()
```

Cách này giúp tách dữ liệu đầu vào khỏi cấu trúc câu truy vấn SQL.

### 9.3. Kiểm thử

Endpoint:

`GET /courses`

Có thể kiểm tra với chuỗi chứa ký tự SQL đặc biệt theo hướng dẫn của tài liệu.

Kết quả kiểm thử thực tế chưa được cung cấp.

Yêu cầu là API xử lý input như dữ liệu, không làm thay đổi cấu trúc SQL và không làm lộ dữ liệu ngoài phạm vi truy vấn hợp lệ.

## 10. GIT VÀ GITHUB

### 10.1. Repository

https://github.com/tienanhnguyen0101nd-ctrl/coursehub-demo

### 10.2. Nhánh thực hành

`week04-transaction-index`

### 10.3. Những file được bổ sung hoặc chỉnh sửa

- backend/app/main.py
- backend/requirements.txt
- backend/tests/week04_concurrency_test.py
- database/migrations/001_add_enrollment_events.sql
- database/migrations/001_add_enrollment_events_rollback.sql
- database/08_week04_demo_setup.sql
- database/09_week04_race_condition_unsafe.sql
- database/10_week04_lock_demo.sql
- database/11_generate_performance_events.sql
- database/12_explain_and_index.sql
- docs/week04_notes.md

### 10.4. Commit và Pull Request

Commit: Đã làm

Pull Request: Đã làm

Không đưa file backend/.env, mật khẩu database hoặc file sao lưu không cần thiết lên GitHub.

## 11. MINH CHỨNG THỰC HÀNH


1. Migration 001.
2. Tổng số sự kiện.
3. Trạng thái lớp RACE-01.
4. Các sự kiện Audit.
5. Số lượng dataset.
6. Kế hoạch Seq Scan.
7. Kế hoạch Index Scan.
8. Thông báo Index đã tồn tại.

Kết quả Concurrency Test PASS đã được xác nhận bằng log Terminal.


## 12. MỐC KIỂM TRA PROJECT 1

Theo tài liệu, Project nhóm cần áp dụng kiến thức Transaction và Concurrency vào nghiệp vụ thực tế.

Cần chuẩn bị:

- ERD/schema phiên bản đầu tiên.
- Một nghiệp vụ có nhiều thao tác dữ liệu.
- Một nguy cơ Race Condition.
- Dòng hoặc tài nguyên cần khóa.
- Migration đầu tiên.
- Truy vấn cần đo hiệu năng.
- Composite Index dự kiến.
- Một bài kiểm thử Concurrency bằng hai luồng.
- Log kết quả và truy vấn xác nhận trạng thái cuối.
- Issue và Pull Request có người thực hiện, người kiểm tra.

Phần này cần được hoàn thiện trên repository Project nhóm nếu thuộc yêu cầu nộp của giảng viên.

## 13. KẾT LUẬN

Buổi thực hành giúp củng cố kiến thức về Transaction, COMMIT, ROLLBACK, Row Lock, Database Migration và tối ưu truy vấn PostgreSQL.

Migration 001 đã được áp dụng và bảng enrollment_events được sử dụng để lưu lịch sử đăng ký.

Dữ liệu thực hành đã ghi nhận 100.000 sự kiện performance.

Kiểm thử Concurrency Test đã thành công:

- Một request nhận HTTP 201.
- Một request nhận HTTP 409.
- Lớp RACE-01 có capacity = 1.
- Enrolled = 1.
- Remaining = 0.

Hai lần đo EXPLAIN ghi nhận thời gian thực thi 6.730 ms và 0.272 ms đối với hai kế hoạch Seq Scan và Index Scan.

Kết quả cho thấy việc kết hợp Transaction, SELECT FOR UPDATE và Composite Index có thể giúp bảo đảm tính nhất quán và nâng cao hiệu năng đối với nghiệp vụ đăng ký học phần.

Các kết quả đã được xác nhận cần tiếp tục bổ sung minh chứng còn thiếu và hoàn thành Pull Request trước khi nộp.
