-- CHAY RIENG tung muc 1, 2, 3 de co so lieu truoc/sau.
-- 1. TRUOC INDEX:
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, student_id, class_section_id, event_type, occurred_at
FROM enrollment_events
WHERE dataset = 'performance'
  AND student_id = '22000001'
  AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
ORDER BY occurred_at DESC LIMIT 50;

-- 2. TAO INDEX (chi chay 1 lan):
CREATE INDEX idx_enrollment_events_dataset_student_time
ON enrollment_events (dataset, student_id, occurred_at DESC);
ANALYZE enrollment_events;

-- 3. SAU INDEX: cung truy van nhu tren:
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, student_id, class_section_id, event_type, occurred_at
FROM enrollment_events
WHERE dataset = 'performance'
  AND student_id = '22000001'
  AND occurred_at >= TIMESTAMP '2025-12-20 00:00:00'
ORDER BY occurred_at DESC LIMIT 50;
