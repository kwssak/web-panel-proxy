#!/bin/bash
# install-bot.sh - Полная установка Telegram-бота и веб-интерфейса WPP

echo ""
echo "🚀 Installing WPP Telegram Bot & Web Interface..."

# 1. Ставим Python и утилиты
apt-get update -y
apt-get install -y python3 python3-pip python3-venv jq

# 2. Создаем структуру папок
mkdir -p /opt/wpp-panel/bot_core/core
mkdir -p /opt/wpp-panel/bot_core/bot
mkdir -p /opt/wpp-panel/bot_core/web/templates
mkdir -p /etc/wpp-panel

# 3. Виртуальное окружение и библиотеки
python3 -m venv /opt/wpp-panel/bot_venv
/opt/wpp-panel/bot_venv/bin/pip install --upgrade pip
/opt/wpp-panel/bot_venv/bin/pip install aiogram==3.4.1 aiohttp==3.9.1 flask==3.0.0

# 4. Создаем __init__.py файлы
cat << 'EOF' > /opt/wpp-panel/bot_core/core/__init__.py
# Core module for WPP Bot
EOF

cat << 'EOF' > /opt/wpp-panel/bot_core/bot/__init__.py
# Bot module for WPP
EOF

cat << 'EOF' > /opt/wpp-panel/bot_core/web/__init__.py
# Web module for WPP
EOF

# 5. Создаем systemd сервис для бота
cat << 'EOF' > /etc/systemd/system/wpp-bot.service
[Unit]
Description=WPP Telegram Bot and Webhook Server
After=network.target xray.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/wpp-panel/bot_core
Environment=PYTHONUNBUFFERED=1
Environment=BOT_TOKEN=YOUR_BOT_TOKEN
Environment=PLATEGA_MERCHANT_ID=YOUR_MERCHANT_ID
Environment=PLATEGA_API_KEY=YOUR_API_KEY
Environment=PLATEGA_WEBHOOK_SECRET=YOUR_WEBHOOK_SECRET
Environment=WPP_DB_PATH=/etc/wpp-panel/wpp.db
Environment=WEB_PORT=5000
ExecStart=/opt/wpp-panel/bot_venv/bin/python3 -m bot.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 6. Создаем systemd сервис для веб-интерфейса
cat << 'EOF' > /etc/systemd/system/wpp-web.service
[Unit]
Description=WPP Web Interface for Tariffs
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/wpp-panel/bot_core/web
Environment=PYTHONUNBUFFERED=1
Environment=WPP_DB_PATH=/etc/wpp-panel/wpp.db
ExecStart=/opt/wpp-panel/bot_venv/bin/python3 app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 7. Создаем файлы веб-интерфейса

# tariffs_api.py
cat << 'PYEOF' > /opt/wpp-panel/bot_core/web/tariffs_api.py
from flask import Blueprint, request, jsonify
import sys
sys.path.insert(0, '/opt/wpp-panel/bot_core')
from core.db_manager import add_tariff, get_active_tariffs, get_tariff_by_id

tariffs_bp = Blueprint('tariffs', __name__, url_prefix='/api/tariffs')

@tariffs_bp.route('/', methods=['GET'])
def api_get_tariffs():
    tariffs = get_active_tariffs()
    return jsonify({"success": True, "tariffs": tariffs})

@tariffs_bp.route('/', methods=['POST'])
def api_add_tariff():
    try:
        data = request.json
        if not all(k in data for k in ['name', 'price', 'duration_days', 'traffic_limit_gb']):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        tariff_id = add_tariff(
            name=data['name'],
            price=float(data['price']),
            duration_days=int(data['duration_days']),
            traffic_limit_gb=float(data['traffic_limit_gb'])
        )
        return jsonify({"success": True, "id": tariff_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
PYEOF

# app.py
cat << 'PYEOF' > /opt/wpp-panel/bot_core/web/app.py
from flask import Flask, render_template, send_from_directory
from tariffs_api import tariffs_bp
import os

app = Flask(__name__, template_folder='templates', static_folder='templates')
app.register_blueprint(tariffs_bp)

@app.route('/')
def index():
    return render_template('tariffs.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('templates', filename)

if __name__ == '__main__':
    port = int(os.getenv('WEB_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
PYEOF

# tariffs.html
cat << 'HTMLEOF' > /opt/wpp-panel/bot_core/web/templates/tariffs.html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Управление тарифами - WPP Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0a; color: #e0e0e0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #fff; margin-bottom: 30px; font-size: 28px; }
        .form-section { background: #1a1a1a; padding: 25px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #333; }
        .form-section h2 { color: #fff; margin-bottom: 20px; font-size: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 8px; color: #b0b0b0; font-size: 14px; }
        input[type="text"], input[type="number"] { width: 100%; padding: 12px; background: #0a0a0a; border: 1px solid #333; border-radius: 6px; color: #fff; font-size: 14px; }
        input:focus { outline: none; border-color: #4a9eff; }
        button { background: #4a9eff; color: #fff; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; }
        button:hover { background: #3a8eef; }
        .tariffs-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .tariff-card { background: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; }
        .tariff-card h3 { color: #fff; margin-bottom: 15px; font-size: 18px; }
        .tariff-info { margin-bottom: 10px; color: #b0b0b0; font-size: 14px; }
        .tariff-info span { color: #fff; font-weight: 600; }
        .message { padding: 12px; border-radius: 6px; margin-bottom: 20px; display: none; }
        .message.success { background: #1b5e20; color: #fff; display: block; }
        .message.error { background: #b71c1c; color: #fff; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Управление тарифами</h1>
        <div id="message" class="message"></div>
        <div class="form-section">
            <h2>Добавить новый тариф</h2>
            <form id="tariffForm">
                <div class="form-group">
                    <label for="name">Название тарифа</label>
                    <input type="text" id="name" name="name" required placeholder="Например: Premium 30 дней">
                </div>
                <div class="form-group">
                    <label for="price">Цена (₽)</label>
                    <input type="number" id="price" name="price" required step="0.01" placeholder="299.99">
                </div>
                <div class="form-group">
                    <label for="duration_days">Срок действия (дней)</label>
                    <input type="number" id="duration_days" name="duration_days" required placeholder="30">
                </div>
                <div class="form-group">
                    <label for="traffic_limit_gb">Лимит трафика (ГБ)</label>
                    <input type="number" id="traffic_limit_gb" name="traffic_limit_gb" required step="0.1" placeholder="100">
                </div>
                <button type="submit">Добавить тариф</button>
            </form>
        </div>
        <div class="form-section">
            <h2>Активные тарифы</h2>
            <div id="tariffsList" class="tariffs-list">
                <p style="color: #b0b0b0;">Загрузка...</p>
            </div>
        </div>
    </div>
    <script>
        const API_BASE = '/api/tariffs';
        async function loadTariffs() {
            try {
                const response = await fetch(API_BASE);
                const data = await response.json();
                if (data.success) {
                    displayTariffs(data.tariffs);
                } else {
                    showMessage('Ошибка загрузки тарифов', 'error');
                }
            } catch (error) {
                showMessage('Ошибка подключения к API', 'error');
            }
        }
        function displayTariffs(tariffs) {
            const container = document.getElementById('tariffsList');
            if (tariffs.length === 0) {
                container.innerHTML = '<p style="color: #b0b0b0;">Нет активных тарифов</p>';
                return;
            }
            container.innerHTML = tariffs.map(tariff => `
                <div class="tariff-card">
                    <h3>${tariff.name}</h3>
                    <div class="tariff-info">Цена: <span>${tariff.price} ₽</span></div>
                    <div class="tariff-info">Срок: <span>${tariff.duration_days} дней</span></div>
                    <div class="tariff-info">Трафик: <span>${tariff.traffic_limit_gb} ГБ</span></div>
                </div>
            `).join('');
        }
        document.getElementById('tariffForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = {
                name: document.getElementById('name').value,
                price: parseFloat(document.getElementById('price').value),
                duration_days: parseInt(document.getElementById('duration_days').value),
                traffic_limit_gb: parseFloat(document.getElementById('traffic_limit_gb').value)
            };
            try {
                const response = await fetch(API_BASE, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const data = await response.json();
                if (data.success) {
                    showMessage(`Тариф успешно добавлен! ID: ${data.id}`, 'success');
                    document.getElementById('tariffForm').reset();
                    loadTariffs();
                } else {
                    showMessage(`Ошибка: ${data.error}`, 'error');
                }
            } catch (error) {
                showMessage('Ошибка подключения к API', 'error');
            }
        });
        function showMessage(text, type) {
            const messageEl = document.getElementById('message');
            messageEl.textContent = text;
            messageEl.className = `message ${type}`;
            setTimeout(() => { messageEl.className = 'message'; }, 5000);
        }
        loadTariffs();
    </script>
</body>
</html>
HTMLEOF

# 8. Включаем автозапуск сервисов
systemctl daemon-reload
systemctl enable wpp-bot.service
systemctl enable wpp-web.service

echo "✅ WPP Bot & Web Interface installed successfully!"
echo "📌 Don't forget to set your BOT_TOKEN and PLATEGA credentials in /etc/systemd/system/wpp-bot.service"
