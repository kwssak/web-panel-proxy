# bot/handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.db_manager import get_active_tariffs, create_subscription
from core.xray_builder import build_xray_inbound
import json

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Купить подписку", callback_data="buy_tariff")],
        [InlineKeyboardButton(text="👤 Мои подписки", callback_data="my_subs")]
    ])
    await message.answer("Добро пожаловать в ColorVpn Bot.\nВыберите действие:", reply_markup=keyboard)

@router.callback_query(F.data == "buy_tariff")
async def show_tariffs(callback: CallbackQuery):
    tariffs = get_active_tariffs()
    if not tariffs:
        await callback.answer("Тарифы временно недоступны", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for t in tariffs:
        btn_text = f"{t['name']} | {t['price']}₽ | {t['duration_days']} дн. | {t['traffic_limit_gb']} ГБ"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=btn_text, callback_data=f"pay_tariff_{t['id']}")
        ])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="start")])
    
    await callback.message.edit_text("Выберите тариф для оплаты:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("pay_tariff_"))
async def process_payment(callback: CallbackQuery):
    tariff_id = int(callback.data.split("_")[2])
    # Здесь должна быть логика создания инвойса через Platega API
    # Для скелета эмулируем успешную оплату и создание конфига
    
    await callback.answer("Создание инвойса Platega...", show_alert=True)
    
    # ЭМУЛЯЦИЯ УСПЕШНОЙ ОПЛАТЫ (в реальности это придет через Webhook от Platega)
    # Получаем данные тарифа из БД (упрощенно)
    tariff = {"name": "Premium", "duration_days": 30, "traffic_limit_gb": 100}
    
    # 1. Генерируем конфиг через наше новое ядро
    new_inbound = build_xray_inbound(
        port=443,
        protocol="vless",
        transport="xhttp",
        security="tls",
        path="/vless-cdn",
        host="cdn.svreeroff.site"
    )
    
    # 2. Сохраняем подписку в БД
    sub_id = create_subscription(
        telegram_id=callback.from_user.id,
        email=f"user{callback.from_user.id}@colorvpn.local",
        protocol="vless",
        transport="xhttp",
        security="tls",
        duration_days=tariff['duration_days'],
        traffic_limit_gb=tariff['traffic_limit_gb'],
        config_json=json.dumps(new_inbound)
    )
    
    # 3. Отдаем ссылку пользователю
    sub_link = f"https://cdn.svreeroff.site/sub/{sub_id}" # Пример формата ссылки
    await callback.message.answer(
        f"✅ Оплата прошла успешно!\n\n"
        f"Ваша ссылка на подписку:\n<code>{sub_link}</code>\n\n"
        f"Скопируйте её и добавьте в ваш VPN-клиент.",
        parse_mode="HTML"
    )
