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
        "enrolled": 2,  # Lớp này đã đầy sẵn
    },
]

enrollments = [
    {"student_id": "22000001", "course_code": "INT2204"}
]

for course in courses:
    remaining = course["capacity"] - course["enrolled"]
    print(course["code"], "- con", remaining, "cho")


def find_course(course_code):
    for course in courses:
        if course["code"] == course_code:
            return course
    return None


print(find_course("INT2204"))


# Hàm mới viết thêm để check sinh viên theo yêu cầu đề
def check_student_exists(student_id):
    for student in students:
        if student["id"] == student_id:
            return True
    return False


def can_enroll(student_id, course_code):
    # Kiem tra sinh vien ton tai chua
    if not check_student_exists(student_id):
        return False, "Sinh vien khong ton tai"

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
    status, msg = can_enroll(student_id, course_code)

    if not status:
        return f"Dang ky that bai: {msg}"

    # Ghi nhan dang ky va tang si so
    enrollments.append({"student_id": student_id, "course_code": course_code})

    course = find_course(course_code)
    course["enrolled"] += 1

    return f"Dang ky thanh cong! Sinh vien {student_id} vao lop {course_code}"


print("\n--- TEST 5 TINH HUONG ---")
# 1. Thành công (INT2204 còn trống 1 chỗ)
print("1.", enroll_student("22000002", "INT2204"))

# 2. Trùng lặp (22000001 đã đăng ký INT2204 từ đầu)
print("2.", enroll_student("22000001", "INT2204"))

# 3. Lớp đầy (INT2205 có capacity=2, enrolled=2)
print("3.", enroll_student("22000001", "INT2205"))

# 4. Mã học phần không tồn tại
print("4.", enroll_student("22000001", "INT9999"))

# 5. Mã sinh viên không tồn tại
print("5.", enroll_student("99999999", "INT2204"))