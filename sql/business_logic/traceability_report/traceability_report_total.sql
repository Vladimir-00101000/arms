-- Для эндпойнта  /reports/traceability и формирования отчета по матрице трассируемостию
WITH requirement_coverage AS (
    SELECT
        r.id,
        r.type,
        CASE
            WHEN r.type = 'business' THEN
                NOT EXISTS (
                    SELECT 1
                    FROM requirement_dependence rd
                    INNER JOIN requirement r_target ON rd.target_requirement_id = r_target.id
                    WHERE rd.source_requirement_id = r.id
                      AND r_target.type IN ('functional', 'non-functional')
                      AND r_target.is_deleted = FALSE
                )
            WHEN r.type IN ('functional', 'non-functional') THEN
                NOT EXISTS (
                    SELECT 1
                    FROM requirement_dependence rd
                    INNER JOIN requirement r_source ON rd.source_requirement_id = r_source.id
                    WHERE rd.target_requirement_id = r.id
                      AND r_source.is_deleted = FALSE
                )
        END AS is_uncovered
    FROM requirement r
    WHERE r.is_deleted = FALSE
      AND r.project_id = :project_id  -- если нужна фильтрация по проекту
)
SELECT
    type AS requirement_type,
    COUNT(*) FILTER (WHERE is_uncovered = TRUE) AS uncovered_count,
    COUNT(*) AS total_count,
    ROUND(
        (COUNT(*) FILTER (WHERE is_uncovered = FALSE)::NUMERIC / NULLIF(COUNT(*), 0) * 100),
        2
    ) AS coverage_percentage
FROM requirement_coverage
GROUP BY type
ORDER BY type;