import asyncio
import json
import os
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8208958973:AAH5EhmNReiVXC-cnE4F6jZQ9PcFL3ZTi1Q"

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
            "business": None,
            "business_level": 1,
            "generator": None,
            "generator_level": 1,
            "farm": None,
            "farm_level": 1,
            "quarry": None,
            "quarry_level": 1,
            "tree": None,
            "tree_level": 1,
            "garden": None,
            "garden_level": 1,
            "last_water": 0,
            "last_business": 0,
            "last_generator": 0,
            "last_farm": 0,
            "last_quarry": 0,
            "last_tree": 0,
            "last_garden": 0,
            "last_daily": 0,
            "married_to": None,
            "married_id": None,
            "cases": {"common": 0, "rare": 0, "epic": 0, "legendary": 0},
            "exp": 0,
            "level": 1
        }
        save_users(users)
    return users[user_id]

def save_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

def add_exp(user_id, amount):
    user = init_user(user_id, "")
    user["exp"] += amount
    new_level = 1 + user["exp"] // 500
    if new_level > user["level"]:
        user["level"] = new_level
        asyncio.create_task(bot.send_message(user_id, f"🎉 Поздравляем! Вы достигли {new_level} уровня!"))
    save_user(user_id, user)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="🏦 Банк")],
        [KeyboardButton(text="🗄 Бизнес"), KeyboardButton(text="🏭 Генератор")],
        [KeyboardButton(text="🧰 Майнинг"), KeyboardButton(text="⚠️ Карьер")],
        [KeyboardButton(text="🌳 Дерево"), KeyboardButton(text="🌿 Сады")],
        [KeyboardButton(text="📦 Кейсы"), KeyboardButton(text="💒 Браки")],
        [KeyboardButton(text="🎮 Игры"), KeyboardButton(text="🎁 Бонус")],
        [KeyboardButton(text="⭐ Профиль"), KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True
)

games_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎮 Спин", callback_data="game_spin"), InlineKeyboardButton(text="🎲 Кубик", callback_data="game_dice")],
    [InlineKeyboardButton(text="🏀 Баскетбол", callback_data="game_basketball"), InlineKeyboardButton(text="🎯 Дартс", callback_data="game_dart")],
    [InlineKeyboardButton(text="🎳 Боулинг", callback_data="game_bowling"), InlineKeyboardButton(text="📉 Трейд", callback_data="game_trade")],
    [InlineKeyboardButton(text="🎰 Казино", callback_data="game_casino"), InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
])

bet_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 100", callback_data="bet_100"), InlineKeyboardButton(text="💰 500", callback_data="bet_500")],
    [InlineKeyboardButton(text="💰 1000", callback_data="bet_1000"), InlineKeyboardButton(text="💰 5000", callback_data="bet_5000")],
    [InlineKeyboardButton(text="💰 10000", callback_data="bet_10000"), InlineKeyboardButton(text="💰 Всё", callback_data="bet_all")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_games")]
])

dice_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎲 1", callback_data="dice_1"), InlineKeyboardButton(text="🎲 2", callback_data="dice_2"), InlineKeyboardButton(text="🎲 3", callback_data="dice_3")],
    [InlineKeyboardButton(text="🎲 4", callback_data="dice_4"), InlineKeyboardButton(text="🎲 5", callback_data="dice_5"), InlineKeyboardButton(text="🎲 6", callback_data="dice_6")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_games")]
])

trade_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📈 ВВЕРХ", callback_data="trade_up"), InlineKeyboardButton(text="📉 ВНИЗ", callback_data="trade_down")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_games")]
])

user_game_state = {}
user_dice_guess = {}
user_trade_direction = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "✨ Добро пожаловать в Retro 19?! ✨\n\n"
        "🎮 Экономическая игра с уклоном в удачу!\n\n"
        "👇 Используй кнопки ниже!",
        reply_markup=main_keyboard
    )

@dp.message(lambda msg: msg.text == "💰 Баланс")
async def show_balance(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(f"💰 Твой баланс: {user['balance']} ₽\n🏦 В банке: {user.get('bank', 0)} ₽")

@dp.message(lambda msg: msg.text == "🏦 Банк")
async def bank_menu(message: types.Message):
    await message.answer(
        "🏦 БАНК\n\n"
        "• `Банк пополнить 1000` - положить деньги\n"
        "• `Банк снять 500` - снять деньги\n"
        "💰 Налог на снятие: 4%"
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

# ============ БИЗНЕС ============
@dp.message(lambda msg: msg.text == "🗄 Бизнес")
async def business_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if user.get('business') and now - user.get('last_business', 0) >= 3600:
        income = 500 * user.get('business_level', 1)
        user['balance'] += income
        user['last_business'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"🏢 Бизнес принёс доход!\n💰 +{income} ₽")
    await message.answer(
        "🏢 БИЗНЕС\n\n"
        "• `Купить бизнес` - 50,000 ₽\n"
        "• `Продать бизнес` - 25,000 ₽\n"
        "💰 Доход: 500 ₽/час"
    )

@dp.message(lambda msg: msg.text == "Купить бизнес")
async def buy_business(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('business'):
        await message.answer("❌ У тебя уже есть бизнес!")
        return
    if user['balance'] < 50000:
        await message.answer(f"❌ Нужно 50,000 ₽! У тебя {user['balance']} ₽")
        return
    user['balance'] -= 50000
    user['business'] = "Магазин"
    user['last_business'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты купил бизнес! Теперь ты получаешь 500 ₽ каждый час!")

@dp.message(lambda msg: msg.text == "Продать бизнес")
async def sell_business(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('business'):
        await message.answer("❌ У тебя нет бизнеса!")
        return
    user['balance'] += 25000
    user['business'] = None
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты продал бизнес за 25,000 ₽!")

# ============ ГЕНЕРАТОР ============
@dp.message(lambda msg: msg.text == "🏭 Генератор")
async def generator_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if user.get('generator') and now - user.get('last_generator', 0) >= 7200:
        income = 300 * user.get('generator_level', 1)
        user['balance'] += income
        user['last_generator'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"🏭 Генератор произвёл энергию!\n💰 +{income} ₽")
    await message.answer(
        "🏭 ГЕНЕРАТОР\n\n"
        "• `Купить генератор` - 100,000 ₽\n"
        "• `Продать генератор` - 50,000 ₽\n"
        "💰 Доход: 300 ₽/2 часа"
    )

@dp.message(lambda msg: msg.text == "Купить генератор")
async def buy_generator(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('generator'):
        await message.answer("❌ У тебя уже есть генератор!")
        return
    if user['balance'] < 100000:
        await message.answer(f"❌ Нужно 100,000 ₽! У тебя {user['balance']} ₽")
        return
    user['balance'] -= 100000
    user['generator'] = "Солнечный генератор"
    user['last_generator'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты купил генератор! Теперь ты получаешь 300 ₽ каждые 2 часа!")

@dp.message(lambda msg: msg.text == "Продать генератор")
async def sell_generator(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('generator'):
        await message.answer("❌ У тебя нет генератора!")
        return
    user['balance'] += 50000
    user['generator'] = None
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты продал генератор за 50,000 ₽!")

# ============ ФЕРМА (МАЙНИНГ) ============
@dp.message(lambda msg: msg.text == "🧰 Майнинг")
async def mining_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if user.get('farm') and now - user.get('last_farm', 0) >= 1800:
        income = 300 * user.get('farm_level', 1)
        user['balance'] += income
        user['last_farm'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"🔋 Ферма намайнила монеты!\n💰 +{income} ₽")
    await message.answer(
        "🔋 МАЙНИНГ ФЕРМА\n\n"
        "• `Купить ферму` - 30,000 ₽\n"
        "• `Продать ферму` - 15,000 ₽\n"
        "💰 Доход: 300 ₽/30 мин"
    )

@dp.message(lambda msg: msg.text == "Купить ферму")
async def buy_farm(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('farm'):
        await message.answer("❌ У тебя уже есть ферма!")
        return
    if user['balance'] < 30000:
        await message.answer(f"❌ Нужно 30,000 ₽! У тебя {user['balance']} ₽")
        return
    user['balance'] -= 30000
    user['farm'] = "Майнинг ферма"
    user['last_farm'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты купил ферму! Теперь ты получаешь 300 ₽ каждые 30 минут!")

@dp.message(lambda msg: msg.text == "Продать ферму")
async def sell_farm(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('farm'):
        await message.answer("❌ У тебя нет фермы!")
        return
    user['balance'] += 15000
    user['farm'] = None
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты продал ферму за 15,000 ₽!")

# ============ КАРЬЕР ============
@dp.message(lambda msg: msg.text == "⚠️ Карьер")
async def quarry_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if user.get('quarry') and now - user.get('last_quarry', 0) >= 5400:
        income = 500 * user.get('quarry_level', 1)
        user['balance'] += income
        user['last_quarry'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"⚠️ Карьер добыл ресурсы!\n💰 +{income} ₽")
    await message.answer(
        "⚠️ КАРЬЕР\n\n"
        "• `Купить карьер` - 80,000 ₽\n"
        "• `Продать карьер` - 40,000 ₽\n"
        "💰 Доход: 500 ₽/1.5 часа"
    )

@dp.message(lambda msg: msg.text == "Купить карьер")
async def buy_quarry(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('quarry'):
        await message.answer("❌ У тебя уже есть карьер!")
        return
    if user['balance'] < 80000:
        await message.answer(f"❌ Нужно 80,000 ₽! У тебя {user['balance']} ₽")
        return
    user['balance'] -= 80000
    user['quarry'] = "Каменный карьер"
    user['last_quarry'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты купил карьер! Теперь ты получаешь 500 ₽ каждые 1.5 часа!")

@dp.message(lambda msg: msg.text == "Продать карьер")
async def sell_quarry(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('quarry'):
        await message.answer("❌ У тебя нет карьера!")
        return
    user['balance'] += 40000
    user['quarry'] = None
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты продал карьер за 40,000 ₽!")

# ============ ДЕРЕВО ============
@dp.message(lambda msg: msg.text == "🌳 Дерево")
async def tree_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if user.get('tree') and now - user.get('last_tree', 0) >= 86400:
        income = 200 * user.get('tree_level', 1)
        user['balance'] += income
        user['last_tree'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"🌳 Дерево принесло плоды!\n💰 +{income} ₽")
    await message.answer(
        "🌳 ДЕНЕЖНОЕ ДЕРЕВО\n\n"
        "• `Купить дерево` - 20,000 ₽\n"
        "• `Продать дерево` - 10,000 ₽\n"
        "💰 Доход: 200 ₽/день"
    )

@dp.message(lambda msg: msg.text == "Купить дерево")
async def buy_tree(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('tree'):
        await message.answer("❌ У тебя уже есть дерево!")
        return
    if user['balance'] < 20000:
        await message.answer(f"❌ Нужно 20,000 ₽! У тебя {user['balance']} ₽")
        return
    user['balance'] -= 20000
    user['tree'] = "Денежное дерево"
    user['last_tree'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты купил дерево! Теперь ты получаешь 200 ₽ каждый день!")

@dp.message(lambda msg: msg.text == "Продать дерево")
async def sell_tree(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('tree'):
        await message.answer("❌ У тебя нет дерева!")
        return
    user['balance'] += 10000
    user['tree'] = None
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты продал дерево за 10,000 ₽!")

# ============ САДЫ ============
@dp.message(lambda msg: msg.text == "🌿 Сады")
async def garden_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if user.get('garden') and now - user.get('last_garden', 0) >= 21600:
        income = 400 * user.get('garden_level', 1)
        user['balance'] += income
        user['last_garden'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"🌿 Сад принёс урожай!\n💰 +{income} ₽")
    await message.answer(
        "🌿 САДЫ\n\n"
        "• `Купить сад` - 40,000 ₽\n"
        "• `Продать сад` - 20,000 ₽\n"
        "• `Сад полить` - +100-500 ₽\n"
        "💰 Доход: 400 ₽/6 часов"
    )

@dp.message(lambda msg: msg.text == "Купить сад")
async def buy_garden(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('garden'):
        await message.answer("❌ У тебя уже есть сад!")
        return
    if user['balance'] < 40000:
        await message.answer(f"❌ Нужно 40,000 ₽! У тебя {user['balance']} ₽")
        return
    user['balance'] -= 40000
    user['garden'] = "Волшебный сад"
    user['last_garden'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты купил сад! Теперь ты получаешь 400 ₽ каждые 6 часов!")

@dp.message(lambda msg: msg.text == "Продать сад")
async def sell_garden(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('garden'):
        await message.answer("❌ У тебя нет сада!")
        return
    user['balance'] += 20000
    user['garden'] = None
    save_user(message.from_user.id, user)
    await message.answer("✅ Ты продал сад за 20,000 ₽!")

@dp.message(lambda msg: msg.text == "Сад полить")
async def water_garden(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('garden'):
        await message.answer("❌ У тебя нет сада!")
        return
    now = datetime.now().timestamp()
    if now - user.get('last_water', 0) < 10800:
        left = int(10800 - (now - user.get('last_water', 0)))
        await message.answer(f"⏳ Сад можно полить через {left // 60} минут")
        return
    user['last_water'] = now
    bonus = random.randint(100, 500)
    user['balance'] += bonus
    save_user(message.from_user.id, user)
    await message.answer(f"💦 Ты полил сад!\n💰 +{bonus} ₽")

# ============ КЕЙСЫ ============
@dp.message(lambda msg: msg.text == "📦 Кейсы")
async def cases_menu(message: types.Message):
    await message.answer(
        "📦 КЕЙСЫ\n\n"
        "• `Купить кейс 1` - Обычный (100 ₽)\n"
        "• `Купить кейс 2` - Редкий (500 ₽)\n"
        "• `Купить кейс 3` - Эпический (2000 ₽)\n"
        "• `Купить кейс 4` - Легендарный (10000 ₽)\n\n"
        "• `Открыть кейс 1` - открыть обычный кейс"
    )

@dp.message(lambda msg: msg.text.startswith("Купить кейс"))
async def buy_case(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ Пример: Купить кейс 1")
        return
    try:
        case_num = int(parts[2])
    except:
        await message.answer("❌ Введи номер кейса (1-4)!")
        return
    prices = {1: 100, 2: 500, 3: 2000, 4: 10000}
    names = {1: "common", 2: "rare", 3: "epic", 4: "legendary"}
    if case_num not in prices:
        await message.answer("❌ Номера кейсов: 1, 2, 3, 4")
        return
    user = init_user(message.from_user.id, message.from_user.username)
    if user['balance'] < prices[case_num]:
        await message.answer(f"❌ Нужно {prices[case_num]} ₽!")
        return
    user['balance'] -= prices[case_num]
    user['cases'][names[case_num]] = user['cases'].get(names[case_num], 0) + 1
    save_user(message.from_user.id, user)
    await message.answer(f"✅ Ты купил кейс за {prices[case_num]} ₽!")

@dp.message(lambda msg: msg.text.startswith("Открыть кейс"))
async def open_case(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ Пример: Открыть кейс 1")
        return
    try:
        case_num = int(parts[2])
    except:
        await message.answer("❌ Введи номер кейса (1-4)!")
        return
    names = {1: "common", 2: "rare", 3: "epic", 4: "legendary"}
    if case_num not in names:
        await message.answer("❌ Номера кейсов: 1, 2, 3, 4")
        return
    user = init_user(message.from_user.id, message.from_user.username)
    case_type = names[case_num]
    if user['cases'].get(case_type, 0) < 1:
        await message.answer("❌ У тебя нет таких кейсов!")
        return
    user['cases'][case_type] -= 1
    money = random.randint(500, 2000) if case_num == 1 else random.randint(1000, 5000) if case_num == 2 else random.randint(5000, 20000) if case_num == 3 else random.randint(20000, 100000)
    exp = random.randint(10, 50) if case_num == 1 else random.randint(30, 100) if case_num == 2 else random.randint(50, 200) if case_num == 3 else random.randint(100, 500)
    user['balance'] += money
    add_exp(message.from_user.id, exp)
    save_user(message.from_user.id, user)
    await message.answer(f"📦 Ты открыл кейс!\n💰 +{money} ₽\n⭐ +{exp} опыта")

# ============ БРАКИ ============
@dp.message(lambda msg: msg.text == "💒 Браки")
async def marriage_menu(message: types.Message):
    await message.answer(
        "💒 БРАКИ\n\n"
        "• `/marry @username` - жениться\n"
        "• `/divorce` - развестись\n"
        "• `/marriage` - показать свой брак"
    )

@dp.message(Command("marry"))
async def marry_user(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Пример: /marry @username")
        return
    target_name = parts[1].replace("@", "")
    user = init_user(message.from_user.id, message.from_user.username)
    users = load_users()
    target_user = None
    target_id = None
    for uid, u in users.items():
        if u['name'].lower() == target_name.lower() and uid != str(message.from_user.id):
            target_user = u
            target_id = uid
            break
    if not target_user:
        await message.answer("❌ Игрок не найден!")
        return
    if user.get('married_to'):
        await message.answer(f"❌ Ты уже в браке с {user['married_to']}!")
        return
    if target_user.get('married_to'):
        await message.answer(f"❌ {target_user['name']} уже в браке!")
        return
    user['married_to'] = target_user['name']
    user['married_id'] = target_id
    target_user['married_to'] = user['name']
    target_user['married_id'] = str(message.from_user.id)
    save_user(message.from_user.id, user)
    save_user(int(target_id), target_user)
    await message.answer(f"💒 Поздравляем! {user['name']} и {target_user['name']} теперь в браке!")

@dp.message(Command("divorce"))
async def divorce_user(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('married_to'):
        await message.answer("❌ Ты не в браке!")
        return
    partner_id = user.get('married_id')
    partner_name = user.get('married_to')
    user['married_to'] = None
    user['married_id'] = None
    save_user(message.from_user.id, user)
    if partner_id:
        partner = init_user(int(partner_id), "")
        partner['married_to'] = None
        partner['married_id'] = None
        save_user(int(partner_id), partner)
        await bot.send_message(int(partner_id), f"💔 {user['name']} развёлся с тобой!")
    await message.answer(f"💔 Ты развёлся с {partner_name}!")

@dp.message(Command("marriage"))
async def my_marriage(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('married_to'):
        await message.answer(f"💒 Ты в браке с {user['married_to']}!")
    else:
        await message.answer("💔 Ты не в браке!")

# ============ ИГРЫ ============
@dp.message(lambda msg: msg.text == "🎮 Игры")
async def games_menu(message: types.Message):
    await message.answer("🎲 ВЫБЕРИ ИГРУ", reply_markup=games_keyboard)

@dp.callback_query(lambda c: c.data.startswith("game_"))
async def handle_game_choice(callback: types.CallbackQuery):
    game = callback.data.replace("game_", "")
    user_game_state[callback.from_user.id] = f"game_{game}"
    if game == "spin":
        await callback.message.answer("🎰 СПИН\n💰 Выбери ставку:", reply_markup=bet_keyboard)
    elif game == "dice":
        await callback.message.answer("🎲 КУБИК\n🎲 Выбери число:", reply_markup=dice_keyboard)
    elif game == "basketball":
        await callback.message.answer("🏀 БАСКЕТБОЛ\n💰 Выбери ставку:", reply_markup=bet_keyboard)
    elif game == "dart":
        await callback.message.answer("🎯 ДАРТС\n💰 Выбери ставку:", reply_markup=bet_keyboard)
    elif game == "bowling":
        await callback.message.answer("🎳 БОУЛИНГ\n💰 Выбери ставку:", reply_markup=bet_keyboard)
    elif game == "trade":
        await callback.message.answer("📉 ТРЕЙД\n📈 Выбери направление:", reply_markup=trade_keyboard)
    elif game == "casino":
        await callback.message.answer("🎰 КАЗИНО\n💰 Выбери ставку:", reply_markup=bet_keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("dice_"))
async def handle_dice_choice(callback: types.CallbackQuery):
    guess = int(callback.data.split("_")[1])
    user_dice_guess[callback.from_user.id] = guess
    await callback.message.answer(f"🎲 Ты выбрал число {guess}!\n👇 Теперь выбери ставку:", reply_markup=bet_keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("trade_"))
async def handle_trade_choice(callback: types.CallbackQuery):
    direction = callback.data.split("_")[1]
    user_trade_direction[callback.from_user.id] = direction
    await callback.message.answer(f"📉 Ты выбрал {direction.upper()}!\n👇 Теперь выбери ставку:", reply_markup=bet_keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("bet_"))
async def handle_bet(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    game_state = user_game_state.get(user_id)
    if not game_state:
        await callback.answer("❌ Ошибка! Начни игру заново.")
        return
    bet_str = callback.data.replace("bet_", "")
    if bet_str == "all":
        user = init_user(user_id, callback.from_user.username)
        bet = user['balance']
    else:
        bet = int(bet_str)
    user = init_user(user_id, callback.from_user.username)
    if bet > user['balance']:
        await callback.message.answer(f"❌ Не хватает! У тебя {user['balance']} ₽")
        await callback.answer()
        return
    game = game_state.replace("game_", "")
    msg = await callback.message.answer("🎲 ИГРАЕМ...")
    await asyncio.sleep(1)
    if game == "spin":
        multiplier = random.choice([2, 2, 3, 3, 4, 5, 10])
        if random.random() < 0.4:
            win = bet * multiplier
            user['balance'] += win
            await msg.edit_text(f"🎰 СПИН\n✨ ВЫПАЛ x{multiplier}!\n🎉 ПОБЕДА! +{win} ₽")
            add_exp(user_id, 10 * multiplier)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🎰 СПИН\n💔 ПРОИГРЫШ! -{bet} ₽")
    elif game == "dice":
        guess = user_dice_guess.get(user_id)
        if not guess:
            await callback.message.answer("❌ Сначала выбери число!")
            await callback.answer()
            return
        roll = random.randint(1, 6)
        if roll == guess:
            win = bet * 5
            user['balance'] += win
            await msg.edit_text(f"🎲 КУБИК\nВыпало: {roll}\nТвоё число: {guess}\n🎉 УГАДАЛ! +{win} ₽")
            add_exp(user_id, 25)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🎲 КУБИК\nВыпало: {roll}\nТвоё число: {guess}\n😞 НЕ УГАДАЛ! -{bet} ₽")
        user_dice_guess[user_id] = None
    elif game == "basketball":
        if random.choice([True, False]):
            win = bet * 2
            user['balance'] += win
            await msg.edit_text(f"🏀 БАСКЕТБОЛ\n🏀 ПОПАДАНИЕ!\n🎉 ПОБЕДА! +{win} ₽")
            add_exp(user_id, 10)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🏀 БАСКЕТБОЛ\n💔 ПРОМАХ!\n😞 ПРОИГРЫШ! -{bet} ₽")
    elif game == "dart":
        if random.random() < 0.33:
            win = bet * 3
            user['balance'] += win
            await msg.edit_text(f"🎯 ДАРТС\n🎯 ЯБЛОЧКО!\n🎉 ПОБЕДА! +{win} ₽")
            add_exp(user_id, 15)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🎯 ДАРТС\n💔 МИМО!\n😞 ПРОИГРЫШ! -{bet} ₽")
    elif game == "bowling":
        rand = random.random()
        if rand < 0.2:
            win = bet * 3
            user['balance'] += win
            await msg.edit_text(f"🎳 БОУЛИНГ\n🎳 СТРАЙК!\n🎉 ПОБЕДА! +{win} ₽")
            add_exp(user_id, 20)
        elif rand < 0.5:
            win = bet * 2
            user['balance'] += win
            await msg.edit_text(f"🎳 БОУЛИНГ\n🎳 СПЭР!\n🎉 ПОБЕДА! +{win} ₽")
            add_exp(user_id, 10)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🎳 БОУЛИНГ\n💔 ПРОМАХ!\n😞 ПРОИГРЫШ! -{bet} ₽")
    elif game == "trade":
        direction = user_trade_direction.get(user_id)
        if not direction:
            await callback.message.answer("❌ Сначала выбери направление!")
            await callback.answer()
            return
        result = random.choice(["вверх", "вниз"])
        multiplier = random.uniform(1.5, 3.0)
        if direction == result:
            win = int(bet * multiplier)
            user['balance'] += win
            await msg.edit_text(f"📉 ТРЕЙД\nКурс пошёл {result.upper()}! x{multiplier:.1f}\n🎉 ВЫИГРЫШ! +{win} ₽")
            add_exp(user_id, 15)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"📉 ТРЕЙД\nКурс пошёл {result.upper()}...\n😞 ПРОИГРЫШ! -{bet} ₽")
        user_trade_direction[user_id] = None
    elif game == "casino":
        if random.random() < 0.48:
            win = bet * 2
            user['balance'] += win
            await msg.edit_text(f"🎰 КАЗИНО\n🍀 ВЕЗЁТ!\n🎉 ВЫИГРЫШ! +{win} ₽")
            add_exp(user_id, 10)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🎰 КАЗИНО\n💔 НЕ ПОВЕЗЛО...\n😞 ПРОИГРЫШ! -{bet} ₽")
    save_user(user_id, user)
    user_game_state[user_id] = None
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.answer("◀️ Главное меню", reply_markup=main_keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_games")
async def back_to_games(callback: types.CallbackQuery):
    await callback.message.answer("🎲 ВЫБЕРИ ИГРУ", reply_markup=games_keyboard)
    await callback.answer()

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
        f"👤 Профиль\n\n"
        f"📛 Ник: {user['name']}\n"
        f"💰 Баланс: {user['balance']} ₽\n"
        f"🏦 В банке: {user.get('bank', 0)} ₽\n"
        f"⭐ Опыт: {user['exp']}\n"
        f"🎚️ Уровень: {user['level']}\n"
        f"💒 Брак: {user.get('married_to') or 'Нет'}"
    )

@dp.message(lambda msg: msg.text == "❓ Помощь")
async def help_command(message: types.Message):
    await message.answer(
        "📖 ПОМОЩЬ\n\n"
        "💰 Баланс - проверить деньги\n"
        "🏦 Банк - пополнить/снять\n"
        "🗄 Бизнес - купить/продать (500₽/час)\n"
        "🏭 Генератор - купить/продать (300₽/2ч)\n"
        "🧰 Майнинг - купить/продать (300₽/30мин)\n"
        "⚠️ Карьер - купить/продать (500₽/1.5ч)\n"
        "🌳 Дерево - купить/продать (200₽/день)\n"
        "🌿 Сады - купить/продать/полить (400₽/6ч)\n"
        "📦 Кейсы - купить/открыть кейсы\n"
        "💒 Браки - /marry, /divorce, /marriage\n"
        "🎮 Игры - Спин, Кубик, Баскетбол, Дартс, Боулинг, Трейд, Казино\n"
        "🎁 Бонус - 500₽ раз в день\n"
        "⭐ Профиль - статистика"
    )

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
