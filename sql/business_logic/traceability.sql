-- Для эндпойнта requirements/{requirement_id}/traceability:
SELECT
    r.id AS requirement_id,
    r.name AS requirement_name,
    r.type AS requirement_type,
    COALESCE(
        ARRAY_AGG(DISTINCT rd_out.target_requirement_id)
        FILTER (WHERE rd_out.target_requirement_id IS NOT NULL),
        ARRAY[]::INTEGER[]
    ) AS targets,
    COALESCE(
        ARRAY_AGG(DISTINCT rd_in.source_requirement_id)
        FILTER (WHERE rd_in.source_requirement_id IS NOT NULL),
        ARRAY[]::INTEGER[]
    ) AS sources
FROM requirement r
LEFT JOIN requirement_dependence rd_out
    ON r.id = rd_out.source_requirement_id
LEFT JOIN requirement_dependence rd_in
    ON r.id = rd_in.target_requirement_id
WHERE r.is_deleted = FALSE
    AND r.project_id = :project_id  -- если нужна фильтрация по проекту
GROUP BY r.id, r.name, r.type
ORDER BY r.id;