import asyncio
import json
import os
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = ""7139683001:AAH7OcXdDSSAGe6fEJuFhjPWuf5Wt4j2wBI"

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
            "bank_level": 1,
            "last_daily": 0,
            "total_bets": 0,
            "total_wins": 0,
            "invited": 0,
            "premium": 0
        }
        save_users(users)
    return users[user_id]

def save_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

def get_bank_percent(level):
    return round(0.1 + (level - 1) * 0.05, 2)

def get_upgrade_cost(level):
    return 80000 + (level - 1) * 20000

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="🏦 Банк")],
        [KeyboardButton(text="⚽ Футбол"), KeyboardButton(text="🎯 Дартс")],
        [KeyboardButton(text="🎁 Бонус"), KeyboardButton(text="👤 Моя статистика")]
    ],
    resize_keyboard=True
)

bank_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📈 Прокачать банк", callback_data="upgrade_bank")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
])

@dp.message(Command("start"))
async def start(message: types.Message):
    init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "✨ Добро пожаловать!\n\n"
        "💰 Баланс - проверить деньги\n"
        "🏦 Банк - банковская система\n"
        "⚽ Футбол - сыграть\n"
        "🎯 Дартс - сыграть\n"
        "🎁 Бонус - получить бонус\n"
        "👤 Моя статистика - твоя статистика",
        reply_markup=main_keyboard
    )

@dp.message(lambda msg: msg.text == "💰 Баланс")
async def show_balance(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(f"💰 Твой баланс: {user['balance']} ₽")

# ============ БАНК ============
@dp.message(lambda msg: msg.text == "🏦 Банк")
async def bank_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    name = user.get('name', 'Игрок')
    percent = get_bank_percent(user['bank_level'])
    upgrade_cost = get_upgrade_cost(user['bank_level'])
    
    bank_text = f"""👨🏼‍✈️ **{name}**: /bank

Бот для развлечения 🥃
💵 Баланс в банке: {user['bank']}
📊 Процент ставки: {percent}%
🏦 Уровень банка: {user['bank_level']}

📥 Пополнить счет - `!банкввод [сумма]`
📤 Вывести - `!банквывод [сумма]`

━━━━━━━━━━━━━━━━━━━━━
📈 Стоимость прокачки: {upgrade_cost} ₽
━━━━━━━━━━━━━━━━━━━━━"""
    
    await message.answer(bank_text, parse_mode="Markdown", reply_markup=bank_keyboard)

@dp.callback_query(lambda c: c.data == "upgrade_bank")
async def upgrade_bank(callback: types.CallbackQuery):
    user = init_user(callback.from_user.id, callback.from_user.username)
    cost = get_upgrade_cost(user['bank_level'])
    
    if user['balance'] >= cost:
        user['balance'] -= cost
        user['bank_level'] += 1
        save_user(callback.from_user.id, user)
        new_percent = get_bank_percent(user['bank_level'])
        next_cost = get_upgrade_cost(user['bank_level'])
        
        await callback.message.answer(
            f"✅ **БАНК ПРОКАЧАН!**\n\n"
            f"📈 Новый уровень: {user['bank_level']}\n"
            f"📊 Новый процент: {new_percent}%\n"
            f"💰 Следующая прокачка: {next_cost} ₽",
            parse_mode="Markdown"
        )
    else:
        need = cost - user['balance']
        await callback.message.answer(
            f"❌ **НЕ ХВАТАЕТ ДЕНЕГ!**\n\n"
            f"💰 Нужно: {cost} ₽\n"
            f"💸 Не хватает: {need} ₽",
            parse_mode="Markdown"
        )
    await callback.answer()

@dp.message(lambda msg: msg.text.startswith("!банкввод"))
async def bank_deposit(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: `!банкввод 1000`", parse_mode="Markdown")
        return
    try:
        amount = int(parts[1])
    except:
        await message.answer("❌ Введи число!", parse_mode="Markdown")
        return
    if amount < 1:
        await message.answer("❌ Минимальная сумма: 1 ₽", parse_mode="Markdown")
        return
    user = init_user(message.from_user.id, message.from_user.username)
    if user['balance'] < amount:
        await message.answer(f"❌ Не хватает! У тебя {user['balance']} ₽", parse_mode="Markdown")
        return
    user['balance'] -= amount
    user['bank'] += amount
    save_user(message.from_user.id, user)
    await message.answer(f"✅ +{amount} ₽ в банк!\n💰 На руках: {user['balance']} ₽\n🏦 В банке: {user['bank']} ₽", parse_mode="Markdown")

@dp.message(lambda msg: msg.text.startswith("!банквывод"))
async def bank_withdraw(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: `!банквывод 1000`", parse_mode="Markdown")
        return
    try:
        amount = int(parts[1])
    except:
        await message.answer("❌ Введи число!", parse_mode="Markdown")
        return
    if amount < 1:
        await message.answer("❌ Минимальная сумма: 1 ₽", parse_mode="Markdown")
        return
    user = init_user(message.from_user.id, message.from_user.username)
    if user['bank'] < amount:
        await message.answer(f"❌ В банке только {user['bank']} ₽", parse_mode="Markdown")
        return
    tax = int(amount * 0.04)
    final = amount - tax
    user['bank'] -= amount
    user['balance'] += final
    save_user(message.from_user.id, user)
    await message.answer(f"✅ -{amount} ₽ из банка!\n💱 Налог: {tax} ₽ (4%)\n💰 Получено: {final} ₽", parse_mode="Markdown")

# ============ ФУТБОЛ ============
@dp.message(lambda msg: msg.text == "⚽ Футбол")
async def football_menu(message: types.Message):
    await message.answer(
        "⚽ ФУТБОЛ\n\n"
        "💰 Введи сумму ставки: `!ф 100`\n\n"
        "🎯 Шанс: 45%\n"
        "🏆 Выигрыш: x2.2",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text.startswith("!ф"))
async def football_game(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: `!ф 100`", parse_mode="Markdown")
        return
    try:
        bet = int(parts[1])
    except:
        await message.answer("❌ Введи сумму числом!", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    if bet < 1:
        await message.answer("❌ Минимальная ставка: 1 ₽", parse_mode="Markdown")
        return
    if bet > user['balance']:
        await message.answer(f"❌ Не хватает! У тебя {user['balance']} ₽", parse_mode="Markdown")
        return
    
    win = random.random() < 0.45
    await message.answer("⚽ Удар...", parse_mode="Markdown")
    await asyncio.sleep(1)
    
    if win:
        win_amount = int(bet * 2.2)
        user['balance'] += win_amount
        user['total_bets'] += 1
        user['total_wins'] += 1
        save_user(message.from_user.id, user)
        await message.answer(f"✅ ГОЛ! ПОБЕДА!\n💰 +{win_amount} ₽", parse_mode="Markdown")
    else:
        user['balance'] -= bet
        user['total_bets'] += 1
        save_user(message.from_user.id, user)
        await message.answer(f"❌ МИМО! ПРОИГРЫШ!\n💰 -{bet} ₽", parse_mode="Markdown")

# ============ ДАРТС ============
@dp.message(lambda msg: msg.text == "🎯 Дартс")
async def darts_menu(message: types.Message):
    await message.answer(
        "🎯 ДАРТС\n\n"
        "💰 Введи сумму ставки: `!д 100`\n\n"
        "🎯 Шанс: 40%\n"
        "🏆 Выигрыш: x2.5",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text.startswith("!д"))
async def darts_game(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: `!д 100`", parse_mode="Markdown")
        return
    try:
        bet = int(parts[1])
    except:
        await message.answer("❌ Введи сумму числом!", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    if bet < 1:
        await message.answer("❌ Минимальная ставка: 1 ₽", parse_mode="Markdown")
        return
    if bet > user['balance']:
        await message.answer(f"❌ Не хватает! У тебя {user['balance']} ₽", parse_mode="Markdown")
        return
    
    win = random.random() < 0.40
    await message.answer("🎯 Бросок...", parse_mode="Markdown")
    await asyncio.sleep(1)
    
    if win:
        win_amount = int(bet * 2.5)
        user['balance'] += win_amount
        user['total_bets'] += 1
        user['total_wins'] += 1
        save_user(message.from_user.id, user)
        await message.answer(f"✅ ПОПАЛ! ПОБЕДА!\n💰 +{win_amount} ₽", parse_mode="Markdown")
    else:
        user['balance'] -= bet
        user['total_bets'] += 1
        save_user(message.from_user.id, user)
        await message.answer(f"❌ МИМО! ПРОИГРЫШ!\n💰 -{bet} ₽", parse_mode="Markdown")

# ============ БОНУС ============
@dp.message(lambda msg: msg.text == "🎁 Бонус")
async def daily_bonus(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if now - user.get('last_daily', 0) < 86400:
        left = int(24 - (now - user.get('last_daily', 0)) // 3600)
        await message.answer(f"⏰ Бонус через {left} часов", parse_mode="Markdown")
        return
    bonus = 500
    user['balance'] += bonus
    user['last_daily'] = now
    save_user(message.from_user.id, user)
    await message.answer(f"🎁 +{bonus} ₽!\n💰 Баланс: {user['balance']} ₽", parse_mode="Markdown")

# ============ СТАТИСТИКА ============
@dp.message(lambda msg: msg.text == "👤 Моя статистика")
async def my_stats(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    
    premium = "❌ Нет" if user.get('premium', 0) == 0 else f"✅ {user.get('premium', 0)} 💎"
    balance = user['balance']
    bank_level = user.get('bank_level', 1)
    total_bets = user.get('total_bets', 0)
    total_wins = user.get('total_wins', 0)
    invited = user.get('invited', 0)
    
    users = load_users()
    sorted_users = sorted(users.values(), key=lambda x: x['balance'], reverse=True)
    top_position = 1
    for i, u in enumerate(sorted_users, 1):
        if str(u['id']) == str(message.from_user.id):
            top_position = i
            break
    
    stats_text = f"""🏆 **BMW СТАТИСТИКА** 🏆
━━━━━━━━━━━━━━━━━━━━━
👤 **{user['name']}**
━━━━━━━━━━━━━━━━━━━━━
👑 Премиум: {premium}
💵 Баланс: {balance:,}$
🏆 Место в топе: {top_position}
🏦 Уровень банка: {bank_level}
🍀 Всего ставок: {total_bets}
🏆 Побед: {total_wins}
👥 Приглашено: {invited}
━━━━━━━━━━━━━━━━━━━━━
🚗 **BMW M5 COMPETITION** 🚗
━━━━━━━━━━━━━━━━━━━━━
💡 Играй и повышай статистику!
━━━━━━━━━━━━━━━━━━━━━"""
    
    await message.answer(stats_text, parse_mode="Markdown")

# ============ НАЗАД ============
@dp.callback_query(lambda c: c.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.answer("◀️ Главное меню", reply_markup=main_keyboard)
    await callback.answer()

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
