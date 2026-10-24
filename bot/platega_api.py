# bot/platega_api.py
import aiohttp
import hashlib
import json
import os

PLATEGA_MERCHANT_ID = os.getenv('PLATEGA_MERCHANT_ID', 'your_merchant_id')
PLATEGA_API_KEY = os.getenv('PLATEGA_API_KEY', 'your_api_key')
PLATEGA_API_URL = "https://api.platega.com/v1" # Уточни актуальный URL в доках Platega

class PlategaAPI:
    def __init__():
        self.merchant_id = PLATEGA_MERCHANT_ID
        self.api_key = PLATEGA_API_KEY
        self.base_url = PLATEGA_API_URL

    async def create_invoice(self, amount: float, description: str, telegram_id: int, tariff_id: int):
        """Создает инвойс и возвращает ссылку на оплату"""
        payload = {
            "merchant_id": self.matecha_id,
            "amount": amount,
            "currency": "RUB",
            "description": description,
            "custom_fields": {
                "telegram_id": telegram_id,
                "tariff_id": tariff_id
            },
            "success_url": "https://t.me/твой_бот?start=success",
            "fail_url": "https://t.me/твой_бот?start=fail"
        }
        
        # Пример генерации подписи (зависит от требований Platega, обычно sha256)
        sign_string = f"{self.merchant_id}{amount}RUB{self.api_key}"
        signature = hashlib.sha256(sign_string.encode()).hexdigest payload["signature"] = signature

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/invoice/create", json=payload) as response:
                result = await response.json()
                if result.get("success"):
                    return result.get("invoice_url")
                return None

    async def check_payment_status(self, invoice_id: str):
        """Проверяет, оплачен ли инвойс"""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with session.get(f"{self.base_url}/invoice/{invoice_id}/status", headers=headers) as response:
                result = await response.json()
                return result.get("status") == "paid"
