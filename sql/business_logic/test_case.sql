-- Для эндпойнта  /requirements/{requirement_id}/test-coverage
SELECT
    r.id AS requirement_id,
    r.name AS requirement_name,
    r.type AS requirement_type,
    COALESCE(
        ARRAY_AGG(DISTINCT rtc.test_case_version_id ORDER BY rtc.test_case_version_id)
        FILTER (WHERE rtc.test_case_version_id IS NOT NULL),
        ARRAY[]::VARCHAR[]
    ) AS test_case_ids
FROM requirement r
LEFT JOIN req_test_case_coverage rtc ON r.id = rtc.requirement_id
WHERE r.is_deleted = FALSE
GROUP BY r.id, r.name, r.type
ORDER BY r.id;