
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from backend.app.database import engine

STUDENT_ID = "22000004"
SECTION_ID = "RACE-01"


def enrollment_count(connection):
    return connection.execute(
        text("""
            SELECT COUNT(*)
            FROM enrollments
            WHERE student_id = :student_id
              AND class_section_id = :section_id
        """),
        {
            "student_id": STUDENT_ID,
            "section_id": SECTION_ID,
        },
    ).scalar_one()


def main():
    # Kiểm tra dữ liệu đầu vào trước khi thử.
    with engine.connect() as connection:
        before = enrollment_count(connection)

    print("Before:", before)

    if before != 0:
        raise RuntimeError(
            "Sinh vien da dang ky RACE-01. "
            "Hay chon sinh vien chua dang ky "
            "hoac reset du lieu demo truoc."
        )

    try:
        with engine.begin() as connection:
            # Khóa lớp để thống nhất với luồng
            # đăng ký chính của CourseHub.
            connection.execute(
                text("""
                    SELECT id
                    FROM class_sections
                    WHERE id = :section_id
                    FOR UPDATE
                """),
                {"section_id": SECTION_ID},
            ).one()

            # INSERT bảng thứ nhất.
            connection.execute(
                text("""
                    INSERT INTO enrollments
                        (student_id, class_section_id)
                    VALUES (:student_id, :section_id)
                """),
                {
                    "student_id": STUDENT_ID,
                    "section_id": SECTION_ID,
                },
            )

            print(
                "Trong transaction, enrollment_count:",
                enrollment_count(connection),
            )

            # INSERT bảng thứ hai cố tình sai CHECK.
            connection.execute(
                text("""
                    INSERT INTO enrollment_events
                        (student_id, class_section_id,
                         event_type, source, dataset)
                    VALUES
                        (:student_id, :section_id,
                         'INVALID', 'test', 'demo')
                """),
                {
                    "student_id": STUDENT_ID,
                    "section_id": SECTION_ID,
                },
            )

    except IntegrityError:
        print(
            "EXPECTED ERROR: "
            "event_type INVALID vi pham CHECK constraint"
        )

    else:
        raise AssertionError(
            "Khong phat sinh loi nhu mong doi"
        )

    # Đây là lần kiểm tra bằng kết nối mới.
    with engine.connect() as connection:
        after = enrollment_count(connection)

        invalid_events = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM enrollment_events
                WHERE student_id = :student_id
                  AND class_section_id = :section_id
                  AND event_type = 'INVALID'
            """),
            {
                "student_id": STUDENT_ID,
                "section_id": SECTION_ID,
            },
        ).scalar_one()

    print("After rollback:", after)
    print("Invalid events:", invalid_events)

    assert before == after == 0
    assert invalid_events == 0

    print("PASS: Rollback ca hai bang thanh cong")


if __name__ == "__main__":
    main()
