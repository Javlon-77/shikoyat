import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("8363022038"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class ComplaintState(StatesGroup):
    waiting_text = State()


MAIN_CATEGORIES = {
    "education": "🎓 Taʼlim jarayoni bilan bogʻliq",
    "admin": "🏢 Maʼmuriy-tashkiliy",
    "labor": "👷 Mehnat munosabatlari",
    "ethics": "🤝 Axloq-odob va hurmat meʼyorlarining buzilishi",
    "corruption": "⚠️ Korrupsiyaga oid alomatlar",
    "other": "📌 Boshqa masalalar",
}

SUBCATEGORIES = {
    "conflict": "⚖️ Nizolar",
    "management": "🏛 Boshqaruvdagi nuqsonlar",
    "ethical": "🚫 Etik buzilishlar",
}

COMPLAINT_TYPES = {
    "personal": "👤 Shaxsiy shikoyat",
    "collective": "👥 Jamoaviy shikoyat",
    "anonymous": "🕶 Anonim murojaat",
}


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=MAIN_CATEGORIES["education"], callback_data="cat:education")],
        [InlineKeyboardButton(text=MAIN_CATEGORIES["admin"], callback_data="cat:admin")],
        [InlineKeyboardButton(text=MAIN_CATEGORIES["labor"], callback_data="cat:labor")],
        [InlineKeyboardButton(text=MAIN_CATEGORIES["ethics"], callback_data="cat:ethics")],
        [InlineKeyboardButton(text=MAIN_CATEGORIES["corruption"], callback_data="cat:corruption")],
        [InlineKeyboardButton(text=MAIN_CATEGORIES["other"], callback_data="cat:other")],
    ])


def subcategory_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=SUBCATEGORIES["conflict"], callback_data="sub:conflict")],
        [InlineKeyboardButton(text=SUBCATEGORIES["management"], callback_data="sub:management")],
        [InlineKeyboardButton(text=SUBCATEGORIES["ethical"], callback_data="sub:ethical")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main")],
    ])


def complaint_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=COMPLAINT_TYPES["personal"], callback_data="type:personal")],
        [InlineKeyboardButton(text=COMPLAINT_TYPES["collective"], callback_data="type:collective")],
        [InlineKeyboardButton(text=COMPLAINT_TYPES["anonymous"], callback_data="type:anonymous")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:subcategory")],
    ])


@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Assalomu alaykum!\n\nMurojaat bo‘limini tanlang:",
        reply_markup=main_keyboard(),
    )


@dp.callback_query(F.data.startswith("cat:"))
async def category_handler(callback: CallbackQuery, state: FSMContext):
    category_key = callback.data.split(":", 1)[1]
    await state.update_data(category=MAIN_CATEGORIES[category_key])

    await callback.message.edit_text(
        f"📂 Tanlangan bo‘lim:\n{MAIN_CATEGORIES[category_key]}\n\nMasala turini tanlang:",
        reply_markup=subcategory_keyboard(),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("sub:"))
async def subcategory_handler(callback: CallbackQuery, state: FSMContext):
    sub_key = callback.data.split(":", 1)[1]
    await state.update_data(subcategory=SUBCATEGORIES[sub_key])

    await callback.message.edit_text(
        f"📂 Masala:\n{SUBCATEGORIES[sub_key]}\n\nMurojaat turini tanlang:",
        reply_markup=complaint_type_keyboard(),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("type:"))
async def complaint_type_handler(callback: CallbackQuery, state: FSMContext):
    type_key = callback.data.split(":", 1)[1]
    await state.update_data(
        complaint_type=COMPLAINT_TYPES[type_key],
        anonymous=(type_key == "anonymous"),
    )
    await state.set_state(ComplaintState.waiting_text)

    await callback.message.edit_text(
        f"✅ {COMPLAINT_TYPES[type_key]} tanlandi.\n\n"
        "✍️ Endi murojaatingizni to‘liq yozing.\n\n"
        "Murojaatni yuborganingizdan so‘ng u mas’ul shaxsga yetkaziladi."
    )
    await callback.answer()


@dp.message(ComplaintState.waiting_text, F.text)
async def receive_complaint(message: Message, state: FSMContext):
    data = await state.get_data()
    category = data.get("category", "Nomaʼlum")
    subcategory = data.get("subcategory", "Nomaʼlum")
    complaint_type = data.get("complaint_type", "Nomaʼlum")
    anonymous = data.get("anonymous", False)
    user_text = message.text.strip()

    if not user_text:
        await message.answer("⚠️ Murojaat matni bo‘sh bo‘lmasligi kerak. Qaytadan yozing.")
        return

    if anonymous:
        admin_message = (
            "📩 YANGI ANONIM MUROJAAT\n\n"
            f"📂 Bo‘lim: {category}\n"
            f"📌 Masala: {subcategory}\n"
            f"🕶 Murojaat turi: {complaint_type}\n\n"
            f"📝 Murojaat matni:\n{user_text}"
        )
    else:
        username = f"@{message.from_user.username}" if message.from_user.username else "Username yo‘q"
        admin_message = (
            "📩 YANGI MUROJAAT\n\n"
            f"👤 F.I.Sh / Ism: {message.from_user.full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 Chat ID: {message.from_user.id}\n\n"
            f"📂 Bo‘lim: {category}\n"
            f"📌 Masala: {subcategory}\n"
            f"📄 Murojaat turi: {complaint_type}\n\n"
            f"📝 Murojaat matni:\n{user_text}"
        )

    try:
        await bot.send_message(ADMIN_CHAT_ID, admin_message)
    except Exception:
        logging.exception("Admin xabarini yuborishda xato")
        await message.answer(
            "❌ Murojaatni yuborishda xatolik yuz berdi.\n"
            "Admin botga /start yuborganini tekshiring."
        )
        return

    await state.clear()
    await message.answer(
        "✅ Murojaatingiz muvaffaqiyatli yuborildi.\n\n"
        "Rahmat. Murojaatingiz mas’ul shaxsga yetkazildi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back:main")]
        ]),
    )


@dp.callback_query(F.data == "back:main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "📋 Murojaat bo‘limini tanlang:",
        reply_markup=main_keyboard(),
    )
    await callback.answer()


@dp.callback_query(F.data == "back:subcategory")
async def back_to_subcategory(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text(
        f"📂 Bo‘lim:\n{data.get('category', 'Nomaʼlum')}\n\nMasala turini tanlang:",
        reply_markup=subcategory_keyboard(),
    )
    await callback.answer()


async def main():
    logging.basicConfig(level=logging.INFO)
    print("✅ Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
