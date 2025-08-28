CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'member')) NOT NULL,
    specialty TEXT CHECK(specialty IN ('designer', 'developer', 'manager')) NOT NULL,
    stack TEXT, -- Стек технологий в виде строки с разделителями
    preferred_orders TEXT, -- Список предпочитаемых размеров заказов, разделенных запятыми
    warnings INTEGER DEFAULT 0, -- JSON формат для хранения уровней выговоров
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    receive_regular_notifications BOOLEAN DEFAULT 1, -- 1 - получать обычные уведомления, 0 - не получать
    total_earnings REAL DEFAULT 0.0 -- Общая сумма заработанных денег
);


CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL, -- Название заказа
    description TEXT, -- Описание заказа
    required_skills TEXT, -- Стек технологий (список навыков, разделенных запятыми)
    size TEXT CHECK(size IN ('small', 'medium', 'large')) NOT NULL, -- Размер заказа
    price REAL, -- Стоимость заказа
    deadline INTEGER, -- Дедлайн (в днях)
    specialty TEXT CHECK(specialty IN ('designer', 'developer')) NOT NULL, -- Специализация
    status TEXT CHECK(status IN ('open', 'in_progress', 'completed', 'rejected')) DEFAULT 'open', -- Статус заказа
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Дата и время создания заказа
    created_by INTEGER, -- ID пользователя, создавшего заказ
    FOREIGN KEY (created_by) REFERENCES users(id) -- Связь с таблицей пользователей
);


CREATE TABLE IF NOT EXISTS order_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL, -- ID заказа
    user_id INTEGER NOT NULL, -- ID пользователя, который взял заказ
    status TEXT CHECK(status IN ('in_progress', 'completed', 'rejected')) NOT NULL DEFAULT 'in_progress', -- Статус выполнения
    is_active BOOLEAN NOT NULL DEFAULT 1, -- Флаг активного назначения
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Время назначения заказа
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS admin_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    action_type TEXT CHECK(action_type IN ('add_whitelist', 'remove_user', 'publish_order')) NOT NULL,
    target_user_id INTEGER,
    order_id INTEGER,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id),
    FOREIGN KEY (target_user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);


CREATE TABLE IF NOT EXISTS whitelist (
    user_id INTEGER PRIMARY KEY, -- ID пользователя, которому разрешен доступ
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Время добавления пользователя в whitelist
);


CREATE TABLE IF NOT EXISTS requests (
    user_id INTEGER PRIMARY KEY,
    data TEXT NOT NULL
);