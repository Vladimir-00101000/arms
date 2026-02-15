INSERT INTO user_project_roles (id, created_at, updated_at, user_id, project_id, role_id) VALUES
(
    uuid_generate_v4(),
    NOW(),
    NOW(),
    (SELECT id FROM users WHERE login = 'admin'),
    (SELECT id FROM projects WHERE name = 'Банковское мобильное приложение'),
    (SELECT id FROM roles WHERE name = 'PROJECT_MANAGER')
),
(
    uuid_generate_v4(),
    NOW(),
    NOW(),
    (SELECT id FROM users WHERE login = 'ivan.petrov'),
    (SELECT id FROM projects WHERE name = 'Банковское мобильное приложение'),
    (SELECT id FROM roles WHERE name = 'REQUIREMENT_ANALYST')
),
(
    uuid_generate_v4(),
    NOW(),
    NOW(),
    (SELECT id FROM users WHERE login = 'maria.sidorova'),
    (SELECT id FROM projects WHERE name = 'Банковское мобильное приложение'),
    (SELECT id FROM roles WHERE name = 'REQUIREMENT_REVIEWER')
);

-- Проект 2: Система управления требованиями
INSERT INTO user_project_roles (id, created_at, updated_at, user_id, project_id, role_id) VALUES
(
    uuid_generate_v4(),
    NOW(),
    NOW(),
    (SELECT id FROM users WHERE login = 'ivan.petrov'),
    (SELECT id FROM projects WHERE name = 'Система управления требованиями'),
    (SELECT id FROM roles WHERE name = 'PROJECT_MANAGER')
),
(
    uuid_generate_v4(),
    NOW(),
    NOW(),
    (SELECT id FROM users WHERE login = 'maria.sidorova'),
    (SELECT id FROM projects WHERE name = 'Система управления требованиями'),
    (SELECT id FROM roles WHERE name = 'REQUIREMENT_ANALYST')
),
(
    uuid_generate_v4(),
    NOW(),
    NOW(),
    (SELECT id FROM users WHERE login = 'alex.smirnov'),
    (SELECT id FROM projects WHERE name = 'Система управления требованиями'),
    (SELECT id FROM roles WHERE name = 'VIEWER')
);

-- Проект 3: Облачная аналитическая платформа
INSERT INTO user_project_roles (id, created_at, updated_at, user_id, project_id, role_id) VALUES
(
    uuid_generate_v4(),
    NOW(),
    NOW(),
    (SELECT id FROM users WHERE login = 'admin'),
    (SELECT id FROM projects WHERE name = 'Облачная аналитическая платформа'),
    (SELECT id FROM roles WHERE name = 'PROJECT_MANAGER')
);