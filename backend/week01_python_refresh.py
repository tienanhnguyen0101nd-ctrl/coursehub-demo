students = [
    {"id": "22000001", "name": "Nguyen Minh Anh", "major": "KHDL"},
    {"id": "22000002", "name": "Tran Duc Long", "major": "KHDL"},
]

courses = [
    {
        "code": "INT2204",
        "name": "Co so du lieu Web va he thong thong tin",
        "capacity": 3,
        "enrolled": 2,
    },
    {
        "code": "INT2205",
        "name": "Khai pha du lieu",
        "capacity": 2,
        "enrolled": 2,
    },
]

enrollments = [
    {"student_id": "22000001", "course_code": "INT2204"}
]

# Code duyệt dữ liệu
for course in courses:
    remaining = course["capacity"] - course["enrolled"]
    print(course["code"], "- con", remaining, "cho")


def find_course(course_code):
    for course in courses:
        if course["code"] == course_code:
            return course
    return None

print(find_course("INT2204"))


def can_enroll(student_id, course_code):
    course = find_course(course_code)
    if course is None:
        return False, "Hoc phan khong ton tai"
    if course["enrolled"] >= course["capacity"]:
        return False, "Lop da du so luong"

    duplicated = any(
        item["student_id"] == student_id and item["course_code"] == course_code
        for item in enrollments
    )
    if duplicated:
        return False, "Sinh vien da dang ky hoc phan nay"

    return True, "Co the dang ky"


print(can_enroll("22000002", "INT2204"))

try:
    limit = int(input("Nhap so luong hoc phan muon hien thi: "))
    print(courses[:limit])
except ValueError:
    print("So luong phai la so nguyen")


def search_courses(keyword):
    normalized = keyword.strip().lower()
    results = []

    for course in courses:
        code = course["code"].lower()
        name = course["name"].lower()
        if normalized in code or normalized in name:
            results.append(course)

    return results


print(search_courses("web"))


def enroll_student(student_id, course_code):
    # 1. Kiểm tra tính hợp lệ
    is_valid, message = can_enroll(student_id, course_code)

    # 2. Xử lý nếu không hợp lệ
    if not is_valid:
        return f"Dang ky that bai: {message}"

    # 3. Xử lý nếu hợp lệ: Thêm vào danh sách và cập nhật sĩ số
    enrollments.append({"student_id": student_id, "course_code": course_code})

    course = find_course(course_code)
    course["enrolled"] += 1

    return f"Dang ky thanh cong hoc phan {course_code} cho sinh vien {student_id}!"


# --- CHẠY THỬ CÁC TÌNH HUỐNG (TEST CASES) ---
print("\n--- KET QUA TEST DANG KY ---")
# 1. Đăng ký thành công (INT2204 đang có 2/3 slot)
print(enroll_student("22000002", "INT2204"))

# 2. Đăng ký thất bại (Lớp đã đầy vì sinh viên trên vừa chiếm slot cuối)
print(enroll_student("22000003", "INT2204"))

# 3. Đăng ký thất bại (Sinh viên 22000001 đã đăng ký từ trước)
print(enroll_student("22000001", "INT2204"))

# 4. Đăng ký thất bại (Mã học phần sai)
print(enroll_student("22000002", "INT9999"))
