# core/db_manager.py
import sqlite3
import time
import os

DB_PATH = os.getenv('WPP_DB_PATH', '/etc/wpp-panel/wpp.db')

def init_db():
    """Инициализация базы данных"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Таблица тарифов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tariffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                duration_days INTEGER NOT NULL,
                traffic_limit_gb REAL NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Таблица подписок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                email TEXT UNIQUE NOT NULL,
                protocol TEXT NOT NULL,
                transport TEXT NOT NULL,
                security TEXT NOT NULL,
                uuid TEXT,
                password TEXT,
                expire_time INTEGER NOT NULL,
                traffic_limit_bytes REAL NOT NULL,
                traffic_used_bytes REAL DEFAULT 0.0,
                config_json TEXT,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()

def add_tariff(name, price, duration_days, traffic_limit_gb):
    """Добавление нового тарифа"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tariffs (name, price, duration_days, traffic_limit_gb) VALUES (?, ?, ?, ?)',
            (name, price, duration_days, traffic_limit_gb)
        )
        conn.commit()
        return cursor.lastrowid

def get_active_tariffs():
    """Получение всех активных тарифов"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tariffs WHERE is_active = 1 ORDER BY price')
        return [dict(row) for row in cursor.fetchall()]

def get_tariff_by_id(tariff_id):
    """Получение тарифа по ID"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tariffs WHERE id = ? AND is_active = 1', (tariff_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def create_subscription(telegram_id, email, protocol, transport, security, 
                       uuid, password, duration_days, traffic_limit_gb, config_json):
    """Создание новой подписки"""
    expire_time = int(time.time()) + (duration_days * 86400)
    traffic_limit_bytes = traffic_limit_gb * (1024 ** 3)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO subscriptions 
            (telegram_id, email, protocol, transport, security, uuid, password, 
             expire_time, traffic_limit_bytes, config_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (telegram_id, email, protocol, transport, security, uuid, password, 
              expire_time, traffic_limit_bytes, config_json))
        conn.commit()
        return cursor.lastrowid

def get_user_subscriptions(telegram_id):
    """Получение всех активных подписок пользователя"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM subscriptions 
            WHERE telegram_id = ? AND is_active = 1 
            ORDER BY expire_time DESC
        ''', (telegram_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_subscription_by_email(email):
    """Получение подписки по email"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM subscriptions WHERE email = ?', (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_subscription_traffic(email, used_bytes):
    """Обновление использованного трафика"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE subscriptions SET traffic_used_bytes = ? WHERE email = ?
        ''', (used_bytes, email))
        conn.commit()

def deactivate_subscription(email):
    """Деактивация подписки"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE subscriptions SET is_active = 0 WHERE email = ?
        ''', (email,))
        conn.commit()

def get_expired_subscriptions():
    """Получение всех просроченных подписок"""
    current_time = int(time.time())
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM subscriptions 
            WHERE expire_time < ? AND is_active = 1
        ''', (current_time,))
        return [dict(row) for row in cursor.fetchall()]

def get_exceeded_traffic_subscriptions():
    """Получение подписок с превышенным трафиком"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM subscriptions 
            WHERE traffic_used_bytes >= traffic_limit_bytes AND is_active = 1
        ''')
        return [dict(row) for row in cursor.fetchall()]
