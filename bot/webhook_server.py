# bot/webhook_server.py
from aiohttp import web
import json
from core.db_manager import create_subscription, get_active_tariffs # Импорт из твоего ядра
from core.xray_builder import build_xray_inbound
import hashlib
import os

PLATEGA_WEBHOOK_SECRET = os.getenv('PLATEGA_WEBHOOK_SECRET', 'your_webhook_secret')

async def handle_platega_webhook(request):
    try:
        data = await request.json()
        
        # 1. Проверка подписи вебхука (защита от фейковых запросов)
        # signature = hashlib.sha256(f"{data['invoice_id']}{PLATEGA_WEBHOOK_SECRET}".encode()).hexdigest()
        # if data.get('signature') != signature:
        #     return web.Response(status=403, text="Invalid signature")

        if data.get("status") == "paid":
            custom_fields = data.get("custom_fields", {})
            telegram_id = custom_fields.get("telegram_id")
            tariff_id = custom_fields.get("tariff_id")

            if not telegram_id or not tariff_id:
                return web.Response(status=400, text="Missing custom fields")

            # 2. Получаем данные тарифа из БД
            tariffs = get_active_tariffs()
            tariff = next((t for t in tariffs if t['id'] == tariff_id), None)
            
            if not tariff:
                return web.Response(status=404, text="Tariff not found")

            # 3. Генерируем конфиг Xray (здесь можно добавить рандомизацию порта/пути)
            new_inbound = build_xray_inbound(
                port=443,
                protocol="vless", # Можно сделать выбор при покупке
                transport="xhttp",
                security="tls",
                path=f"/{telegram_id}", # Уникальный путь для пользователя
                host="cdn.svreeroff.site"
            )

            # 4. Сохраняем в БД
            sub_id = create_subscription(
                telegram_id=telegram_id,
                email=f"user{telegram_id}@colorvpn.local",
                protocol="vless",
                transport="xhttp",
                security="tls",
                duration_days=tariff['duration_days'],
                traffic_limit_gb=tariff['traffic_limit_gb'],
                config_json=json.dumps(new_inbound)
            )

            # 5. (Опционально) Здесь можно отправить сообщение пользователю через Bot API, 
            # если у тебя есть доступ к объекту bot, или просто положиться на то, что он проверит статус.
            
            return web.Response(status=200, text="OK")
        
        return web.Response(status=200, text="Ignored status")

    except Exception as e:
        print(f"Webhook error: {e}")
        return web.Response(status=500, text="Internal Server Error")

def setup_webhook_app():
    app = web.Application()
    app.router.add_post('/webhook/platega', handle_platega_webhook)
    return app
