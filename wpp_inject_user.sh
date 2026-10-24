#!/bin/bash
# wpp_inject_user.sh
# Добавляет новый inbound в конфиг Xray и перезапускает сервис

INBOUND_JSON="$1"
# Путь к конфигу Xray (может отличаться, проверь в своей панели)
XRAY_CONFIG="/etc/xray/config.json" 

if [ -z "$INBOUND_JSON" ]; then
    echo "Error: No JSON config provided"
    exit 1
fi

if command -v jq &> /dev/null; then
    # Проверяем, валидный ли JSON
    if ! echo "$INBOUND_JSON" | jq empty 2>/dev/null; then
        echo "Error: Invalid JSON format"
        exit 1
    fi

    # Добавляем новый inbound в массив inbounds существующего конфига
    jq --argjson new_inbound "$INBOUND_JSON" '.inbounds += [$new_inbound]' "$XRAY_CONFIG" > "${XRAY_CONFIG}.tmp" && mv "${XRAY_CONFIG}.tmp" "$XRAY_CONFIG"
    
    # Перезапускаем Xray (пытаемся разные имена сервисов, так как в разных панелях они отличаются)
    systemctl restart xray 2>/dev/null || systemctl restart x-ui 2>/dev/null || systemctl restart web-panel-proxy-xray 2>/dev/null
    
    echo "Success: User added to Xray"
else
    echo "Error: jq is not installed"
    exit 1
fi
