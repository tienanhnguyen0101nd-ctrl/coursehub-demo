-- CHI DUNG TREN DATABASE HOC TAP. Reset bang 08_week04_demo_setup.sql truoc va sau.
-- Tab A: chay khoi nay truoc
BEGIN;
SELECT cs.id, cs.capacity, COUNT(e.student_id) AS enrolled
FROM class_sections AS cs LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
WHERE cs.id = 'RACE-01' GROUP BY cs.id, cs.capacity;
SELECT pg_sleep(8);
INSERT INTO enrollments (student_id, class_section_id) VALUES ('22000002', 'RACE-01');
COMMIT;

-- Tab B: chi chay phan duoi trong Query Tool KHAC khi Tab A dang sleep.
-- KHONG chay toan bo file trong cung mot tab.
BEGIN;
SELECT cs.id, cs.capacity, COUNT(e.student_id) AS enrolled
FROM class_sections AS cs LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
WHERE cs.id = 'RACE-01' GROUP BY cs.id, cs.capacity;
INSERT INTO enrollments (student_id, class_section_id) VALUES ('22000004', 'RACE-01');
COMMIT;

-- Kiem tra SAU KHI ca hai tab hoan tat (chay rieng):
SELECT cs.id, cs.capacity, COUNT(e.student_id) AS enrolled,
       cs.capacity - COUNT(e.student_id) AS remaining
FROM class_sections AS cs LEFT JOIN enrollments AS e ON e.class_section_id = cs.id
WHERE cs.id = 'RACE-01' GROUP BY cs.id, cs.capacity;
SELECT student_id, class_section_id FROM enrollments
WHERE class_section_id = 'RACE-01' ORDER BY student_id;
