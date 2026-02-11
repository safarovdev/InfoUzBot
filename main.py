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

# --- НАСТРОЙКИ ---
TOKEN = '8381035959:AAGJKrNcU8APOFEz4GjTsf-zKsMrWS8yTvc'
ADMIN_ID = 8352512372
GROUP_ID = -1003562115857
# В Koyeb URL будет вида: https://имя-приложения-сгенерированное.koyeb.app
# Но мы подтянем его автоматически позже или укажем вручную
BASE_URL = "https://confident-maggi-infouzbot-1847c816.koyeb.app" 

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- ТВОЯ ЛОГИКА СОСТОЯНИЙ И КЛАВИАТУР ---
class Form(StatesGroup):
    niche, description, budget, phone, name = State(), State(), State(), State(), State()

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Заказать сайт", callback_data="pre_order")],
        [InlineKeyboardButton(text="🔥 Примеры работ", callback_data="cases")],
        [InlineKeyboardButton(text="📱 Связаться со мной", callback_data="contacts")]
    ])

# ... (остальные функции клавиатур budget_kb, pre_order_kb оставь как были) ...
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

# --- ОБРАБОТЧИКИ (Копируем твою логику) ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = "🤖 **Добро пожаловать!**\n\nЯ помогу заказать сайт или связаться с разработчиком."
    await message.answer(text, reply_markup=main_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "contacts")
async def show_contacts(callback: CallbackQuery):
    text = "📱 **Мои контакты:**\n\n📞 +998338886898\n🌐 [devu.uz](https://devu.uz)"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏠 Меню", callback_data="to_main")]]), parse_mode="Markdown")

# ... (Сюда добавь все остальные обработчики: cases, pre_order, process_niche и т.д. из прошлого кода) ...
# ВАЖНО: В функции confirm_order оставь логику отправки в группу и админу.

@dp.callback_query(F.data == "to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Главное меню:", reply_markup=main_kb())
    await callback.answer()

# --- ЛОГИКА ВЕБХУКА (FastAPI) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При запуске устанавливаем вебхук
    # URL_APP подставится из переменных окружения Koyeb (нужно будет добавить в панель)
    webhook_url = f"https://{APP_NAME}.koyeb.app{WEBHOOK_PATH}" 
    await bot.set_webhook(url=webhook_url)
    yield
    # При выключении удаляем вебхук
    await bot.delete_webhook()

app = FastAPI(lifespan=lifespan)
APP_NAME = "infouzbot" # Замени на имя своего сервиса в Koyeb

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def index():
    return "Bot is running!"

# Запуск для локального теста или через uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

