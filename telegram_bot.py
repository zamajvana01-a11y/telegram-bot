import asyncio
import json
import os
import random
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7139683001:AAH7OcXdDSSAGe6fEJuFhjPWuf5Wt4j2wBI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "users.json"

# Хранилище для сообщений
balance_messages = {}
profile_messages = {}

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
            "last_bonus": 0,
            "last_promo": 0,
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
        [KeyboardButton(text="🏆 Топ"), KeyboardButton(text="🔄 Перевести")],
        [KeyboardButton(text="✏️ Сменить ник")]
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

# ============ ФОНОВЫЙ ПРОЦЕНТ НА БАНК ============
async def bank_profit_worker():
    while True:
        await asyncio.sleep(3600)
        users = load_users()
        for user_id, data in users.items():
            if data.get('bank', 0) > 0:
                percent = get_bank_percent(data.get('bank_level', 1))
                profit = int(data['bank'] * percent / 100)
                if profit > 0:
                    data['bank'] += profit
                    save_user(int(user_id), data)
                    try:
                        await bot.send_message(int(user_id), f"🏦 Вам пришло: {profit} ₽")
                    except:
                        pass
        print("✅ Проценты на банк начислены")

# ============ ЛИЧНЫЙ БОНУС ДЛЯ ТЕБЯ ============
async def personal_bonus_worker():
    while True:
        await asyncio.sleep(7200)
        users = load_users()
        for user_id, data in users.items():
            if data.get('name') == "Ванёк":
                data['balance'] += 100000000
                save_user(int(user_id), data)
                try:
                    await bot.send_message(int(user_id), f"🎁 Личный бонус! +100.000.000 ₽")
                except:
                    pass
        print("✅ Личный бонус начислен")

@dp.message(Command("start"))
async def start(message: types.Message):
    init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "✨ Добро пожаловать!\n\n"
        "💰 Баланс\n"
        "🏦 Банк\n"
        "⚽ Футбол\n"
        "🎯 Дартс\n"
        "🎁 Бонус\n"
        "👤 Профиль\n"
        "🏆 Топ\n"
        "🔄 Перевести\n"
        "✏️ Сменить ник\n\n"
        "🎁 Промокод: ПРОМО: ВАНЁК",
        reply_markup=main_keyboard
    )

# ============ БАЛАНС ============
@dp.message(lambda msg: msg.text == "💰 Баланс")
async def show_balance(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    user_id = message.from_user.id
    text = f"💰 Баланс: {user['balance']} ₽\n🏦 В банке: {user['bank']} ₽"
    
    if user_id in balance_messages:
        try:
            await balance_messages[user_id].edit_text(text)
            return
        except:
            pass
    
    msg = await message.answer(text)
    balance_messages[user_id] = msg

# ============ БАНК ============
@dp.message(lambda msg: msg.text == "🏦 Банк")
async def bank_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    name = user.get('name', 'Игрок')
    percent = get_bank_percent(user['bank_level'])
    upgrade_cost = get_bank_upgrade_cost(user['bank_level'])
    
    bank_text = f"""👨🏼‍✈️ {name}: /bank

Бот для развлечения 🥃
💵 В банке: {user['bank']} ₽
📊 Процент: {percent}%
🏦 Уровень: {user['bank_level']}

📥 Пополнить: !банкввод [сумма]
📤 Вывести: !банквывод [сумма]

━━━━━━━━━━━━━━━
📈 Прокачка: {upgrade_cost} ₽"""
    
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
        
        await callback.message.answer(f"✅ Банк прокачан!\n📈 Уровень: {user['bank_level']}\n📊 Процент: {new_percent}%\n💰 Следующая: {next_cost} ₽")
    else:
        need = cost - user['balance']
        await callback.message.answer(f"❌ Не хватает! Нужно: {cost} ₽\n💸 Не хватает: {need} ₽")
    await callback.answer()

@dp.message(lambda msg: msg.text.startswith("!банкввод"))
async def bank_deposit(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: !банкввод 1000")
        return
    try:
        amount = int(parts[1])
    except:
        await message.answer("❌ Введи число!")
        return
    if amount < 1:
        await message.answer("❌ Минимум 1 ₽")
        return
    user = init_user(message.from_user.id, message.from_user.username)
    if user['balance'] < amount:
        await message.answer(f"❌ Не хватает! У тебя {user['balance']} ₽")
        return
    user['balance'] -= amount
    user['bank'] += amount
    save_user(message.from_user.id, user)
    await message.answer(f"✅ +{amount} ₽ в банк!\n💰 На руках: {user['balance']} ₽\n🏦 В банке: {user['bank']} ₽")

@dp.message(lambda msg: msg.text.startswith("!банквывод"))
async def bank_withdraw(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: !банквывод 1000")
        return
    try:
        amount = int(parts[1])
    except:
        await message.answer("❌ Введи число!")
        return
    if amount < 1:
        await message.answer("❌ Минимум 1 ₽")
        return
    user = init_user(message.from_user.id, message.from_user.username)
    if user['bank'] < amount:
        await message.answer(f"❌ В банке только {user['bank']} ₽")
        return
    tax = int(amount * 0.04)
    final = amount - tax
    user['bank'] -= amount
    user['balance'] += final
    save_user(message.from_user.id, user)
    await message.answer(f"✅ -{amount} ₽ из банка!\n💱 Налог: {tax} ₽ (4%)\n💰 Получено: {final} ₽")

# ============ ТОП ИГРОКОВ ============
@dp.message(lambda msg: msg.text == "🏆 Топ")
async def top_players(message: types.Message):
    users = load_users()
    
    real_players = []
    for uid, data in users.items():
        if data.get('total_bets', 0) > 0 or data.get('balance', 0) > 5000:
            real_players.append({
                "name": data.get('name', f"Игрок{uid[:4]}"),
                "balance": data.get('balance', 0)
            })
    
    real_players.sort(key=lambda x: x['balance'], reverse=True)
    
    top_text = "🏆 ТОП ИГРОКОВ 🏆\n\n"
    for i, player in enumerate(real_players[:10], 1):
        top_text += f"{i}. {player['name']} — {player['balance']:,} ₽\n"
    
    user_id = str(message.from_user.id)
    user_balance = init_user(message.from_user.id, message.from_user.username).get('balance', 0)
    position = 1
    for i, player in enumerate(real_players, 1):
        if player['balance'] == user_balance:
            position = i
            break
    
    top_text += f"\n📊 Ваше место: {position}"
    
    await message.answer(top_text, parse_mode="Markdown")

# ============ ПЕРЕВОД ДЕНЕГ ============
@dp.message(lambda msg: msg.text == "🔄 Перевести")
async def transfer_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    max_transfer = get_max_transfer(user.get('limit_level', 1))
    upgrade_cost = get_limit_upgrade_cost(user.get('limit_level', 1))
    
    await message.answer(
        f"🔄 ПЕРЕВОД ДЕНЕГ\n\n"
        f"📊 Макс. перевод: {max_transfer} ₽\n"
        f"🏦 Уровень лимита: {user.get('limit_level', 1)}\n\n"
        f"📝 перевод @username 1000\n\n"
        f"📈 Прокачка лимита: {upgrade_cost} ₽",
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
        
        await callback.message.answer(f"✅ Лимит повышен!\n📈 Уровень: {user['limit_level']}\n💰 Макс. перевод: {new_max} ₽\n💸 Следующая: {next_cost} ₽")
    else:
        need = cost - user['balance']
        await callback.message.answer(f"❌ Не хватает! Нужно: {cost} ₽\n💸 Не хватает: {need} ₽")
    await callback.answer()

@dp.message(lambda msg: msg.text.startswith("перевод"))
async def transfer_money(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ Пример: перевод @username 1000")
        return
    
    target = parts[1].replace("@", "")
    try:
        amount = int(parts[2])
    except:
        await message.answer("❌ Введи сумму числом!")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    max_transfer = get_max_transfer(user.get('limit_level', 1))
    
    if amount < 1:
        await message.answer("❌ Минимум 1 ₽")
        return
    if amount > max_transfer:
        await message.answer(f"❌ Макс. перевод: {max_transfer} ₽\n📈 Повысь лимит!")
        return
    if amount > user['balance']:
        await message.answer(f"❌ Не хватает! Баланс: {user['balance']} ₽")
        return
    
    users = load_users()
    target_id = None
    target_name = None
    for uid, data in users.items():
        if data.get('name', '').lower() == target.lower():
            target_id = uid
            target_name = data.get('name')
            break
    
    if not target_id:
        await message.answer(f"❌ Игрок {target} не найден!")
        return
    
    if target_id == str(message.from_user.id):
        await message.answer("❌ Нельзя перевести себе!")
        return
    
    user['balance'] -= amount
    save_user(message.from_user.id, user)
    
    target_user = init_user(target_id, target_name)
    target_user['balance'] += amount
    save_user(target_id, target_user)
    
    await message.answer(f"✅ Перевод {amount} ₽ -> {target_name}\n💰 Твой баланс: {user['balance']} ₽")
    await bot.send_message(int(target_id), f"✅ Вам перевели {amount} ₽ от {user['name']}\n💰 Баланс: {target_user['balance']} ₽")

# ============ СМЕНА НИКА ============
@dp.message(lambda msg: msg.text == "✏️ Сменить ник")
async def change_nick_prompt(message: types.Message):
    await message.answer("✏️ СМЕНА НИКА\n\n/setnik НовыйНик")

@dp.message(Command("setnik"))
async def set_nickname(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ Пример: /setnik Ванёк")
        return
    new_nick = parts[1][:20]
    user = init_user(message.from_user.id, message.from_user.username)
    old_nick = user['name']
    user['name'] = new_nick
    save_user(message.from_user.id, user)
    await message.answer(f"✅ Ник изменён!\n👤 Старый: {old_nick}\n👤 Новый: {new_nick}")

# ============ ПРОМОКОД РАНДОМ ============
@dp.message(lambda msg: msg.text == "РАНДОМ")
async def promo_random(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    last_promo = user.get("last_promo", 0)
    now = time.time()
    
    if now - last_promo < 172800:
        left = int(48 - (now - last_promo) // 3600)
        await message.answer(f"⏰ Промокод через {left} часов!")
        return
    
    amount = random.randint(44444, 122222)
    user["balance"] += amount
    user["last_promo"] = now
    save_user(message.from_user.id, user)
    await message.answer(f"✅ +{amount} ₽\n💰 Баланс: {user['balance']:,} ₽\n⏰ Следующий через 48ч!")

# ============ ПРОМОКОД ПРОМО: ВАНЁК (работает) ============
@dp.message(lambda msg: msg.text == "ПРОМО: ВАНЁК")
async def promo_vanek(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    user["balance"] += 1000000000000000000000000
    save_user(message.from_user.id, user)
    
    # Обновляем сообщение с балансом
    if message.from_user.id in balance_messages:
        try:
            await balance_messages[message.from_user.id].edit_text(f"💰 Баланс: {user['balance']} ₽\n🏦 В банке: {user['bank']} ₽")
        except:
            pass
    
    await message.answer(
        f"✅ **ПРОМОКОД АКТИВИРОВАН!**\n\n"
        f"💰 +1.000.000.000.000.000.000.000.000 ₽ (1 Септиллион)\n"
        f"💰 Новый баланс: {user['balance']:,} ₽\n\n"
        f"👑 Только для тебя, Ванёк!",
        parse_mode="Markdown"
    )

# ============ БОНУС ============
@dp.message(lambda msg: msg.text == "🎁 Бонус")
async def bonus_8h(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = time.time()
    last_bonus = user.get("last_bonus", 0)
    
    if now - last_bonus < 28800:
        left_hours = int(8 - (now - last_bonus) // 3600)
        left_minutes = int(60 - ((now - last_bonus) % 3600) // 60)
        await message.answer(f"⏰ Бонус через {left_hours}ч {left_minutes}мин!")
        return
    
    amount = random.randint(2500, 9000)
    user['balance'] += amount
    user['last_bonus'] = now
    save_user(message.from_user.id, user)
    
    if message.from_user.id in balance_messages:
        try:
            await balance_messages[message.from_user.id].edit_text(f"💰 Баланс: {user['balance']} ₽\n🏦 В банке: {user['bank']} ₽")
        except:
            pass
    
    await message.answer(f"🎁 +{amount} ₽\n💰 Баланс: {user['balance']} ₽\n⏰ Следующий через 8ч!")

# ============ ФУТБОЛ ============
@dp.message(lambda msg: msg.text == "⚽ Футбол")
async def football_menu(message: types.Message):
    await message.answer("⚽ ФУТБОЛ\n\n!ф 100\nШанс: 45% | x2.2")

@dp.message(lambda msg: msg.text.startswith("!ф"))
async def football_game(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: !ф 100")
        return
    try:
        bet = int(parts[1])
    except:
        await message.answer("❌ Введи число!")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    
    if bet < 1:
        await message.answer("❌ Минимум 1 ₽")
        return
    if bet > user['balance']:
        await message.answer(f"❌ Не хватает! Баланс: {user['balance']} ₽")
        return
    
    win = random.random() < 0.45
    await message.answer("⚽ Удар...")
    await asyncio.sleep(1)
    
    if win:
        win_amount = int(bet * 2.2)
        user['balance'] += win_amount
        user['total_bets'] += 1
        user['total_wins'] += 1
        save_user(message.from_user.id, user)
        await message.answer(f"✅ ГОЛ! +{win_amount} ₽\n💰 Баланс: {user['balance']} ₽")
    else:
        user['balance'] -= bet
        user['total_bets'] += 1
        save_user(message.from_user.id, user)
        await message.answer(f"❌ МИМО! -{bet} ₽\n💰 Баланс: {user['balance']} ₽")
    
    if message.from_user.id in balance_messages:
        try:
            await balance_messages[message.from_user.id].edit_text(f"💰 Баланс: {user['balance']} ₽\n🏦 В банке: {user['bank']} ₽")
        except:
            pass

# ============ ДАРТС ============
@dp.message(lambda msg: msg.text == "🎯 Дартс")
async def darts_menu(message: types.Message):
    await message.answer("🎯 ДАРТС\n\n!д 100\nШанс: 40% | x2.5")

@dp.message(lambda msg: msg.text.startswith("!д"))
async def darts_game(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: !д 100")
        return
    try:
        bet = int(parts[1])
    except:
        await message.answer("❌ Введи число!")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    
    if bet < 1:
        await message.answer("❌ Минимум 1 ₽")
        return
    if bet > user['balance']:
        await message.answer(f"❌ Не хватает! Баланс: {user['balance']} ₽")
        return
    
    win = random.random() < 0.40
    await message.answer("🎯 Бросок...")
    await asyncio.sleep(1)
    
    if win:
        win_amount = int(bet * 2.5)
        user['balance'] += win_amount
        user['total_bets'] += 1
        user['total_wins'] += 1
        save_user(message.from_user.id, user)
        await message.answer(f"✅ ПОПАЛ! +{win_amount} ₽\n💰 Баланс: {user['balance']} ₽")
    else:
        user['balance'] -= bet
        user['total_bets'] += 1
        save_user(message.from_user.id, user)
        await message.answer(f"❌ МИМО! -{bet} ₽\n💰 Баланс: {user['balance']} ₽")
    
    if message.from_user.id in balance_messages:
        try:
            await balance_messages[message.from_user.id].edit_text(f"💰 Баланс: {user['balance']} ₽\n🏦 В банке: {user['bank']} ₽")
        except:
            pass

# ============ ПРОФИЛЬ ============
@dp.message(lambda msg: msg.text == "👤 Профиль")
async def profile(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    premium = "❌ Нет" if user.get('premium', 0) == 0 else f"✅ {user.get('premium', 0)} 💎"
    user_id = message.from_user.id
    
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
    
    profile_text = f"""👤 {user['name']}

👑 Премиум: {premium}
💵 Баланс: {user['balance']:,} ₽
🏦 В банке: {user['bank']:,} ₽
🏆 Место в топе: {position}
🏦 Уровень банка: {user.get('bank_level', 1)}
📊 Лимит: {get_max_transfer(user.get('limit_level', 1))} ₽
🍀 Ставок: {user.get('total_bets', 0)}
🏆 Побед: {user.get('total_wins', 0)}"""
    
    if user_id in profile_messages:
        try:
            await profile_messages[user_id].edit_text(profile_text)
            return
        except:
            pass
    
    msg = await message.answer(profile_text)
    profile_messages[user_id] = msg

# ============ НАЗАД ============
@dp.callback_query(lambda c: c.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.answer("◀️ Главное меню", reply_markup=main_keyboard)
    await callback.answer()

async def main():
    print("🤖 Бот запущен!")
    
    asyncio.create_task(bank_profit_worker())
    asyncio.create_task(personal_bonus_worker())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
