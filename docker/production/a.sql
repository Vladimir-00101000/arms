-- 1. Вставляем пользователей
INSERT INTO users (id, created_at, updated_at, external_id, login, surname, name, email, status, is_admin) VALUES
(uuid_generate_v4(), NOW(), NOW(), 'ext_admin_001', 'admin', 'Иванов', 'Иван', 'admin@example.com', 'ACTIVE', TRUE),
(uuid_generate_v4(), NOW(), NOW(), 'ext_user_002', 'ivan.petrov', 'Петров', 'Иван', 'ivan.petrov@example.com', 'ACTIVE', FALSE),
(uuid_generate_v4(), NOW(), NOW(), 'ext_user_003', 'maria.sidorova', 'Сидорова', 'Мария', 'maria.sidorova@example.com', 'ACTIVE', FALSE),
(uuid_generate_v4(), NOW(), NOW(), 'ext_user_004', 'alex.smirnov', 'Смирнов', 'Алексей', 'alex.smirnov@example.com', 'ACTIVE', FALSE);

-- 2. Вставляем роли
INSERT INTO roles (id, created_at, updated_at, name, description) VALUES
(uuid_generate_v4(), NOW(), NOW(), 'PROJECT_MANAGER', 'Руководитель проекта: полный доступ к проекту и требованиям'),
(uuid_generate_v4(), NOW(), NOW(), 'REQUIREMENT_ANALYST', 'Аналитик требований: работа с требованиями'),
(uuid_generate_v4(), NOW(), NOW(), 'REQUIREMENT_REVIEWER', 'Рецензент требований: проверка и утверждение'),
(uuid_generate_v4(), NOW(), NOW(), 'VIEWER', 'Наблюдатель: только просмотр проекта и требований');

-- 3. Вставляем права доступа
INSERT INTO permissions (id, created_at, updated_at, permission, description) VALUES
(uuid_generate_v4(), NOW(), NOW(), 'project:read', 'Просмотр проектов'),
(uuid_generate_v4(), NOW(), NOW(), 'project:create', 'Создание проектов'),
(uuid_generate_v4(), NOW(), NOW(), 'project:manage_users', 'Управление пользователями в проекте'),
(uuid_generate_v4(), NOW(), NOW(), 'requirement:create', 'Создание требований'),
(uuid_generate_v4(), NOW(), NOW(), 'requirement:read', 'Просмотр требований'),
(uuid_generate_v4(), NOW(), NOW(), 'requirement:update', 'Обновление требований'),
(uuid_generate_v4(), NOW(), NOW(), 'requirement:delete', 'Удаление требований'),
(uuid_generate_v4(), NOW(), NOW(), 'requirement:approve', 'Утверждение требований'),
(uuid_generate_v4(), NOW(), NOW(), 'requirement:reject', 'Отклонение требований'),
(uuid_generate_v4(), NOW(), NOW(), 'requirement:review', 'Рецензирование требований');

-- 4. Назначаем права ролям (RolePermission)
INSERT INTO role_permissions (id, created_at, updated_at, role_id, permission_id)
SELECT 
    uuid_generate_v4(),
    NOW(),
    NOW(),
    r.id AS role_id,
    p.id AS permission_id
FROM roles r, permissions p
WHERE r.name = 'PROJECT_MANAGER'
AND p.permission IN (
    'project:read', 'project:create', 'project:manage_users',
    'requirement:create', 'requirement:read', 'requirement:update',
    'requirement:delete', 'requirement:approve', 'requirement:reject',
    'requirement:review'
);

-- ... остальные role_permissions с NOW(), NOW() ...

-- 5. Вставляем проекты
INSERT INTO projects (id, created_at, updated_at, name, description, status, created_by_user_id) VALUES
(uuid_generate_v4(), NOW(), NOW(), 'Банковское мобильное приложение', 'Разработка мобильного приложения для банка', 'active',
    (SELECT id FROM users WHERE login = 'admin')),
(uuid_generate_v4(), NOW(), NOW(), 'Система управления требованиями', 'Внутренняя система для работы с требованиями', 'active',
    (SELECT id FROM users WHERE login = 'ivan.petrov')),
(uuid_generate_v4(), NOW(), NOW(), 'Облачная аналитическая платформа', 'Платформа для анализа больших данных', 'planned',
    (SELECT id FROM users WHERE login = 'admin'));

-- 6. Назначаем пользователей на проекты с ролями (UserProjectRole)
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