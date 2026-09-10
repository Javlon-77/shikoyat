import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


# =========================
# SOZLAMALAR
# =========================

BOT_TOKEN = "8922035954:AAHdH2ZX9gWW7_Cf3-1NaOPK6wv_Fl5breQ"
ADMIN_CHAT_ID = 8363022038


# =========================
# BOT / DISPATCHER
# =========================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =========================
# FSM HOLATLAR
# =========================

class ComplaintState(StatesGroup):
    waiting_text = State()


# =========================
# ASOSIY KATEGORIYALAR
# =========================

MAIN_CATEGORIES = {
    "education": "🎓 Taʼlim jarayoni bilan bogʻliq",
    "admin": "🏢 Maʼmuriy-tashkiliy",
    "labor": "👷 Mehnat munosabatlari",
    "ethics": "🤝 Axloq-odob va hurmat meʼyorlarining buzilishi",
    "corruption": "⚠️ Korrupsiyaga oid alomatlar",
    "other": "📌 Boshqa masalalar",
}


# =========================
# 2-BOSQICH
# =========================

SUBCATEGORIES = {
    "conflict": "⚖️ Nizolar",
    "management": "🏛 Boshqaruvdagi nuqsonlar",
    "ethical": "🚫 Etik buzilishlar",
}


# =========================
# 3-BOSQICH
# =========================

COMPLAINT_TYPES = {
    "personal": "👤 Shaxsiy shikoyat",
    "collective": "👥 Jamoaviy shikoyat",
    "anonymous": "🕶 Anonim murojaat",
}


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["education"],
                    callback_data="cat:education"
                )
            ],
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["admin"],
                    callback_data="cat:admin"
                )
            ],
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["labor"],
                    callback_data="cat:labor"
                )
            ],
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["ethics"],
                    callback_data="cat:ethics"
                )
            ],
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["corruption"],
                    callback_data="cat:corruption"
                )
            ],
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["other"],
                    callback_data="cat:other"
                )
            ],
        ]
    )

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Murojaat turini tanlang:",
        reply_markup=keyboard
    )


# =========================
# 1-BOSQICH: KATEGORIYA
# =========================

@dp.callback_query(F.data.startswith("cat:"))
async def category_handler(callback: CallbackQuery, state: FSMContext):
    category_key = callback.data.split(":")[1]

    await state.update_data(
        category=MAIN_CATEGORIES[category_key]
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=SUBCATEGORIES["conflict"],
                    callback_data="sub:conflict"
                )
            ],
            [
                InlineKeyboardButton(
                    text=SUBCATEGORIES["management"],
                    callback_data="sub:management"
                )
            ],
            [
                InlineKeyboardButton(
                    text=SUBCATEGORIES["ethical"],
                    callback_data="sub:ethical"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Orqaga",
                    callback_data="back:main"
                )
            ],
        ]
    )

    await callback.message.edit_text(
        f"📂 Tanlangan bo‘lim:\n"
        f"{MAIN_CATEGORIES[category_key]}\n\n"
        f"Endi masala turini tanlang:",
        reply_markup=keyboard
    )

    await callback.answer()


# =========================
# 2-BOSQICH: SUBKATEGORIYA
# =========================

@dp.callback_query(F.data.startswith("sub:"))
async def subcategory_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    sub_key = callback.data.split(":")[1]

    await state.update_data(
        subcategory=SUBCATEGORIES[sub_key]
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=COMPLAINT_TYPES["personal"],
                    callback_data="type:personal"
                )
            ],
            [
                InlineKeyboardButton(
                    text=COMPLAINT_TYPES["collective"],
                    callback_data="type:collective"
                )
            ],
            [
                InlineKeyboardButton(
                    text=COMPLAINT_TYPES["anonymous"],
                    callback_data="type:anonymous"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Orqaga",
                    callback_data="back:subcategory"
                )
            ],
        ]
    )

    await callback.message.edit_text(
        f"📂 Masala:\n"
        f"{SUBCATEGORIES[sub_key]}\n\n"
        f"Murojaat turini tanlang:",
        reply_markup=keyboard
    )

    await callback.answer()


# =========================
# 3-BOSQICH: SHIKOYAT TURI
# =========================

@dp.callback_query(F.data.startswith("type:"))
async def complaint_type_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    type_key = callback.data.split(":")[1]

    await state.update_data(
        complaint_type=COMPLAINT_TYPES[type_key],
        anonymous=(type_key == "anonymous")
    )

    await state.set_state(ComplaintState.waiting_text)

    await callback.message.edit_text(
        f"✅ {COMPLAINT_TYPES[type_key]} tanlandi.\n\n"
        "✍️ Endi murojaatingizni to‘liq yozing.\n\n"
        "Xabaringizni yuborganingizdan so‘ng u mas’ul shaxsga yetkaziladi."
    )

    await callback.answer()


# =========================
# FOYDALANUVCHI MATNI
# =========================

@dp.message(ComplaintState.waiting_text, F.text)
async def receive_complaint(message: Message, state: FSMContext):
    data = await state.get_data()

    category = data.get("category", "Nomaʼlum")
    subcategory = data.get("subcategory", "Nomaʼlum")
    complaint_type = data.get("complaint_type", "Nomaʼlum")
    anonymous = data.get("anonymous", False)

    user_text = message.text

    # =========================
    # ADMIN UCHUN XABAR
    # =========================

    if anonymous:
        admin_message = (
            "📩 YANGI ANONIM MUROJAAT\n\n"
            f"📂 Bo‘lim: {category}\n"
            f"📌 Masala: {subcategory}\n"
            f"🕶 Murojaat turi: {complaint_type}\n\n"
            f"📝 Murojaat matni:\n"
            f"{user_text}"
        )
    else:
        username = (
            f"@{message.from_user.username}"
            if message.from_user.username
            else "Username yo‘q"
        )

        full_name = message.from_user.full_name

        admin_message = (
            "📩 YANGI MUROJAAT\n\n"
            f"👤 F.I.Sh / Ism: {full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 Chat ID: {message.from_user.id}\n\n"
            f"📂 Bo‘lim: {category}\n"
            f"📌 Masala: {subcategory}\n"
            f"📄 Murojaat turi: {complaint_type}\n\n"
            f"📝 Murojaat matni:\n"
            f"{user_text}"
        )

    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )

        await message.answer(
            "✅ Murojaatingiz muvaffaqiyatli yuborildi.\n\n"
            "Rahmat. Sizning murojaatingiz mas’ul shaxsga yetkazildi."
        )

    except Exception as e:
        logging.exception("Admin xabarini yuborishda xato: %s", e)

        await message.answer(
            "❌ Murojaatni yuborishda xatolik yuz berdi. "
            "Iltimos, keyinroq qayta urinib ko‘ring."
        )

    await state.clear()

    # Asosiy menyuga qaytish
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Asosiy menyu",
                    callback_data="back:main"
                )
            ]
        ]
    )

    await message.answer(
        "Boshqa murojaat yuborish uchun:",
        reply_markup=keyboard
    )


# =========================
# ORQAGA: ASOSIY MENYU
# =========================

@dp.callback_query(F.data == "back:main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["education"],
                    callback_data="cat:education"
                )
            ],
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["admin"],
                    callback_data="cat:admin"
                )
            ],
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["labor"],
                    callback_data="cat:labor"
                )
            ],
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["ethics"],
                    callback_data="cat:ethics"
                )
            ],
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["corruption"],
                    callback_data="cat:corruption"
                )
            ],
            [
                InlineKeyboardButton(
                    text=MAIN_CATEGORIES["other"],
                    callback_data="cat:other"
                )
            ],
        ]
    )

    await callback.message.edit_text(
        "📋 Murojaat bo‘limini tanlang:",
        reply_markup=keyboard
    )

    await callback.answer()


# =========================
# ORQAGA: SUBKATEGORIYA
# =========================

@dp.callback_query(F.data == "back:subcategory")
async def back_to_subcategory(
    callback: CallbackQuery,
    state: FSMContext
):
    data = await state.get_data()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=SUBCATEGORIES["conflict"],
                    callback_data="sub:conflict"
                )
            ],
            [
                InlineKeyboardButton(
                    text=SUBCATEGORIES["management"],
                    callback_data="sub:management"
                )
            ],
            [
                InlineKeyboardButton(
                    text=SUBCATEGORIES["ethical"],
                    callback_data="sub:ethical"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Orqaga",
                    callback_data="back:main"
                )
            ],
        ]
    )

    await callback.message.edit_text(
        f"📂 Bo‘lim:\n{data.get('category', 'Nomaʼlum')}\n\n"
        "Masala turini tanlang:",
        reply_markup=keyboard
    )

    await callback.answer()


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

async def main():
    logging.basicConfig(level=logging.INFO)

    print("✅ Bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
