#!/bin/bash
# install-bot.sh - Установка Telegram-бота и расширенной БД для WPP

echo "🤖 Установка модуля Telegram-бота..."

# Python и зависимости
if ! command -v python3 &> /dev/null; then
    apt-get update && apt-get install -y python3 python3-pip python3-venv jq
fi

# Виртуальное окружение
python3 -m venv /opt/wpp-panel/bot_venv
source /opt/wpp-panel/bot_venv/bin/activate
pip3 install --upgrade pip
pip3 install aiogram==3.4.1 aiohttp==3.9.1

# Структура папок
mkdir -p /opt/wpp-panel/bot_core/core
mkdir -p /opt/wpp-panel/bot_core/bot
mkdir -p /etc/wpp-panel

# Системный сервис
cat << 'EOF' > /etc/systemd/system/wpp-bot.service
[Unit]
Description=WPP Telegram Bot
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

systemctl daemon-reload
systemctl enable wpp-bot.service

echo "✅ Модуль бота установлен!"
