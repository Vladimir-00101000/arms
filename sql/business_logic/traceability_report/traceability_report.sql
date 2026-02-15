-- Для эндпойнта  /reports/traceability и формирования отчета по матрице трассировки
SELECT
    r.id AS requirement_id,
    r.name AS requirement_name,
    r.type AS requirement_type,
    CASE
        WHEN r.type = 'business' THEN 'Нет исходящих связей'
        WHEN r.type IN ('functional', 'non-functional') THEN 'Нет входящих связей (источников)'
    END AS issue_description
FROM requirement r
WHERE r.is_deleted = FALSE
  AND (
    -- Business требования без исходящих связей к functional/non-functional
    (
        r.type = 'business'
        AND NOT EXISTS (
            SELECT 1
            FROM requirement_dependence rd
            INNER JOIN requirement r_target ON rd.target_requirement_id = r_target.id
            WHERE rd.source_requirement_id = r.id
              AND r_target.type IN ('functional', 'non-functional')
              AND r_target.is_deleted = FALSE
        )
    )
    OR
    -- Functional/Non-functional требования без входящих связей
    (
        r.type IN ('functional', 'non-functional')
        AND NOT EXISTS (
            SELECT 1
            FROM requirement_dependence rd
            INNER JOIN requirement r_source ON rd.source_requirement_id = r_source.id
            WHERE rd.target_requirement_id = r.id
              AND r_source.is_deleted = FALSE
        )
    )
  )
ORDER BY r.type, r.id;