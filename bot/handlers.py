# bot/handlers.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.db_manager import get_active_tariffs
from bot.platega_api import PlategaAPI

router = Router()
platega = PlategaAPI()

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
            InlineKeyboardButton(text=btn_text, callback_data=f"create_invoice_{t['id']}")
        ])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="start")])
    
    await callback.message.edit_text("Выберите тариф для оплаты:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("create_invoice_"))
async def create_invoice_handler(callback: CallbackQuery):
    tariff_id = int(callback.data.split("_")[2])
    tariffs = get_active_tariffs()
    tariff = next((t for t in tariffs if t['id'] == tariff_id), None)
    
    if not tariff:
        await callback.answer("Ошибка: тариф не найден", show_alert=True)
        return

    await callback.message.edit_text("⏳ Формирую счет на оплату...")
    
    # Создаем инвойс
    invoice_url = await platega.create_invoice(
        amount=tariff['price'],
        description=f"VPN Подписка: {tariff['name']} ({tariff['duration_days']} дн.)",
        telegram_id=callback.from_user.id,
        tariff_id=tariff['id']
    )
    
    if invoice_url:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=invoice_url)],
            [InlineKeyboardButton(text="🔄 Проверить статус оплаты", callback_data=f"check_status_{tariff_id}")]
        ])
        await callback.message.edit_text(
            f"Счет на сумму **{tariff['price']}₽** создан.\n\n"
            f"Нажмите кнопку ниже для перехода к оплате. После оплаты нажмите 'Проверить статус'.",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text("❌ Ошибка при создании счета. Попробуйте позже или напишите в поддержку.")
