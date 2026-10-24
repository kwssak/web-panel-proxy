# bot/webhook_server.py
from aiohttp import web
import json
import subprocess
import os
from core.db_manager import create_subscription, get_tariff_by_id
from core.xray_builder import build_xray_inbound

PLATEGA_WEBHOOK_SECRET = os.getenv('PLATEGA_WEBHOOK_SECRET', 'secret')

async def handle_platega_webhook(request):
    try:
        data = await request.json()
        
        # В реальном проекте здесь нужно проверить подпись запроса!
        if data.get("status") == "paid":
            custom_fields = data.get("custom_fields", {})
            telegram_id = custom_fields.get("telegram_id")
            tariff_id = custom_fields.get("tariff_id")

            if not telegram_id or not tariff_id:
                return web.Response(status=400, text="Missing fields")

            tariff = get_tariff_by_id(tariff_id)
            if not tariff:
                return web.Response(status=404, text="Tariff not found")

            # Генерируем уникальный конфиг
            user_uuid = build_xray_inbound(443, "vless", "xhttp", "tls")["settings"]["clients"][0]["id"]
            user_path = f"/{telegram_id}_{build_xray_inbound(443, 'vless', 'xhttp', 'tls')['tag'][:8]}"
            
            new_inbound = build_xray_inbound(
                port=443,
                protocol="vless",
                transport="xhttp",
                security="tls",
                uuid=user_uuid,
                path=user_path,
                host="cdn.svreeroff.site"
            )

            # Сохраняем в БД
            sub_id = create_subscription(
                telegram_id=telegram_id,
                email=f"user{telegram_id}@colorvpn.local",
                protocol="vless",
                transport="xhttp",
                security="tls",
                uuid=user_uuid,
                password="",
                duration_days=tariff['duration_days'],
                traffic_limit_gb=tariff['traffic_limit_gb'],
                config_json=json.dumps(new_inbound)
            )

            # Вызываем bash-инжектор, чтобы добавить в Xray
            inject_script = "/opt/wpp-panel/wpp_inject_user.sh"
            if os.path.exists(inject_script):
                subprocess.run([inject_script, json.dumps(new_inbound)], check=True)

            return web.Response(status=200, text="OK")
        
        return web.Response(status=200, text="Ignored")

    except Exception as e:
        print(f"Webhook error: {e}")
        return web.Response(status=500, text="Error")

def setup_webhook_app():
    app = web.Application()
    app.router.add_post('/webhook/platega', handle_platega_webhook)
    return app
