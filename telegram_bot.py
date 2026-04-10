import asyncio
import json
import os
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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
            "bank_level": 1,
            "limit_level": 1,
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

def get_bank_upgrade_cost(level):
    return 80000 + (level - 1) * 20000

def get_limit_upgrade_cost(level):
    return 50000 + (level - 1) * 10000

def get_max_transfer(level):
    return 100000 + (level - 1) * 50000

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="🏦 Банк")],
        [KeyboardButton(text="⚽ Футбол"), KeyboardButton(text="🎯 Дартс")],
        [KeyboardButton(text="🎁 Бонус"), KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="🏆 Топ"), KeyboardButton(text="🔄 Перевести")]
    ],
    resize_keyboard=True
)

bank_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📈 Прокачать банк", callback_data="upgrade_bank")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
])

limit_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📈 Прокачать лимит", callback_data="upgrade_limit")],
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
        "👤 Профиль - твоя статистика\n"
        "🏆 Топ - лучшие игроки\n"
        "🔄 Перевести - перевод денег игроку",
        reply_markup=main_keyboard
    )

@dp.message(lambda msg: msg.text == "💰 Баланс")
async def show_balance(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(f"💰 Твой баланс: {user['balance']} ₽\n🏦 В банке: {user['bank']} ₽")

# ============ БАНК ============
@dp.message(lambda msg: msg.text == "🏦 Банк")
async def bank_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    name = user.get('name', 'Игрок')
    percent = get_bank_percent(user['bank_level'])
    upgrade_cost = get_bank_upgrade_cost(user['bank_level'])
    
    bank_text = f"""👨🏼‍✈️ **{name}**: /bank

Бот для развлечения 🥃
💵 Баланс в банке: {user['bank']} ₽
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
    cost = get_bank_upgrade_cost(user['bank_level'])
    
    if user['balance'] >= cost:
        user['balance'] -= cost
        user['bank_level'] += 1
        save_user(callback.from_user.id, user)
        new_percent = get_bank_percent(user['bank_level'])
        next_cost = get_bank_upgrade_cost(user['bank_level'])
        
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

# ============ ТОП ИГРОКОВ ============
@dp.message(lambda msg: msg.text == "🏆 Топ")
async def top_players(message: types.Message):
    users = load_users()
    name = init_user(message.from_user.id, message.from_user.username).get('name', 'Игрок')
    
    # Собираем только реальных игроков (у кого есть ставки или баланс > 5000)
    real_players = []
    for uid, data in users.items():
        if data.get('total_bets', 0) > 0 or data.get('balance', 0) > 5000:
            real_players.append({
                "name": data.get('name', f"Игрок{uid[:4]}"),
                "balance": data.get('balance', 0)
            })
    
    # Сортируем по балансу
    real_players.sort(key=lambda x: x['balance'], reverse=True)
    
    # Формируем топ-10
    top_text = f"👨🏼‍✈️ **{name}**: /top\n\nБот для развлечения 🥃\n"
    for i, player in enumerate(real_players[:10], 1):
        top_text += f"{i}. {player['name']} — {player['balance']:,} ₽\n"
    
    # Находим место текущего игрока
    user_id = str(message.from_user.id)
    user_balance = init_user(message.from_user.id, message.from_user.username).get('balance', 0)
    position = 1
    for i, player in enumerate(real_players, 1):
        if player['balance'] == user_balance and player['name'] == init_user(message.from_user.id, message.from_user.username).get('name', ''):
            position = i
            break
    
    top_text += f"\n📊 Ваше место в топе: {position}"
    
    await message.answer(top_text, parse_mode="Markdown")

# ============ ПЕРЕВОД ДЕНЕГ С ЛИМИТОМ ============
@dp.message(lambda msg: msg.text == "🔄 Перевести")
async def transfer_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    max_transfer = get_max_transfer(user.get('limit_level', 1))
    upgrade_cost = get_limit_upgrade_cost(user.get('limit_level', 1))
    
    await message.answer(
        f"🔄 **ПЕРЕВОД ДЕНЕГ**\n\n"
        f"📊 Максимальный перевод: {max_transfer} ₽\n"
        f"🏦 Уровень лимита: {user.get('limit_level', 1)}\n\n"
        f"📝 Чтобы перевести деньги:\n"
        f"`перевод @username 1000`\n\n"
        f"📈 Стоимость прокачки лимита: {upgrade_cost} ₽",
        parse_mode="Markdown",
        reply_markup=limit_keyboard
    )

@dp.callback_query(lambda c: c.data == "upgrade_limit")
async def upgrade_limit(callback: types.CallbackQuery):
    user = init_user(callback.from_user.id, callback.from_user.username)
    cost = get_limit_upgrade_cost(user.get('limit_level', 1))
    
    if user['balance'] >= cost:
        user['balance'] -= cost
        user['limit_level'] = user.get('limit_level', 1) + 1
        save_user(callback.from_user.id, user)
        new_max = get_max_transfer(user['limit_level'])
        next_cost = get_limit_upgrade_cost(user['limit_level'])
        
        await callback.message.answer(
            f"✅ **ЛИМИТ ПЕРЕВОДА ПОВЫШЕН!**\n\n"
            f"📈 Новый уровень: {user['limit_level']}\n"
            f"💰 Максимальный перевод: {new_max} ₽\n"
            f"💸 Следующая прокачка: {next_cost} ₽",
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

@dp.message(lambda msg: msg.text.startswith("перевод"))
async def transfer_money(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ Пример: `перевод @username 1000`", parse_mode="Markdown")
        return
    
    target = parts[1].replace("@", "")
    try:
        amount = int(parts[2])
    except:
        await message.answer("❌ Введи сумму числом!", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    max_transfer = get_max_transfer(user.get('limit_level', 1))
    
    if amount < 1:
        await message.answer("❌ Минимальная сумма перевода: 1 ₽", parse_mode="Markdown")
        return
    if amount > max_transfer:
        await message.answer(f"❌ Максимальный перевод: {max_transfer} ₽\n📈 Повысь уровень лимита!", parse_mode="Markdown")
        return
    if amount > user['balance']:
        await message.answer(f"❌ Не хватает! У тебя {user['balance']} ₽", parse_mode="Markdown")
        return
    
    # Ищем получателя
    users = load_users()
    target_id = None
    target_name = None
    for uid, data in users.items():
        if data.get('name', '').lower() == target.lower():
            target_id = uid
            target_name = data.get('name')
            break
    
    if not target_id:
        await message.answer(f"❌ Игрок {target} не найден!", parse_mode="Markdown")
        return
    
    if target_id == str(message.from_user.id):
        await message.answer("❌ Нельзя перевести деньги самому себе!", parse_mode="Markdown")
        return
    
    # Переводим деньги
    user['balance'] -= amount
    save_user(message.from_user.id, user)
    
    target_user = init_user(target_id, target_name)
    target_user['balance'] += amount
    save_user(target_id, target_user)
    
    await message.answer(f"✅ **ПЕРЕВОД ВЫПОЛНЕН!**\n\n👤 Кому: {target_name}\n💰 Сумма: {amount} ₽\n💰 Твой баланс: {user['balance']} ₽", parse_mode="Markdown")
    await bot.send_message(int(target_id), f"✅ **Вам перевели деньги!**\n\n👤 От: {user['name']}\n💰 Сумма: {amount} ₽\n💰 Новый баланс: {target_user['balance']} ₽", parse_mode="Markdown")

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

# ============ ПРОФИЛЬ ============
@dp.message(lambda msg: msg.text == "👤 Профиль")
async def profile(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    premium = "❌ Нет" if user.get('premium', 0) == 0 else f"✅ {user.get('premium', 0)} 💎"
    
    # Место в топе
    users = load_users()
    real_players = []
    for uid, data in users.items():
        if data.get('total_bets', 0) > 0 or data.get('balance', 0) > 5000:
            real_players.append(data.get('balance', 0))
    real_players.sort(reverse=True)
    position = 1
    for bal in real_players:
        if user['balance'] < bal:
            position += 1
        else:
            break
    
    profile_text = f"""👤 **{user['name']}**

👑 Премиум: {premium}
💵 Баланс: {user['balance']:,} ₽
🏦 В банке: {user['bank']:,} ₽
🏆 Место в топе: {position}
🏦 Уровень банка: {user.get('bank_level', 1)}
📊 Лимит перевода: {get_max_transfer(user.get('limit_level', 1))} ₽
🍀 Ставок: {user.get('total_bets', 0)}
🏆 Побед: {user.get('total_wins', 0)}
👥 Приглашено: {user.get('invited', 0)}"""
    
    await message.answer(profile_text, parse_mode="Markdown")

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
