#!/bin/bash
# install-bot.sh - Установка Telegram-бота и расширенной БД для WPP

echo ""
echo "🚀 Installing WPP Telegram Bot & DB Module..."

# 1. Ставим Python и утилиты
apt-get update -y
apt-get install -y python3 python3-pip python3-venv jq

# 2. Создаем папки
mkdir -p /opt/wpp-panel/bot_core/core
mkdir -p /opt/wpp-panel/bot_core/bot
mkdir -p /etc/wpp-panel

# 3. Виртуальное окружение и библиотеки
python3 -m venv /opt/wpp-panel/bot_venv
/opt/wpp-panel/bot_venv/bin/pip install --upgrade pip
/opt/wpp-panel/bot_venv/bin/pip install aiogram==3.4.1 aiohttp==3.9.1

# 4. Создаем systemd сервис для бота
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
ExecStart=/opt/wpp-panel/bot_venv/bin/python3 /opt/wpp-panel/bot_core/bot/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 5. Включаем автозапуск
systemctl daemon-reload
systemctl enable wpp-bot.service

echo "✅ WPP Bot Module installed successfully!"
