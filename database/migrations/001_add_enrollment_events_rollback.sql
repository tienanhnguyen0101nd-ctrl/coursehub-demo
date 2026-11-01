-- KHONG CHAY trong bai thuc hanh binh thuong: xoa toan bo audit events.
BEGIN;
DROP TABLE enrollment_events;
DELETE FROM schema_migrations WHERE version = '001';
COMMIT;
