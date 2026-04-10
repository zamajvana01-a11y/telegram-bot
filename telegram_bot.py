import asyncio
import json
import os
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "7139683001:AAH7OcXdDSSAGe6fEJuFhjPWuf5Wt4j2wBI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "users.json"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def init_user(user_id, username):
    users = load_users()
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {
            "id": user_id,
            "name": username or f"Игрок{user_id}",
            "balance": 5000,
            "bank": 0,
            "last_daily": 0
        }
        save_users(users)
    return users[user_id]

def save_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="🏦 Банк")],
        [KeyboardButton(text="⚽ Футбол"), KeyboardButton(text="🎯 Дартс")],
        [KeyboardButton(text="🎁 Бонус"), KeyboardButton(text="⭐ Профиль")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "✨ Добро пожаловать!\n\n"
        "💰 Баланс - проверить деньги\n"
        "🏦 Банк - пополнить/снять\n"
        "⚽ Футбол - сыграть\n"
        "🎯 Дартс - сыграть\n"
        "🎁 Бонус - получить бонус\n"
        "⭐ Профиль - твоя статистика",
        reply_markup=main_keyboard
    )

@dp.message(lambda msg: msg.text == "💰 Баланс")
async def show_balance(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(f"💰 Твой баланс: {user['balance']} ₽")

@dp.message(lambda msg: msg.text == "🏦 Банк")
async def bank_menu(message: types.Message):
    await message.answer(
        "🏦 БАНК\n\n"
        "• `Банк пополнить 1000` - положить деньги\n"
        "• `Банк снять 500` - снять деньги (налог 4%)"
    )

@dp.message(lambda msg: msg.text.startswith("Банк пополнить"))
async def bank_deposit(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ Пример: Банк пополнить 1000")
        return
    try:
        amount = int(parts[2])
    except:
        await message.answer("❌ Введи число!")
        return
    user = init_user(message.from_user.id, message.from_user.username)
    if user['balance'] < amount:
        await message.answer(f"❌ Не хватает! У тебя {user['balance']} ₽")
        return
    user['balance'] -= amount
    user['bank'] = user.get('bank', 0) + amount
    save_user(message.from_user.id, user)
    await message.answer(f"✅ +{amount} ₽ в банк!\n💰 На руках: {user['balance']} ₽\n🏦 В банке: {user['bank']} ₽")

@dp.message(lambda msg: msg.text.startswith("Банк снять"))
async def bank_withdraw(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ Пример: Банк снять 1000")
        return
    try:
        amount = int(parts[2])
    except:
        await message.answer("❌ Введи число!")
        return
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('bank', 0) < amount:
        await message.answer(f"❌ В банке только {user.get('bank', 0)} ₽")
        return
    tax = int(amount * 0.04)
    final = amount - tax
    user['bank'] -= amount
    user['balance'] += final
    save_user(message.from_user.id, user)
    await message.answer(f"✅ -{amount} ₽ из банка!\n💱 Налог: {tax} ₽ (4%)\n💰 Получено: {final} ₽")

# ФУТБОЛ
@dp.message(lambda msg: msg.text == "⚽ Футбол")
async def football_menu(message: types.Message):
    await message.answer(
        "⚽ ФУТБОЛ\n\n"
        "💰 Введи сумму ставки: `!ф 100`\n\n"
        "🎯 Шанс: 45%\n"
        "🏆 Выигрыш: x2.2"
    )

@dp.message(lambda msg: msg.text.startswith("!ф"))
async def football_game(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: `!ф 100`")
        return
    try:
        bet = int(parts[1])
    except:
        await message.answer("❌ Введи сумму числом!")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    if bet < 1:
        await message.answer("❌ Минимальная ставка: 1 ₽")
        return
    if bet > user['balance']:
        await message.answer(f"❌ Не хватает! У тебя {user['balance']} ₽")
        return
    
    win = random.random() < 0.45
    await message.answer("⚽ Удар...")
    await asyncio.sleep(1)
    
    if win:
        win_amount = int(bet * 2.2)
        user['balance'] += win_amount
        save_user(message.from_user.id, user)
        await message.answer(f"✅ ГОЛ! ПОБЕДА!\n💰 +{win_amount} ₽")
    else:
        user['balance'] -= bet
        save_user(message.from_user.id, user)
        await message.answer(f"❌ МИМО! ПРОИГРЫШ!\n💰 -{bet} ₽")

# ДАРТС
@dp.message(lambda msg: msg.text == "🎯 Дартс")
async def darts_menu(message: types.Message):
    await message.answer(
        "🎯 ДАРТС\n\n"
        "💰 Введи сумму ставки: `!д 100`\n\n"
        "🎯 Шанс: 40%\n"
        "🏆 Выигрыш: x2.5"
    )

@dp.message(lambda msg: msg.text.startswith("!д"))
async def darts_game(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: `!д 100`")
        return
    try:
        bet = int(parts[1])
    except:
        await message.answer("❌ Введи сумму числом!")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    if bet < 1:
        await message.answer("❌ Минимальная ставка: 1 ₽")
        return
    if bet > user['balance']:
        await message.answer(f"❌ Не хватает! У тебя {user['balance']} ₽")
        return
    
    win = random.random() < 0.40
    await message.answer("🎯 Бросок...")
    await asyncio.sleep(1)
    
    if win:
        win_amount = int(bet * 2.5)
        user['balance'] += win_amount
        save_user(message.from_user.id, user)
        await message.answer(f"✅ ПОПАЛ! ПОБЕДА!\n💰 +{win_amount} ₽")
    else:
        user['balance'] -= bet
        save_user(message.from_user.id, user)
        await message.answer(f"❌ МИМО! ПРОИГРЫШ!\n💰 -{bet} ₽")

@dp.message(lambda msg: msg.text == "🎁 Бонус")
async def daily_bonus(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if now - user.get('last_daily', 0) < 86400:
        left = int(24 - (now - user.get('last_daily', 0)) // 3600)
        await message.answer(f"⏰ Бонус через {left} часов")
        return
    bonus = 500
    user['balance'] += bonus
    user['last_daily'] = now
    save_user(message.from_user.id, user)
    await message.answer(f"🎁 +{bonus} ₽!\n💰 Баланс: {user['balance']} ₽")

@dp.message(lambda msg: msg.text == "⭐ Профиль")
async def profile(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"👤 ПРОФИЛЬ\n\n"
        f"📛 Ник: {user['name']}\n"
        f"💰 Баланс: {user['balance']} ₽\n"
        f"🏦 В банке: {user.get('bank', 0)} ₽"
    )

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
