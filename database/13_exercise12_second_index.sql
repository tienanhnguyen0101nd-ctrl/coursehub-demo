
ANALYZE enrollment_events;

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
  AND occurred_at >=
      TIMESTAMP '2025-12-01 00:00:00'
ORDER BY occurred_at DESC, id DESC
LIMIT 50;



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
  AND occurred_at >=
      TIMESTAMP '2025-12-01 00:00:00'
ORDER BY occurred_at DESC, id DESC
LIMIT 50;

SELECT COUNT(*)
FROM enrollment_events
WHERE dataset = 'performance'
  AND class_section_id = 'WEB-02'
  AND event_type = 'CREATED'
  AND occurred_at >=
      TIMESTAMP '2025-12-01 00:00:00';

SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'enrollment_events'
  AND indexname =
      'idx_enrollment_events_class_type_time';