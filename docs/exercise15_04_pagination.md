# BÀI TẬP XV-4: TÌM KIẾM VÀ PHÂN TRANG PHÍA SERVER (`GET /sections`)

## 1. Mục tiêu

Mở rộng tìm kiếm và phân trang phía server (PostgreSQL) cho danh sách lớp học phần `GET /sections`, thay vì tải toàn bộ dữ liệu về trình duyệt rồi lọc mảng bằng JavaScript.

## 2. Đặc tả tham số truy vấn (Query Parameters)

Endpoint: `GET /sections`

| Tham số | Kiểu | Mặc định | Ràng buộc / Giới hạn | Ý nghĩa |
|---|---|---|---|---|
| `q` | `string \| null` | `null` | `min_length = 1`, không được chỉ chứa khoảng trắng | Tìm theo `class_id`, `course_code` hoặc tên học phần `courses.name` (không phân biệt hoa/thường, dùng bind parameter `:keyword`) |
| `course_code` | `string \| null` | `null` | `min_length = 1` | Lọc chính xác theo mã học phần (`INT2204`, `INT2205`, `INT2206`) |
| `available_only` | `boolean` | `false` | `true` / `false` | Chỉ lấy các lớp còn chỗ (`remaining > 0`) |
| `skip` | `integer` | `0` | `skip >= 0` (`ge=0`) | Vị trí bắt đầu (`OFFSET :skip`) |
| `limit` | `integer` | `10` | `1 <= limit <= 100` (`ge=1, le=100`) | Giới hạn kích thước trang tối đa `100` bản ghi/lần (`LIMIT :limit`) |

## 3. Thứ tự sắp xếp ổn định (Deterministic Ordering)

Truy vấn SQL luôn kết thúc bằng:

```sql
ORDER BY v.class_id ASC OFFSET :skip LIMIT :limit
```

- `v.class_id` là khóa chính (`class_sections.id` — duy nhất cho mỗi lớp học phần).
- Sắp xếp theo khóa duy nhất `v.class_id ASC` bảo đảm thứ tự ổn định tuyệt đối giữa các trang (`skip = 0, limit = 2`, sau đó `skip = 2, limit = 2` không bị trùng hoặc bỏ sót dòng).
- Mọi giá trị đầu vào (`:keyword`, `:course_code`, `:skip`, `:limit`) đều truyền qua bind parameters của SQLAlchemy.
