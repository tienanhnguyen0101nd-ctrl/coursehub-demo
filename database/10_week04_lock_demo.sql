-- Tab A: chay dau tien, giu lock trong 8 giay:
BEGIN;
SELECT id, capacity FROM class_sections WHERE id = 'RACE-01' FOR UPDATE;
SELECT pg_sleep(8);
COMMIT;

-- Tab B: chay RIENG trong Query Tool khac khi Tab A dang sleep:
BEGIN;
SELECT id, capacity FROM class_sections WHERE id = 'RACE-01' FOR UPDATE;
ROLLBACK;
