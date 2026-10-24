# core/db_manager.py
import sqlite3
import time
import os

DB_PATH = os.getenv('WPP_DB_PATH', '/etc/wpp-panel/wpp.db')

def init_db():
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
        # Таблица подписок (клиентов)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                email TEXT UNIQUE NOT NULL,
                protocol TEXT NOT NULL,
                transport TEXT NOT NULL,
                security TEXT NOT NULL,
                expire_time INTEGER NOT NULL,
                traffic_limit_bytes REAL NOT NULL,
                traffic_used_bytes REAL DEFAULT 0.0,
                config_json TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        conn.commit()

def add_tariff(name, price, duration_days, traffic_limit_gb):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tariffs (name, price, duration_days, traffic_limit_gb) VALUES (?, ?, ?, ?)',
            (name, price, duration_days, traffic_limit_gb)
        )
        conn.commit()
        return cursor.lastrowid

def get_active_tariffs():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tariffs WHERE is_active = 1')
        return [dict(row) for row in cursor.fetchall()]

def create_subscription(telegram_id, email, protocol, transport, security, duration_days, traffic_limit_gb, config_json):
    expire_time = int(time.time()) + (duration_days * 86400)
    traffic_limit_bytes = traffic_limit_gb * (1024 ** 3)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO subscriptions 
            (telegram_id, email, protocol, transport, security, expire_time, traffic_limit_bytes, config_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (telegram_id, email, protocol, transport, security, expire_time, traffic_limit_bytes, config_json))
        conn.commit()
        return cursor.lastrowid

def get_user_subscriptions(telegram_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM subscriptions WHERE telegram_id = ? AND is_active = 1', (telegram_id,))
        return [dict(row) for row in cursor.fetchall()]
