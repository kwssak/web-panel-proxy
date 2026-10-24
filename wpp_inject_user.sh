#!/bin/bash
# wpp_inject_user.sh - Добавляет пользователя в конфиг Xray

INBOUND_JSON="$1"
XRAY_CONFIG="/etc/xray/config.json"

if [ -z "$INBOUND_JSON" ]; then
    echo "Ошибка: не передан JSON конфиг"
    exit 1
fi

if command -v jq &> /dev/null; then
    jq ".inbounds += [$INBOUND_JSON]" "$XRAY_CONFIG" > "${XRAY_CONFIG}.tmp" && mv "${XRAY_CONFIG}.tmp" "$XRAY_CONFIG"
    systemctl restart xray
    echo "✅ Пользователь добавлен в Xray!"
else
    echo "❌ Ошибка: утилита 'jq' не установлена"
    exit 1
fi
