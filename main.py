import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Update

# --- НАСТРОЙКИ (ВСТАВЬ СВОИ ДАННЫЕ) ---
TOKEN = '8381035959:AAFggEA6wuLgsxK7xCHa6WGLWg7vN0n4zGA'
ADMIN_ID = 8352512372
GROUP_ID = -1003562115857
# Твой домен из панели Koyeb (без / в конце)
BASE_URL = "https://confident-maggi-infouzbot-1847c816.koyeb.app"

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- СОСТОЯНИЯ ---
class Form(StatesGroup):
    niche = State()
    description = State()
    budget = State()
    phone = State()
    name = State()

# --- КЛАВИАТУРЫ ---
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Заказать сайт", callback_data="pre_order")],
        [InlineKeyboardButton(text="🔥 Примеры работ", callback_data="cases")],
        [InlineKeyboardButton(text="📱 Связаться со мной", callback_data="contacts")]
    ])

def pre_order_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Начать заполнение", callback_data="start_filling")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="to_main")]
    ])

def budget_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="200-300$", callback_data="b200")],
        [InlineKeyboardButton(text="350-500$", callback_data="b350")],
        [InlineKeyboardButton(text="800-1000$", callback_data="b800")],
        [InlineKeyboardButton(text="⏩ Пропустить", callback_data="bskip")]
    ])

def get_welcome_text():
    return (
        "🤖 **Добро пожаловать! Я — твой интерактивный помощник.**\n\n"
        "**В этом боте вы можете:**\n"
        "🔹 **Оставить заявку** на разработку сайта, ответив на вопросы.\n"
        "🔹 **Посмотреть портфолио** и мои реальные кейсы.\n"
        "🔹 **Получить контакты** для быстрой связи.\n\n"
        "Выберите нужный раздел ниже:"
    )

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(get_welcome_text(), reply_markup=main_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(get_welcome_text(), reply_markup=main_kb(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "contacts")
async def show_contacts(callback: CallbackQuery):
    text = (
        "📱 **Мои контакты и ресурсы:**\n\n"
        "📞 **Телефон:** +998338886898\n"
        "🌐 **Личный сайт:** [ceors.duckdns.org](https://ceors.duckdns.org)\n"
        "🏢 **Сайт студии:** [devu.uz](https://devu.uz)\n\n"
        "💬 **Telegram:** @nevps\n"
        "📸 **Instagram:** [seosfv](https://instagram.com/seosfv)"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 Меню", callback_data="to_main")]])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=True)
    await callback.answer()

@dp.callback_query(F.data == "cases")
async def show_cases(callback: CallbackQuery):
    text = (
        "🔥 **Примеры моих работ:**\n\n"
        "🌐 **Сайт студии:** https://devu.uz\n"
        "🚀 **Мой личный сайт:** https://ceors.duckdns.org\n\n"
        "Хотите обсудить ваш проект?"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Заказать", callback_data="pre_order")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="to_main")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "pre_order")
async def pre_order(callback: CallbackQuery):
    text = "📝 **Оформление заявки**\n\nОтветьте на вопросы, чтобы я быстрее подготовил предложение."
    await callback.message.edit_text(text, reply_markup=pre_order_kb(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "start_filling")
async def start_filling(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("1️⃣ **Какая тематика сайта?**", parse_mode="Markdown")
    await state.set_state(Form.niche)
    await callback.answer()

@dp.message(Form.niche)
async def process_niche(message: types.Message, state: FSMContext):
    await state.update_data(niche=message.text)
    await message.answer("2️⃣ **Опишите ваш сайт и пожелания:**")
    await state.set_state(Form.description)

@dp.message(Form.description)
async def process_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("3️⃣ **Выберите примерный бюджет:**", reply_markup=budget_kb())
    await state.set_state(Form.budget)

@dp.callback_query(Form.budget)
async def process_budget(callback: CallbackQuery, state: FSMContext):
    budgets = {"b200": "200-300$", "b350": "350-500$", "b800": "800-1000$", "bskip": "Пропущен"}
    await state.update_data(budget=budgets[callback.data])
    await callback.message.edit_text(f"✅ Бюджет: {budgets[callback.data]}")
    await callback.message.answer("4️⃣ **Введите ваш номер телефона:**")
    await state.set_state(Form.phone)
    await callback.answer()

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("5️⃣ **Как к вам обращаться?**")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    summary = (
        f"🏁 **Проверьте заявку:**\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📁 Тематика: {data['niche']}\n"
        f"💰 Бюджет: {data['budget']}\n"
        f"📞 Телефон: {data['phone']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить!", callback_data="confirm")],
        [InlineKeyboardButton(text="🔄 Заполнить заново", callback_data="start_filling")]
    ])
    await message.answer(summary, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "confirm")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    admin_msg = (
        f"🚀 **НОВАЯ ЗАЯВКА**\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📁 Ниша: {data['niche']}\n"
        f"💰 Бюджет: {data['budget']}\n"
        f"📞 Тел: {data['phone']}\n"
        f"📝 Описание: {data.get('description', 'Нет описания')}\n"
        f"🔗 Юзер: @{callback.from_user.username if callback.from_user.username else 'нет'}"
    )
    
    try:
        await bot.send_message(ADMIN_ID, admin_msg)
        await bot.send_message(GROUP_ID, admin_msg)
    except Exception as e:
        logging.error(f"Ошибка отправки уведомлений: {e}")

    await callback.message.edit_text("🎉 **Заявка успешно отправлена!**", parse_mode="Markdown")
    success_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 В меню", callback_data="to_main")]])
    await callback.message.answer("Вы можете вернуться в начало:", reply_markup=success_kb)
    
    await state.clear()
    await callback.answer()

# --- ЛОГИКА ВЕБХУКА (FastAPI) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # drop_pending_updates=True удаляет сообщения, пришедшие, пока бот лежал
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    logging.info(f"Вебхук установлен на {WEBHOOK_URL}")
    yield
    # При перезагрузке не удаляем вебхук, чтобы он не пропадал
    # await bot.delete_webhook()  <-- закомментируй эту строку

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def index():
    return "Bot is running!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

