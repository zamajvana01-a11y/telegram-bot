import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8208958973:AAH5EhmNReiVXC-cnE4F6jZQ9PcFL3ZTi1Q"

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "users.json"
CLANS_FILE = "clans.json"
BOSS_FILE = "boss.json"
LOTTERY_FILE = "lottery.json"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_boss():
    if not os.path.exists(BOSS_FILE):
        return {"hp": 1000000, "max_hp": 1000000, "players": {}}
    with open(BOSS_FILE, "r") as f:
        return json.load(f)

def save_boss(boss):
    with open(BOSS_FILE, "w") as f:
        json.dump(boss, f, indent=2)

def load_clans():
    if not os.path.exists(CLANS_FILE):
        return {}
    with open(CLANS_FILE, "r") as f:
        return json.load(f)

def save_clans(clans):
    with open(CLANS_FILE, "w") as f:
        json.dump(clans, f, indent=2)

def load_lottery():
    if not os.path.exists(LOTTERY_FILE):
        return {"tickets": [], "jackpot": 10000, "last_draw": 0}
    with open(LOTTERY_FILE, "r") as f:
        return json.load(f)

def save_lottery(lottery):
    with open(LOTTERY_FILE, "w") as f:
        json.dump(lottery, f, indent=2)

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
            "diamonds": 0,
            "ore": 0,
            "stardust": 0,
            "rank": "🟤 Новичок",
            "frame": "📄 Обычная",
            "achievements": {},
            "daily_quests": {"date": "", "quests": []},
            "last_daily": 0,
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
            "exp": 0,
            "level": 1,
            "wins": 0,
            "games_played": 0,
            "boss_damage": 0,
            "boss_power": 100,
            "boss_upgrades": 0,
            "married_to": None,
            "married_id": None,
            "clan": None,
            "friends": [],
            "cases": {"common": 0, "gold": 0, "ore": 0, "material": 0},
            "shop_items": {"luck": 0, "shield": 0, "double_income_end": 0},
            "promo_used_count": 0
        }
        save_users(users)
    return users[user_id]

def save_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

def get_bank_percent(level):
    return min(0.3 + (level - 1) * 0.05, 5.0)

def get_upgrade_cost(level):
    return level * 10000

def get_boss_upgrade_cost(upgrades):
    return 1000 * (10 ** upgrades)

def update_rank(user_id):
    user = init_user(user_id, "")
    balance = user['balance']
    if balance >= 1000000000:
        user['rank'] = "👑 Олигарх"
    elif balance >= 100000000:
        user['rank'] = "💎 Магнат"
    elif balance >= 10000000:
        user['rank'] = "🏆 Миллионер"
    elif balance >= 1000000:
        user['rank'] = "⭐ Богач"
    elif balance >= 100000:
        user['rank'] = "💰 Состоятельный"
    else:
        user['rank'] = "🟤 Новичок"
    save_user(user_id, user)

def add_diamonds(user_id, amount):
    user = init_user(user_id, "")
    user['diamonds'] += amount
    save_user(user_id, user)

def add_ore(user_id, amount):
    user = init_user(user_id, "")
    user['ore'] += amount
    save_user(user_id, user)

def add_stardust(user_id, amount):
    user = init_user(user_id, "")
    user['stardust'] += amount
    save_user(user_id, user)

def add_case(user_id, case_type, amount=1):
    user = init_user(user_id, "")
    user['cases'][case_type] = user['cases'].get(case_type, 0) + amount
    save_user(user_id, user)

def add_exp(user_id, amount):
    user = init_user(user_id, "")
    user["exp"] += amount
    new_level = 1 + user["exp"] // 500
    if new_level > user["level"]:
        user["level"] = new_level
        add_diamonds(user_id, 10)
        asyncio.create_task(bot.send_message(user_id, f"🎉 Новый уровень {new_level}! +10💎"))
    save_user(user_id, user)

def get_daily_quests(user_id):
    user = init_user(user_id, "")
    today = datetime.now().strftime("%Y-%m-%d")
    if user.get('daily_quests', {}).get('date') != today:
        quests_list = [
            {"name": "Сыграй 3 игры", "target": 3, "progress": 0, "reward": 20, "type": "games"},
            {"name": "Выиграй 2 игры", "target": 2, "progress": 0, "reward": 30, "type": "wins"},
            {"name": "Заработай 10000 ₽", "target": 10000, "progress": 0, "reward": 25, "type": "money"},
            {"name": "Купи бизнес", "target": 1, "progress": 0, "reward": 50, "type": "buy_business"},
            {"name": "Открой кейс", "target": 2, "progress": 0, "reward": 40, "type": "open_case"},
            {"name": "Пополни банк", "target": 5000, "progress": 0, "reward": 35, "type": "bank_deposit"},
            {"name": "Ударь босса", "target": 3, "progress": 0, "reward": 45, "type": "boss_hit"},
            {"name": "Повысь уровень", "target": 1, "progress": 0, "reward": 60, "type": "level_up"},
        ]
        user['daily_quests'] = {"date": today, "quests": quests_list}
        save_user(user_id, user)
    return user['daily_quests']['quests']

def update_quest_progress(user_id, qtype, amount=1, money_earned=0):
    user = init_user(user_id, "")
    quests = get_daily_quests(user_id)
    updated = False
    for q in quests:
        if q['type'] == qtype:
            old_progress = q['progress']
            if qtype == "money":
                q['progress'] += money_earned
            elif qtype == "bank_deposit":
                q['progress'] += amount
            else:
                q['progress'] += amount
            if old_progress < q['target'] and q['progress'] >= q['target']:
                user['balance'] += q['reward']
                add_diamonds(user_id, q['reward'] // 2)
                asyncio.create_task(bot.send_message(user_id, f"✅ Квест выполнен: {q['name']}!\n💰 +{q['reward']} ₽\n💎 +{q['reward']//2}💎"))
            updated = True
    if updated:
        user['daily_quests']['quests'] = quests
        save_user(user_id, user)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="🏦 Банк")],
        [KeyboardButton(text="🗄 Бизнес"), KeyboardButton(text="🏭 Генератор")],
        [KeyboardButton(text="🧰 Майнинг"), KeyboardButton(text="⚠️ Карьер")],
        [KeyboardButton(text="🌳 Дерево"), KeyboardButton(text="🌿 Сады")],
        [KeyboardButton(text="📦 Кейсы"), KeyboardButton(text="💒 Браки")],
        [KeyboardButton(text="🎮 Игры"), KeyboardButton(text="🎁 Бонус")],
        [KeyboardButton(text="🏆 Ранги"), KeyboardButton(text="💎 Алмазы")],
        [KeyboardButton(text="🎨 Оформление"), KeyboardButton(text="📋 Квесты")],
        [KeyboardButton(text="⚔️ Арена"), KeyboardButton(text="💰 Инвестиции")],
        [KeyboardButton(text="👹 Босс"), KeyboardButton(text="🏛 Кланы")],
        [KeyboardButton(text="🎰 Лотерея"), KeyboardButton(text="🛒 Магазин")],
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

pvP_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⚔️ Битва на 1000💰", callback_data="pvp_1000"), InlineKeyboardButton(text="⚔️ Битва на 5000💰", callback_data="pvp_5000")],
    [InlineKeyboardButton(text="⚔️ Битва на 10000💰", callback_data="pvp_10000"), InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
])

invest_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Инвестировать 1000", callback_data="invest_1000"), InlineKeyboardButton(text="💰 Инвестировать 5000", callback_data="invest_5000")],
    [InlineKeyboardButton(text="💰 Инвестировать 10000", callback_data="invest_10000"), InlineKeyboardButton(text="📊 Продать", callback_data="invest_sell")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
])

frame_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📄 Обычная (0💎)", callback_data="frame_normal"), InlineKeyboardButton(text="✨ Золотая (100💎)", callback_data="frame_gold")],
    [InlineKeyboardButton(text="💎 Алмазная (300💎)", callback_data="frame_diamond"), InlineKeyboardButton(text="👑 Королевская (500💎)", callback_data="frame_royal")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
])

clan_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📋 Список кланов", callback_data="clan_list"), InlineKeyboardButton(text="➕ Создать клан", callback_data="clan_create")],
    [InlineKeyboardButton(text="🚪 Вступить в клан", callback_data="clan_join"), InlineKeyboardButton(text="💰 Внести в казну", callback_data="clan_donate")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
])

user_game_state = {}
user_dice_guess = {}
user_trade_direction = {}
user_pvp_bet = {}
user_clan_create = {}
user_clan_join = {}

# ПРОМОКОД Ванёк
@dp.message(lambda msg: msg.text == "Ванёк")
async def promo_vanek(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    used_count = user.get("promo_used_count", 0)
    if used_count >= 1000:
        await message.answer("❌ *Промокод использован 1000 раз! Лимит исчерпан.*", parse_mode="Markdown")
    else:
        user["promo_used_count"] = used_count + 1
        user["balance"] += 10000000000000000000
        save_user(message.from_user.id, user)
        remaining = 1000 - used_count - 1
        await message.answer(
            f"✅ **ПРОМОКОД АКТИВИРОВАН!**\n\n"
            f"💰 +10.000.000.000.000.000.000💰\n"
            f"📊 Осталось активаций: {remaining}\n"
            f"💎 Всего использовано: {used_count + 1}/1000",
            parse_mode="Markdown
            # ============ КОМАНДА START ============
@dp.message(Command("start"))
async def start(message: types.Message):
    init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "✨ **Добро пожаловать в Retro 19?!** ✨\n\n"
        "🎮 Экономическая игра с уклоном в удачу!\n\n"
        "📌 **Что тебя ждёт:**\n"
        "• 🏦 Банк с процентами и прокачкой\n"
        "• 🎮 7 азартных игр (любая ставка)\n"
        "• 👹 Босс с топ-100 игроков по урону\n"
        "• 📦 Кейсы с рандомными выигрышами\n"
        "• 🗄 Бизнес, генератор, ферма, карьер\n"
        "• 🌳 Денежное дерево и сады\n"
        "• 🎁 Ежедневные бонусы и квесты\n"
        "• 🏆 Ранги и достижения\n"
        "• 💎 Алмазы и оформление профиля\n"
        "• ⚔️ PvP-арена и инвестиции\n"
        "• 🏛 Кланы и лотерея\n\n"
        "👇 **Используй кнопки ниже!** 👇",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )

# ============ БАЛАНС ============
@dp.message(lambda msg: msg.text == "💰 Баланс")
async def show_balance(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"💰 **ТВОЙ БАЛАНС** 💰\n\n"
        f"💵 Наличные: {user['balance']:,} ₽\n"
        f"🏦 В банке: {user.get('bank', 0):,} ₽\n"
        f"💎 Алмазов: {user.get('diamonds', 0)}\n"
        f"⚙ Руды: {user.get('ore', 0)}\n"
        f"🌌 Звёздной пыли: {user.get('stardust', 0)}",
        parse_mode="Markdown"
    )

# ============ БАНК ============
@dp.message(lambda msg: msg.text == "🏦 Банк")
async def bank_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    percent = get_bank_percent(user['bank_level'])
    await message.answer(
        f"🏦 **БАНКОВСКАЯ СИСТЕМА** 🏦\n\n"
        f"💰 Деньги в банке: {user.get('bank', 0):,} ₽\n"
        f"📈 Процент в час: {percent:.2f}%\n"
        f"🏆 Уровень банка: {user['bank_level']}\n"
        f"💎 Стоимость прокачки: {get_upgrade_cost(user['bank_level']):,} ₽\n\n"
        f"📌 **Команды:**\n"
        f"• `Банк пополнить [сумма]`\n"
        f"• `Банк снять [сума]`\n"
        f"• `Банк прокачать`\n\n"
        f"💡 Каждый час начисляется {percent:.2f}% от суммы в банке!",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text.startswith("Банк пополнить"))
async def bank_deposit(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ *Пример:* `Банк пополнить 1000`", parse_mode="Markdown")
        return
    try:
        amount = int(parts[2])
    except:
        await message.answer("❌ *Введи число!*", parse_mode="Markdown")
        return
    if amount < 1:
        await message.answer("❌ *Минимальная сумма: 1 ₽*", parse_mode="Markdown")
        return
    user = init_user(message.from_user.id, message.from_user.username)
    if user['balance'] < amount:
        await message.answer(f"❌ *Не хватает!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= amount
    user['bank'] = user.get('bank', 0) + amount
    save_user(message.from_user.id, user)
    update_quest_progress(message.from_user.id, "bank_deposit", amount)
    await message.answer(f"✅ +{amount:,} ₽ в банк!\n💰 На руках: {user['balance']:,} ₽\n🏦 В банке: {user['bank']:,} ₽", parse_mode="Markdown")

@dp.message(lambda msg: msg.text.startswith("Банк снять"))
async def bank_withdraw(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ *Пример:* `Банк снять 1000`", parse_mode="Markdown")
        return
    try:
        amount = int(parts[2])
    except:
        await message.answer("❌ *Введи число!*", parse_mode="Markdown")
        return
    if amount < 1:
        await message.answer("❌ *Минимальная сумма: 1 ₽*", parse_mode="Markdown")
        return
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('bank', 0) < amount:
        await message.answer(f"❌ *В банке только {user.get('bank', 0):,} ₽*", parse_mode="Markdown")
        return
    percent = get_bank_percent(user['bank_level'])
    tax = int(amount * 0.04)
    final = amount - tax
    user['bank'] -= amount
    user['balance'] += final
    save_user(message.from_user.id, user)
    await message.answer(
        f"✅ -{amount:,} ₽ из банка!\n"
        f"💱 Налог (4%): -{tax:,} ₽\n"
        f"💰 Получено на руки: {final:,} ₽\n"
        f"🏦 Осталось в банке: {user['bank']:,} ₽",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "Банк прокачать")
async def upgrade_bank(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    cost = get_upgrade_cost(user['bank_level'])
    if user['balance'] < cost:
        await message.answer(f"❌ *Не хватает!* Нужно {cost:,} ₽\n💰 У тебя: {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['bank_level'] += 1
    save_user(message.from_user.id, user)
    new_percent = get_bank_percent(user['bank_level'])
    await message.answer(
        f"✅ **УРОВЕНЬ БАНКА ПОВЫШЕН!**\n\n"
        f"📈 Новый уровень: {user['bank_level']}\n"
        f"💰 Новый процент: {new_percent:.2f}%/час\n"
        f"💎 Следующая прокачка: {get_upgrade_cost(user['bank_level']):,} ₽",
        parse_mode="Markdown"
    )

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
        update_quest_progress(message.from_user.id, "money", 0, income)
        await message.answer(f"🏢 **Бизнес принёс доход!**\n💰 +{income:,} ₽", parse_mode="Markdown")
    await message.answer(
        "🏢 **БИЗНЕС** 🏢\n\n"
        "• `Купить бизнес` — 50,000 ₽\n"
        "• `Продать бизнес` — 25,000 ₽\n"
        "• `Улучшить бизнес` — повысить доход\n\n"
        f"📊 Твой бизнес: {user.get('business') or '❌ Нет'}\n"
        f"📈 Уровень: {user.get('business_level', 1)}\n"
        f"💰 Доход: {500 * user.get('business_level', 1):,} ₽/час",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "Купить бизнес")
async def buy_business(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('business'):
        await message.answer("❌ *У тебя уже есть бизнес!*", parse_mode="Markdown")
        return
    cost = 50000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['business'] = "Магазин"
    user['last_business'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    update_quest_progress(message.from_user.id, "buy_business")
    await message.answer("✅ **Ты купил бизнес!**\n💰 Теперь ты получаешь 500 ₽ каждый час!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Продать бизнес")
async def sell_business(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('business'):
        await message.answer("❌ *У тебя нет бизнеса!*", parse_mode="Markdown")
        return
    sell_price = 25000
    user['balance'] += sell_price
    user['business'] = None
    save_user(message.from_user.id, user)
    await message.answer(f"✅ **Ты продал бизнес!**\n💰 +{sell_price:,} ₽", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Улучшить бизнес")
async def upgrade_business(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('business'):
        await message.answer("❌ *У тебя нет бизнеса!*", parse_mode="Markdown")
        return
    cost = user.get('business_level', 1) * 25000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['business_level'] = user.get('business_level', 1) + 1
    save_user(message.from_user.id, user)
    new_income = 500 * user['business_level']
    await message.answer(
        f"✅ **БИЗНЕС УЛУЧШЕН!**\n\n"
        f"📈 Новый уровень: {user['business_level']}\n"
        f"💰 Новый доход: {new_income:,} ₽/час",
        parse_mode="Markdown"
    )

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
        update_quest_progress(message.from_user.id, "money", 0, income)
        await message.answer(f"🏭 **Генератор произвёл энергию!**\n💰 +{income:,} ₽", parse_mode="Markdown")
    await message.answer(
        "🏭 **ГЕНЕРАТОР** 🏭\n\n"
        "• `Купить генератор` — 100,000 ₽\n"
        "• `Продать генератор` — 50,000 ₽\n"
        "• `Улучшить генератор` — повысить доход\n\n"
        f"📊 Твой генератор: {user.get('generator') or '❌ Нет'}\n"
        f"📈 Уровень: {user.get('generator_level', 1)}\n"
        f"💰 Доход: {300 * user.get('generator_level', 1):,} ₽/2 часа",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "Купить генератор")
async def buy_generator(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('generator'):
        await message.answer("❌ *У тебя уже есть генератор!*", parse_mode="Markdown")
        return
    cost = 100000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['generator'] = "Солнечный генератор"
    user['last_generator'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ **Ты купил генератор!**\n💰 Теперь ты получаешь 300 ₽ каждые 2 часа!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Продать генератор")
async def sell_generator(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('generator'):
        await message.answer("❌ *У тебя нет генератора!*", parse_mode="Markdown")
        return
    sell_price = 50000
    user['balance'] += sell_price
    user['generator'] = None
    save_user(message.from_user.id, user)
    await message.answer(f"✅ **Ты продал генератор!**\n💰 +{sell_price:,} ₽", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Улучшить генератор")
async def upgrade_generator(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('generator'):
        await message.answer("❌ *У тебя нет генератора!*", parse_mode="Markdown")
        return
    cost = user.get('generator_level', 1) * 50000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['generator_level'] = user.get('generator_level', 1) + 1
    save_user(message.from_user.id, user)
    new_income = 300 * user['generator_level']
    await message.answer(
        f"✅ **ГЕНЕРАТОР УЛУЧШЕН!**\n\n"
        f"📈 Новый уровень: {user['generator_level']}\n"
        f"💰 Новый доход: {new_income:,} ₽/2 часа",
        parse_mode="Markdown"
    )

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
        update_quest_progress(message.from_user.id, "money", 0, income)
        await message.answer(f"🔋 **Ферма намайнила монеты!**\n💰 +{income:,} ₽", parse_mode="Markdown")
    await message.answer(
        "🔋 **МАЙНИНГ ФЕРМА** 🔋\n\n"
        "• `Купить ферму` — 30,000 ₽\n"
        "• `Продать ферму` — 15,000 ₽\n"
        "• `Улучшить ферму` — повысить доход\n\n"
        f"📊 Твоя ферма: {user.get('farm') or '❌ Нет'}\n"
        f"📈 Уровень: {user.get('farm_level', 1)}\n"
        f"💰 Доход: {300 * user.get('farm_level', 1):,} ₽/30 мин",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "Купить ферму")
async def buy_farm(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('farm'):
        await message.answer("❌ *У тебя уже есть ферма!*", parse_mode="Markdown")
        return
    cost = 30000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['farm'] = "Майнинг ферма"
    user['last_farm'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ **Ты купил ферму!**\n💰 Теперь ты получаешь 300 ₽ каждые 30 минут!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Продать ферму")
async def sell_farm(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('farm'):
        await message.answer("❌ *У тебя нет фермы!*", parse_mode="Markdown")
        return
    sell_price = 15000
    user['balance'] += sell_price
    user['farm'] = None
    save_user(message.from_user.id, user)
    await message.answer(f"✅ **Ты продал ферму!**\n💰 +{sell_price:,} ₽", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Улучшить ферму")
async def upgrade_farm(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('farm'):
        await message.answer("❌ *У тебя нет фермы!*", parse_mode="Markdown")
        return
    cost = user.get('farm_level', 1) * 15000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['farm_level'] = user.get('farm_level', 1) + 1
    save_user(message.from_user.id, user)
    new_income = 300 * user['farm_level']
    await message.answer(
        f"✅ **ФЕРМА УЛУЧШЕНА!**\n\n"
        f"📈 Новый уровень: {user['farm_level']}\n"
        f"💰 Новый доход: {new_income:,} ₽/30 мин",
        parse_mode="Markdown"
    )# ============ КАРЬЕР ============
@dp.message(lambda msg: msg.text == "⚠️ Карьер")
async def quarry_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if user.get('quarry') and now - user.get('last_quarry', 0) >= 5400:
        income = 500 * user.get('quarry_level', 1)
        user['balance'] += income
        user['last_quarry'] = now
        save_user(message.from_user.id, user)
        update_quest_progress(message.from_user.id, "money", 0, income)
        await message.answer(f"⚠️ **Карьер добыл ресурсы!**\n💰 +{income:,} ₽", parse_mode="Markdown")
    await message.answer(
        "⚠️ **КАРЬЕР** ⚠️\n\n"
        "• `Купить карьер` — 80,000 ₽\n"
        "• `Продать карьер` — 40,000 ₽\n"
        "• `Улучшить карьер` — повысить доход\n\n"
        f"📊 Твой карьер: {user.get('quarry') or '❌ Нет'}\n"
        f"📈 Уровень: {user.get('quarry_level', 1)}\n"
        f"💰 Доход: {500 * user.get('quarry_level', 1):,} ₽/1.5 часа",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "Купить карьер")
async def buy_quarry(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('quarry'):
        await message.answer("❌ *У тебя уже есть карьер!*", parse_mode="Markdown")
        return
    cost = 80000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['quarry'] = "Каменный карьер"
    user['last_quarry'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ **Ты купил карьер!**\n💰 Теперь ты получаешь 500 ₽ каждые 1.5 часа!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Продать карьер")
async def sell_quarry(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('quarry'):
        await message.answer("❌ *У тебя нет карьера!*", parse_mode="Markdown")
        return
    sell_price = 40000
    user['balance'] += sell_price
    user['quarry'] = None
    save_user(message.from_user.id, user)
    await message.answer(f"✅ **Ты продал карьер!**\n💰 +{sell_price:,} ₽", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Улучшить карьер")
async def upgrade_quarry(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('quarry'):
        await message.answer("❌ *У тебя нет карьера!*", parse_mode="Markdown")
        return
    cost = user.get('quarry_level', 1) * 40000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['quarry_level'] = user.get('quarry_level', 1) + 1
    save_user(message.from_user.id, user)
    new_income = 500 * user['quarry_level']
    await message.answer(
        f"✅ **КАРЬЕР УЛУЧШЕН!**\n\n"
        f"📈 Новый уровень: {user['quarry_level']}\n"
        f"💰 Новый доход: {new_income:,} ₽/1.5 часа",
        parse_mode="Markdown"
    )

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
        update_quest_progress(message.from_user.id, "money", 0, income)
        await message.answer(f"🌳 **Денежное дерево принесло плоды!**\n💰 +{income:,} ₽", parse_mode="Markdown")
    await message.answer(
        "🌳 **ДЕНЕЖНОЕ ДЕРЕВО** 🌳\n\n"
        "• `Купить дерево` — 20,000 ₽\n"
        "• `Продать дерево` — 10,000 ₽\n"
        "• `Улучшить дерево` — повысить доход\n\n"
        f"📊 Твоё дерево: {user.get('tree') or '❌ Нет'}\n"
        f"📈 Уровень: {user.get('tree_level', 1)}\n"
        f"💰 Доход: {200 * user.get('tree_level', 1):,} ₽/день",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "Купить дерево")
async def buy_tree(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('tree'):
        await message.answer("❌ *У тебя уже есть дерево!*", parse_mode="Markdown")
        return
    cost = 20000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['tree'] = "Денежное дерево"
    user['last_tree'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ **Ты купил дерево!**\n💰 Теперь ты получаешь 200 ₽ каждый день!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Продать дерево")
async def sell_tree(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('tree'):
        await message.answer("❌ *У тебя нет дерева!*", parse_mode="Markdown")
        return
    sell_price = 10000
    user['balance'] += sell_price
    user['tree'] = None
    save_user(message.from_user.id, user)
    await message.answer(f"✅ **Ты продал дерево!**\n💰 +{sell_price:,} ₽", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Улучшить дерево")
async def upgrade_tree(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('tree'):
        await message.answer("❌ *У тебя нет дерева!*", parse_mode="Markdown")
        return
    cost = user.get('tree_level', 1) * 10000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['tree_level'] = user.get('tree_level', 1) + 1
    save_user(message.from_user.id, user)
    new_income = 200 * user['tree_level']
    await message.answer(
        f"✅ **ДЕРЕВО УЛУЧШЕНО!**\n\n"
        f"📈 Новый уровень: {user['tree_level']}\n"
        f"💰 Новый доход: {new_income:,} ₽/день",
        parse_mode="Markdown"
    )

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
        update_quest_progress(message.from_user.id, "money", 0, income)
        await message.answer(f"🌿 **Сад принёс урожай!**\n💰 +{income:,} ₽", parse_mode="Markdown")
    await message.answer(
        "🌿 **САДЫ** 🌿\n\n"
        "• `Купить сад` — 40,000 ₽\n"
        "• `Продать сад` — 20,000 ₽\n"
        "• `Улучшить сад` — повысить доход\n"
        "• `Сад полить` — +100-500 ₽\n\n"
        f"📊 Твой сад: {user.get('garden') or '❌ Нет'}\n"
        f"📈 Уровень: {user.get('garden_level', 1)}\n"
        f"💰 Доход: {400 * user.get('garden_level', 1):,} ₽/6 часов",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "Купить сад")
async def buy_garden(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('garden'):
        await message.answer("❌ *У тебя уже есть сад!*", parse_mode="Markdown")
        return
    cost = 40000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['garden'] = "Волшебный сад"
    user['last_garden'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("✅ **Ты купил сад!**\n💰 Теперь ты получаешь 400 ₽ каждые 6 часов!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Продать сад")
async def sell_garden(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('garden'):
        await message.answer("❌ *У тебя нет сада!*", parse_mode="Markdown")
        return
    sell_price = 20000
    user['balance'] += sell_price
    user['garden'] = None
    save_user(message.from_user.id, user)
    await message.answer(f"✅ **Ты продал сад!**\n💰 +{sell_price:,} ₽", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "Улучшить сад")
async def upgrade_garden(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('garden'):
        await message.answer("❌ *У тебя нет сада!*", parse_mode="Markdown")
        return
    cost = user.get('garden_level', 1) * 20000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= cost
    user['garden_level'] = user.get('garden_level', 1) + 1
    save_user(message.from_user.id, user)
    new_income = 400 * user['garden_level']
    await message.answer(
        f"✅ **САД УЛУЧШЕН!**\n\n"
        f"📈 Новый уровень: {user['garden_level']}\n"
        f"💰 Новый доход: {new_income:,} ₽/6 часов",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "Сад полить")
async def water_garden(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('garden'):
        await message.answer("❌ *У тебя нет сада!*", parse_mode="Markdown")
        return
    now = datetime.now().timestamp()
    if now - user.get('last_water', 0) < 10800:
        left = int(10800 - (now - user.get('last_water', 0)))
        await message.answer(f"⏳ *Сад можно полить через {left // 60} минут*", parse_mode="Markdown")
        return
    user['last_water'] = now
    bonus = random.randint(100, 500)
    user['balance'] += bonus
    save_user(message.from_user.id, user)
    update_quest_progress(message.from_user.id, "money", 0, bonus)
    await message.answer(f"💦 **Ты полил сад!**\n💰 +{bonus:,} ₽", parse_mode="Markdown")

# ============ КЕЙСЫ ============
@dp.message(lambda msg: msg.text == "📦 Кейсы")
async def cases_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    cases = user.get('cases', {})
    text = f"""🧾 **Ваши кейсы:** {user['name']}
━━━━━━━━━━━━━━━━━━━━━
📦 Обычный кейс — {cases.get('common', 0)} шт.
🏵 Золотой кейс — {cases.get('gold', 0)} шт.
⚙ Рудный кейс — {cases.get('ore', 0)} шт.
🌌 Материальный кейс — {cases.get('material', 0)} шт.
━━━━━━━━━━━━━━━━━━━━━

🎁 **Доступные кейсы:**
1. Обычный — 50.000₽
2. Золотой — 150.000₽
3. Рудный — 50 ⚙
4. Материальный — 200 🌌
━━━━━━━━━━━━━━━━━━━━━

🔐 `Кейс открыть [1-4] [кол-во]`
🛒 `Купить кейс [1-4] [кол-во]`"""
    await message.answer(text, parse_mode="Markdown")

@dp.message(lambda msg: msg.text.startswith("Купить кейс"))
async def buy_case(message: types.Message):
    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("❌ *Пример:* `Купить кейс 1 5`\n\n1 — Обычный (50.000₽)\n2 — Золотой (150.000₽)\n3 — Рудный (50⚙)\n4 — Материальный (200🌌)", parse_mode="Markdown")
        return
    try:
        case_num = int(parts[2])
        amount = int(parts[3])
    except:
        await message.answer("❌ *Введи номер кейса и количество!*", parse_mode="Markdown")
        return
    
    prices = {
        1: {"name": "Обычный", "key": "common", "cost": 50000, "currency": "money"},
        2: {"name": "Золотой", "key": "gold", "cost": 150000, "currency": "money"},
        3: {"name": "Рудный", "key": "ore", "cost": 50, "currency": "ore"},
        4: {"name": "Материальный", "key": "material", "cost": 200, "currency": "stardust"}
    }
    
    if case_num not in prices:
        await message.answer("❌ *Номера кейсов: 1, 2, 3 или 4*", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    price_info = prices[case_num]
    total_cost = price_info["cost"] * amount
    
    if price_info["currency"] == "money":
        if user['balance'] < total_cost:
            await message.answer(f"❌ *Не хватает денег!* Нужно {total_cost:,} ₽", parse_mode="Markdown")
            return
        user['balance'] -= total_cost
    elif price_info["currency"] == "ore":
        if user.get('ore', 0) < total_cost:
            await message.answer(f"❌ *Не хватает руды!* Нужно {total_cost} ⚙", parse_mode="Markdown")
            return
        user['ore'] -= total_cost
    elif price_info["currency"] == "stardust":
        if user.get('stardust', 0) < total_cost:
            await message.answer(f"❌ *Не хватает звёздной пыли!* Нужно {total_cost} 🌌", parse_mode="Markdown")
            return
        user['stardust'] -= total_cost
    
    user['cases'][price_info["key"]] = user['cases'].get(price_info["key"], 0) + amount
    save_user(message.from_user.id, user)
    await message.answer(
        f"✅ **Покупка!**\n"
        f"📦 Куплено: {amount} {price_info['name']} кейс(ов)\n"
        f"💰 Цена: {total_cost:,} {price_info['currency']}\n"
        f"📊 Всего {price_info['name']} кейсов: {user['cases'].get(price_info['key'], 0)}",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text.startswith("Кейс открыть"))
async def open_case(message: types.Message):
    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("❌ *Пример:* `Кейс открыть 1 3`\n\n1 — Обычный\n2 — Золотой\n3 — Рудный\n4 — Материальный", parse_mode="Markdown")
        return
    try:
        case_num = int(parts[2])
        amount = int(parts[3])
    except:
        await message.answer("❌ *Введи номер кейса и количество!*", parse_mode="Markdown")
        return
    
    cases = {
        1: {"name": "Обычный", "key": "common", "currency": "money", "min": 50000, "max": 500000, "small_chance": 50},
        2: {"name": "Золотой", "key": "gold", "currency": "money", "min": 150000, "max": 700000, "small_chance": 60},
        3: {"name": "Рудный", "key": "ore", "currency": "ore", "min": 10, "max": 100, "small_chance": 50},
        4: {"name": "Материальный", "key": "material", "currency": "stardust", "min": 20, "max": 200, "small_chance": 50}
    }
    
    if case_num not in cases:
        await message.answer("❌ *Номера кейсов: 1, 2, 3 или 4*", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    case_info = cases[case_num]
    case_key = case_info["key"]
    
    if user['cases'].get(case_key, 0) < amount:
        await message.answer(f"❌ *У тебя только {user['cases'].get(case_key, 0)} {case_info['name']} кейс(ов)!*", parse_mode="Markdown")
        return
    
    user['cases'][case_key] -= amount
    
    total_reward = 0
    results = []
    
    for i in range(amount):
        rand = random.randint(1, 100)
        if rand <= case_info["small_chance"]:
            reward = random.randint(case_info["min"], case_info["min"] + (case_info["max"] - case_info["min"]) // 3)
            results.append(f"  {i+1}. 🟢 {reward:,} {case_info['currency']}")
        elif rand <= case_info["small_chance"] + 40:
            reward = random.randint(case_info["max"] - (case_info["max"] - case_info["min"]) // 3, case_info["max"])
            results.append(f"  {i+1}. 🔴 {reward:,} {case_info['currency']}")
        else:
            reward = random.randint(case_info["min"] + (case_info["max"] - case_info["min"]) // 3, case_info["max"] - (case_info["max"] - case_info["min"]) // 3)
            results.append(f"  {i+1}. 🟡 {reward:,} {case_info['currency']}")
        total_reward += reward
        
        if case_info["currency"] == "money":
            user['balance'] += reward
        elif case_info["currency"] == "ore":
            user['ore'] = user.get('ore', 0) + reward
        elif case_info["currency"] == "stardust":
            user['stardust'] = user.get('stardust', 0) + reward
    
    update_quest_progress(message.from_user.id, "open_case", amount)
    save_user(message.from_user.id, user)
    
    result_text = "\n".join(results[:20])
    if amount > 20:
        result_text += f"\n  ... и ещё {amount - 20} кейсов"
    
    await message.answer(
        f"📦 **ОТКРЫТИЕ {amount} {case_info['name']} КЕЙСОВ** 📦\n\n"
        f"{result_text}\n\n"
        f"📊 **ИТОГО:**\n"
        f"💰 +{total_reward:,} {case_info['currency']}",
        parse_mode="Markdown"
    )# ============ БОСС ============
@dp.message(lambda msg: msg.text == "👹 Босс")
async def boss_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    boss = load_boss()
    boss_hp = boss.get("hp", 1000000)
    boss_max_hp = boss.get("max_hp", 1000000)
    player_damage = boss.get("players", {}).get(str(message.from_user.id), {}).get("total_damage", 0)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Атаковать", callback_data="boss_attack"), InlineKeyboardButton(text="💪 Улучшить силу", callback_data="boss_upgrade")],
        [InlineKeyboardButton(text="🏆 Топ урона", callback_data="boss_top"), InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
    ])
    
    await message.answer(
        f"👹 **БОСС: ДРЕВНИЙ ТИТАН** 👹\n\n"
        f"❤️ Здоровье: {boss_hp:,} / {boss_max_hp:,}\n"
        f"⚔️ Твой урон за атаку: {user.get('boss_power', 100)}\n"
        f"📊 Твой общий урон: {player_damage:,}\n"
        f"💪 Улучшение силы: {user.get('boss_upgrades', 0)} ур.\n\n"
        f"💰 Следующая прокачка: {get_boss_upgrade_cost(user.get('boss_upgrades', 0)):,} ₽\n\n"
        f"🏆 Топ-100 игроков получат **ЗОЛОТОЙ КЕЙС**!",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "boss_attack")
async def boss_attack(callback: types.CallbackQuery):
    user = init_user(callback.from_user.id, callback.from_user.username)
    boss = load_boss()
    boss_hp = boss.get("hp", 1000000)
    
    if boss_hp <= 0:
        await callback.message.answer("👹 **БОСС УЖЕ ПОВЕРЖЕН!**\nОжидайте возрождения...", parse_mode="Markdown")
        await callback.answer()
        return
    
    damage = user.get('boss_power', 100)
    boss_hp -= damage
    if boss_hp < 0:
        boss_hp = 0
    
    # Сохраняем урон игрока
    player_stats = boss.get("players", {}).get(str(callback.from_user.id), {"total_damage": 0, "name": user['name']})
    player_stats["total_damage"] += damage
    player_stats["name"] = user['name']
    boss["players"][str(callback.from_user.id)] = player_stats
    boss["hp"] = boss_hp
    save_boss(boss)
    
    update_quest_progress(callback.from_user.id, "boss_hit")
    
    await callback.message.answer(
        f"⚔️ **АТАКА!** ⚔️\n\n"
        f"💥 Ты нанёс {damage} урона!\n"
        f"❤️ У босса осталось: {boss_hp:,} / {boss.get('max_hp', 1000000):,}\n\n"
        f"📊 Твой общий урон: {player_stats['total_damage']:,}",
        parse_mode="Markdown"
    )
    
    # Если босс умер
    if boss_hp <= 0:
        # Награда всем игрокам в топе
        top_players = sorted(boss["players"].items(), key=lambda x: x[1]["total_damage"], reverse=True)[:100]
        for i, (uid, data) in enumerate(top_players, 1):
            add_case(int(uid), "gold", 1)
            try:
                await bot.send_message(int(uid), f"👑 **БОСС ПОВЕРЖЕН!**\nТы в ТОП-100! Получен ЗОЛОТОЙ КЕЙС!", parse_mode="Markdown")
            except:
                pass
        
        # Возрождаем босса
        boss["hp"] = boss["max_hp"]
        boss["players"] = {}
        save_boss(boss)
        await callback.message.answer("👑 **БОСС ПОВЕРЖЕН!**\nВсе топ-100 игроков получили ЗОЛОТОЙ КЕЙС!\nБосс возродился!", parse_mode="Markdown")
    
    await callback.answer()

@dp.callback_query(lambda c: c.data == "boss_upgrade")
async def boss_upgrade(callback: types.CallbackQuery):
    user = init_user(callback.from_user.id, callback.from_user.username)
    upgrades = user.get('boss_upgrades', 0)
    cost = get_boss_upgrade_cost(upgrades)
    
    if user['balance'] < cost:
        await callback.message.answer(f"❌ *Не хватает денег!*\n💰 Нужно: {cost:,} ₽\n💰 У тебя: {user['balance']:,} ₽", parse_mode="Markdown")
        await callback.answer()
        return
    
    user['balance'] -= cost
    user['boss_upgrades'] = upgrades + 1
    user['boss_power'] = 100 + (user['boss_upgrades'] * 10)
    save_user(callback.from_user.id, user)
    
    next_cost = get_boss_upgrade_cost(upgrades + 1)
    await callback.message.answer(
        f"💪 **СИЛА АТАКИ УЛУЧШЕНА!** 💪\n\n"
        f"📈 Новая сила: {user['boss_power']}\n"
        f"💰 Стоимость: {cost:,} ₽\n"
        f"💎 Следующая прокачка: {next_cost:,} ₽",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "boss_top")
async def boss_top(callback: types.CallbackQuery):
    boss = load_boss()
    players = boss.get("players", {})
    sorted_players = sorted(players.items(), key=lambda x: x[1]["total_damage"], reverse=True)[:20]
    
    if not sorted_players:
        await callback.message.answer("🏆 **ТОП УРОНА ПО БОССУ** 🏆\n\nПока никто не наносил урон!", parse_mode="Markdown")
        await callback.answer()
        return
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    text = "👺 **ТОП ИГРОКОВ ПО УРОНУ** 👺\n━━━━━━━━━━━━━━━━━━━━━\n"
    for i, (uid, data) in enumerate(sorted_players[:20], 1):
        medal = medals[i-1] if i-1 < len(medals) else f"{i}️⃣"
        name = data.get('name', f"Игрок{uid[:4]}")
        text += f"{medal} {name} — нанёс {data['total_damage']:,} урона\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n👺 ТОП 100 игроков получат Кейс «Золотой»!"
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

# ============ ИГРЫ ============
@dp.message(lambda msg: msg.text == "🎮 Игры")
async def games_menu(message: types.Message):
    await message.answer(
        "🎲 **ВЫБЕРИ ИГРУ** 🎲\n\n"
        "👇 *Нажми на кнопку:* 👇\n\n"
        "💡 *Можно ставить любую сумму!*\n"
        "📌 Пример: `!слот 777`, `!кубик 500`, `!баскетбол 1000`",
        parse_mode="Markdown",
        reply_markup=games_keyboard
    )

# Игры через команды (любая ставка)
@dp.message(lambda msg: msg.text.startswith("!слот"))
async def slot_game(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ *Пример:* `!слот 100`", parse_mode="Markdown")
        return
    try:
        bet = int(parts[1])
    except:
        await message.answer("❌ *Введи сумму ставки числом!*", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    if bet < 1:
        await message.answer("❌ *Минимальная ставка: 1 ₽*", parse_mode="Markdown")
        return
    if bet > user['balance']:
        await message.answer(f"❌ *Не хватает!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    
    multiplier = random.choice([2, 2, 3, 3, 4, 5, 10])
    win_game = random.random() < 0.4
    
    await message.answer("🎰 **КРУТИМ БАРАБАНЫ...** 🎰")
    await asyncio.sleep(1)
    
    if win_game:
        win = bet * multiplier
        user['balance'] += win
        save_user(message.from_user.id, user)
        add_game_result(message.from_user.id, True)
        await message.answer(
            f"🎰 **СПИН** 🎰\n\n"
            f"✨ ВЫПАЛ x{multiplier}!\n"
            f"🎉 ПОБЕДА! +{win:,} ₽\n"
            f"💰 Новый баланс: {user['balance']:,} ₽",
            parse_mode="Markdown"
        )
    else:
        user['balance'] -= bet
        save_user(message.from_user.id, user)
        add_game_result(message.from_user.id, False)
        await message.answer(
            f"🎰 **СПИН** 🎰\n\n"
            f"💔 НИЧЕГО НЕ ВЫПАЛО...\n"
            f"😞 ПРОИГРЫШ! -{bet:,} ₽\n"
            f"💰 Новый баланс: {user['balance']:,} ₽",
            parse_mode="Markdown"
        )

@dp.message(lambda msg: msg.text.startswith("!кубик"))
async def dice_game(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ *Пример:* `!кубик 3 100`\n1-6 число и ставка", parse_mode="Markdown")
        return
    try:
        guess = int(parts[1])
        bet = int(parts[2])
    except:
        await message.answer("❌ *Введи число и ставку!*", parse_mode="Markdown")
        return
    
    if guess < 1 or guess > 6:
        await message.answer("❌ *Число должно быть от 1 до 6!*", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    if bet < 1:
        await message.answer("❌ *Минимальная ставка: 1 ₽*", parse_mode="Markdown")
        return
    if bet > user['balance']:
        await message.answer(f"❌ *Не хватает!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    
    roll = random.randint(1, 6)
    await message.answer(f"🎲 **БРОСАЮ КУБИК...** 🎲")
    await asyncio.sleep(1)
    
    if roll == guess:
        win = bet * 5
        user['balance'] += win
        save_user(message.from_user.id, user)
        add_game_result(message.from_user.id, True)
        await message.answer(
            f"🎲 **КУБИК** 🎲\n\n"
            f"Выпало: {roll}\n"
            f"Твоё число: {guess}\n"
            f"🎉 УГАДАЛ! +{win:,} ₽\n"
            f"💰 Новый баланс: {user['balance']:,} ₽",
            parse_mode="Markdown"
        )
    else:
        user['balance'] -= bet
        save_user(message.from_user.id, user)
        add_game_result(message.from_user.id, False)
        await message.answer(
            f"🎲 **КУБИК** 🎲\n\n"
            f"Выпало: {roll}\n"
            f"Твоё число: {guess}\n"
            f"😞 НЕ УГАДАЛ! -{bet:,} ₽\n"
            f"💰 Новый баланс: {user['balance']:,} ₽",
            parse_mode="Markdown"
        )

@dp.message(lambda msg: msg.text.startswith("!баскетбол"))
async def basketball_game(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ *Пример:* `!баскетбол 100`", parse_mode="Markdown")
        return
    try:
        bet = int(parts[1])
    except:
        await message.answer("❌ *Введи сумму ставки числом!*", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    if bet < 1:
        await message.answer("❌ *Минимальная ставка: 1 ₽*", parse_mode="Markdown")
        return
    if bet > user['balance']:
        await message.answer(f"❌ *Не хватает!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    
    win_game = random.choice([True, False])
    
    await message.answer("🏀 **БРОСАЮ МЯЧ...** 🏀")
    await asyncio.sleep(1)
    
    if win_game:
        win = bet * 2
        user['balance'] += win
        save_user(message.from_user.id, user)
        add_game_result(message.from_user.id, True)
        await message.answer(
            f"🏀 **БАСКЕТБОЛ** 🏀\n\n"
            f"🏀 ПОПАДАНИЕ!\n"
            f"🎉 ПОБЕДА! +{win:,} ₽\n"
            f"💰 Новый баланс: {user['balance']:,} ₽",
            parse_mode="Markdown"
        )
    else:
        user['balance'] -= bet
        save_user(message.from_user.id, user)
        add_game_result(message.from_user.id, False)
        await message.answer(
            f"🏀 **БАСКЕТБОЛ** 🏀\n\n"
            f"💔 ПРОМАХ!\n"
            f"😞 ПРОИГРЫШ! -{bet:,} ₽\n"
            f"💰 Новый баланс: {user['balance']:,} ₽",
            parse_mode="Markdown"
        )

# ============ АРЕНА ============
@dp.message(lambda msg: msg.text == "⚔️ Арена")
async def pvp_menu(message: types.Message):
    await message.answer(
        "⚔️ **АРЕНА** ⚔️\n\n"
        "Битва с другим игроком на ставку!\n"
        "Победитель забирает деньги и получает алмазы.\n\n"
        "👇 *Выбери ставку и ответь на сообщение противника:*",
        parse_mode="Markdown",
        reply_markup=pvP_keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("pvp_"))
async def pvp_bet(callback: types.CallbackQuery):
    amount = int(callback.data.split("_")[1])
    user_pvp_bet[callback.from_user.id] = amount
    await callback.message.answer(
        f"⚔️ *Ты выбрал ставку {amount} ₽*\n\n"
        f"📌 *Теперь ОТВЕТЬ НА СООБЩЕНИЕ ПРОТИВНИКА и напиши сумму {amount}*",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(lambda msg: msg.text.isdigit() and msg.reply_to_message)
async def pvp_fight(message: types.Message):
    amount = int(message.text)
    attacker_id = message.from_user.id
    defender_id = message.reply_to_message.from_user.id
    
    if attacker_id == defender_id:
        await message.answer("❌ *Нельзя бить самого себя!*", parse_mode="Markdown")
        return
    
    attacker = init_user(attacker_id, message.from_user.username)
    defender = init_user(defender_id, message.reply_to_message.from_user.first_name)
    
    if amount != user_pvp_bet.get(attacker_id, 0):
        await message.answer(f"❌ *Ставка должна быть {user_pvp_bet.get(attacker_id, 0)} ₽!*", parse_mode="Markdown")
        return
    
    if attacker['balance'] < amount:
        await message.answer(f"❌ *Не хватает денег!* У тебя {attacker['balance']:,} ₽", parse_mode="Markdown")
        return
    if defender['balance'] < amount:
        await message.answer(f"❌ *У противника нет {amount} ₽ для ставки!*", parse_mode="Markdown")
        return
    
    attacker_win = random.choice([True, False])
    
    if attacker_win:
        attacker['balance'] += amount
        defender['balance'] -= amount
        add_diamonds(attacker_id, 5)
        save_user(attacker_id, attacker)
        save_user(defender_id, defender)
        await message.answer(f"⚔️ **ПОБЕДА!**\n💰 +{amount} ₽ и +5💎!", parse_mode="Markdown")
        await bot.send_message(defender_id, f"⚔️ *Поражение на арене!* Ты проиграл {amount} ₽ игроку {attacker['name']}", parse_mode="Markdown")
    else:
        attacker['balance'] -= amount
        defender['balance'] += amount
        add_diamonds(defender_id, 5)
        save_user(attacker_id, attacker)
        save_user(defender_id, defender)
        await message.answer(f"⚔️ **ПОРАЖЕНИЕ!**\n😞 Ты проиграл {amount} ₽!", parse_mode="Markdown")
        await bot.send_message(defender_id, f"⚔️ **ПОБЕДА!**\n💰 +{amount} ₽ и +5💎!", parse_mode="Markdown")
    
    user_pvp_bet[attacker_id] = None

# ============ ИНВЕСТИЦИИ ============
@dp.message(lambda msg: msg.text == "💰 Инвестиции")
async def invest_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    invest_data = user.get('investments', {})
    current_price = invest_data.get('price', 100)
    shares = invest_data.get('shares', 0)
    await message.answer(
        f"💰 **ИНВЕСТИЦИИ** 💰\n\n"
        f"📈 Текущая цена актива: {current_price} ₽\n"
        f"📊 У тебя акций: {shares}\n"
        f"💎 Стоимость портфеля: {shares * current_price:,} ₽\n\n"
        f"👇 *Выбери действие:*",
        parse_mode="Markdown",
        reply_markup=invest_keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("invest_"))
async def invest_action(callback: types.CallbackQuery):
    user = init_user(callback.from_user.id, callback.from_user.username)
    invest_data = user.get('investments', {})
    current_price = invest_data.get('price', 100)
    shares = invest_data.get('shares', 0)
    
    if callback.data == "invest_sell":
        if shares > 0:
            profit = shares * current_price
            user['balance'] += profit
            user['investments'] = {'price': current_price, 'shares': 0}
            save_user(callback.from_user.id, user)
            await callback.message.answer(f"✅ *Ты продал {shares} акций за {profit:,} ₽!*", parse_mode="Markdown")
        else:
            await callback.message.answer("❌ *У тебя нет акций!*", parse_mode="Markdown")
    else:
        amount = int(callback.data.split("_")[1])
        if user['balance'] >= amount:
            new_shares = amount // current_price
            if new_shares > 0:
                user['balance'] -= new_shares * current_price
                invest_data['shares'] = invest_data.get('shares', 0) + new_shares
                user['investments'] = invest_data
                save_user(callback.from_user.id, user)
                await callback.message.answer(f"✅ *Ты купил {new_shares} акций по {current_price} ₽!*", parse_mode="Markdown")
            else:
                await callback.message.answer(f"❌ *Сумма слишком мала! Цена акции {current_price} ₽*", parse_mode="Markdown")
        else:
            await callback.message.answer(f"❌ *Не хватает денег!*", parse_mode="Markdown")
    
    # Изменяем цену случайно
    change = random.uniform(0.95, 1.05)
    new_price = int(current_price * change)
    if new_price < 50:
        new_price = 50
    if new_price > 500:
        new_price = 500
    user['investments']['price'] = new_price
    save_user(callback.from_user.id, user)
    await callback.answer()
    # ============ КЛАНЫ ============
@dp.message(lambda msg: msg.text == "🏛 Кланы")
async def clans_menu(message: types.Message):
    await message.answer(
        "🏛 **КЛАНЫ** 🏛\n\n"
        "• `📋 Список кланов` — посмотреть все кланы\n"
        "• `➕ Создать клан [название]` — создать клан (50.000₽)\n"
        "• `🚪 Вступить в клан [название]` — вступить в клан\n"
        "• `💰 Внести в казну [сумма]` — пополнить казну клана\n\n"
        "✨ *Клановые бонусы:* +5% к доходу от бизнеса!",
        parse_mode="Markdown",
        reply_markup=clan_keyboard
    )

@dp.callback_query(lambda c: c.data == "clan_list")
async def clan_list(callback: types.CallbackQuery):
    clans = load_clans()
    if not clans:
        await callback.message.answer("📋 *Список кланов пуст!*\nСоздай свой клан!", parse_mode="Markdown")
        await callback.answer()
        return
    
    text = "🏛 **СПИСОК КЛАНОВ** 🏛\n━━━━━━━━━━━━━━━━━━━━━\n"
    for name, data in clans.items():
        text += f"📌 {name} — участников: {len(data.get('members', []))}, казна: {data.get('treasury', 0):,} ₽\n"
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "clan_create")
async def clan_create_prompt(callback: types.CallbackQuery):
    await callback.message.answer("📝 *Введи название клана:*\n`Создать клан Название`", parse_mode="Markdown")
    user_clan_create[callback.from_user.id] = True
    await callback.answer()

@dp.callback_query(lambda c: c.data == "clan_join")
async def clan_join_prompt(callback: types.CallbackQuery):
    await callback.message.answer("📝 *Введи название клана для вступления:*\n`Вступить в клан Название`", parse_mode="Markdown")
    user_clan_join[callback.from_user.id] = True
    await callback.answer()

@dp.callback_query(lambda c: c.data == "clan_donate")
async def clan_donate_prompt(callback: types.CallbackQuery):
    await callback.message.answer("💰 *Введи сумму для пополнения казны:*\n`Внести в казну 10000`", parse_mode="Markdown")
    await callback.answer()

@dp.message(lambda msg: msg.text.startswith("Создать клан"))
async def create_clan(message: types.Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("❌ *Пример:* `Создать клан Воины`", parse_mode="Markdown")
        return
    clan_name = parts[2][:20]
    user = init_user(message.from_user.id, message.from_user.username)
    
    if user.get('clan'):
        await message.answer("❌ *Ты уже в клане!*", parse_mode="Markdown")
        return
    
    clans = load_clans()
    if clan_name in clans:
        await message.answer("❌ *Клан с таким названием уже существует!*", parse_mode="Markdown")
        return
    
    cost = 50000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost:,} ₽ для создания клана!*", parse_mode="Markdown")
        return
    
    user['balance'] -= cost
    user['clan'] = clan_name
    save_user(message.from_user.id, user)
    
    clans[clan_name] = {
        "owner": str(message.from_user.id),
        "members": [str(message.from_user.id)],
        "treasury": 0,
        "created": datetime.now().timestamp()
    }
    save_clans(clans)
    await message.answer(f"✅ **Клан «{clan_name}» создан!**", parse_mode="Markdown")
    user_clan_create[message.from_user.id] = False

@dp.message(lambda msg: msg.text.startswith("Вступить в клан"))
async def join_clan(message: types.Message):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 3:
        await message.answer("❌ *Пример:* `Вступить в клан Воины`", parse_mode="Markdown")
        return
    clan_name = parts[2]
    user = init_user(message.from_user.id, message.from_user.username)
    
    if user.get('clan'):
        await message.answer("❌ *Ты уже в клане!*", parse_mode="Markdown")
        return
    
    clans = load_clans()
    if clan_name not in clans:
        await message.answer("❌ *Клан не найден!*", parse_mode="Markdown")
        return
    
    clans[clan_name]["members"].append(str(message.from_user.id))
    save_clans(clans)
    user['clan'] = clan_name
    save_user(message.from_user.id, user)
    await message.answer(f"✅ **Ты вступил в клан «{clan_name}»!**", parse_mode="Markdown")
    user_clan_join[message.from_user.id] = False

@dp.message(lambda msg: msg.text.startswith("Внести в казну"))
async def donate_to_clan(message: types.Message):
    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("❌ *Пример:* `Внести в казну 10000`", parse_mode="Markdown")
        return
    try:
        amount = int(parts[3])
    except:
        await message.answer("❌ *Введи сумму числом!*", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    clan_name = user.get('clan')
    if not clan_name:
        await message.answer("❌ *Ты не в клане!*", parse_mode="Markdown")
        return
    
    if user['balance'] < amount:
        await message.answer(f"❌ *Не хватает!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    
    clans = load_clans()
    if clan_name not in clans:
        await message.answer("❌ *Клан не найден!*", parse_mode="Markdown")
        return
    
    user['balance'] -= amount
    clans[clan_name]["treasury"] = clans[clan_name].get("treasury", 0) + amount
    save_user(message.from_user.id, user)
    save_clans(clans)
    await message.answer(f"✅ **Ты внёс {amount:,} ₽ в казну клана «{clan_name}»!**", parse_mode="Markdown")

# ============ ЛОТЕРЕЯ ============
@dp.message(lambda msg: msg.text == "🎰 Лотерея")
async def lottery_menu(message: types.Message):
    lottery = load_lottery()
    await message.answer(
        f"🎰 **ЛОТЕРЕЯ** 🎰\n\n"
        f"💰 Джекпот: {lottery.get('jackpot', 10000):,} ₽\n"
        f"🎫 Билетов продано: {len(lottery.get('tickets', []))}\n\n"
        f"📌 *Купить билет:* `Купить билет` (1000 ₽)\n"
        f"🎲 Розыгрыш каждый час!",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "Купить билет")
async def buy_ticket(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    cost = 1000
    if user['balance'] < cost:
        await message.answer(f"❌ *Нужно {cost} ₽!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    
    user['balance'] -= cost
    save_user(message.from_user.id, user)
    
    lottery = load_lottery()
    lottery['jackpot'] = lottery.get('jackpot', 10000) + cost
    lottery['tickets'].append(str(message.from_user.id))
    save_lottery(lottery)
    await message.answer(f"✅ *Билет куплен!* Твой номер: {len(lottery['tickets'])}\n🎲 Розыгрыш каждый час!", parse_mode="Markdown")

# ============ МАГАЗИН ============
@dp.message(lambda msg: msg.text == "🛒 Магазин")
async def shop_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"🛒 **МАГАЗИН** 🛒\n\n"
        f"🍀 *Зелье удачи* — 100💎\n"
        f"   Увеличивает шанс выигрыша в играх на 10%\n\n"
        f"🛡️ *Защита от проигрыша* — 200💎\n"
        f"   Защищает от проигрыша 1 раз\n\n"
        f"⚡ *Двойной доход* — 150💎\n"
        f"   Удваивает доход от бизнеса на 1 час\n\n"
        f"💎 Твои алмазы: {user.get('diamonds', 0)}\n\n"
        f"📌 *Купить:* `Купить предмет [название]`\n"
        f"📌 Пример: `Купить предмет удача`",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text.startswith("Купить предмет"))
async def buy_item(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ *Пример:* `Купить предмет удача`", parse_mode="Markdown")
        return
    item = parts[2].lower()
    
    user = init_user(message.from_user.id, message.from_user.username)
    items = {
        "удача": {"cost": 100, "key": "luck", "name": "Зелье удачи"},
        "защита": {"cost": 200, "key": "shield", "name": "Защита от проигрыша"},
        "доход": {"cost": 150, "key": "double_income", "name": "Двойной доход"}
    }
    
    if item not in items:
        await message.answer("❌ *Доступные предметы:* удача, защита, доход", parse_mode="Markdown")
        return
    
    item_info = items[item]
    if user.get('diamonds', 0) < item_info["cost"]:
        await message.answer(f"❌ *Не хватает алмазов!* Нужно {item_info['cost']}💎", parse_mode="Markdown")
        return
    
    user['diamonds'] -= item_info["cost"]
    user['shop_items'][item_info["key"]] = user['shop_items'].get(item_info["key"], 0) + 1
    save_user(message.from_user.id, user)
    await message.answer(f"✅ *Ты купил {item_info['name']}!*", parse_mode="Markdown")

# ============ ОФОРМЛЕНИЕ ============
@dp.message(lambda msg: msg.text == "🎨 Оформление")
async def frame_shop(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"🎨 **ОФОРМЛЕНИЕ** 🎨\n\n"
        f"📄 *Обычная рамка* — 0💎\n"
        f"✨ *Золотая рамка* — 100💎\n"
        f"💎 *Алмазная рамка* — 300💎\n"
        f"👑 *Королевская рамка* — 500💎\n\n"
        f"🖼️ Твоя рамка: {user.get('frame', '📄 Обычная')}\n"
        f"💎 Алмазов: {user.get('diamonds', 0)}\n\n"
        f"👇 *Выбери новую рамку:*",
        parse_mode="Markdown",
        reply_markup=frame_keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("frame_"))
async def buy_frame(callback: types.CallbackQuery):
    frame_type = callback.data.replace("frame_", "")
    user = init_user(callback.from_user.id, callback.from_user.username)
    frames = {
        "normal": {"name": "📄 Обычная", "cost": 0},
        "gold": {"name": "✨ Золотая", "cost": 100},
        "diamond": {"name": "💎 Алмазная", "cost": 300},
        "royal": {"name": "👑 Королевская", "cost": 500}
    }
    if frame_type in frames:
        if user.get('diamonds', 0) >= frames[frame_type]["cost"]:
            user['diamonds'] -= frames[frame_type]["cost"]
            user['frame'] = frames[frame_type]["name"]
            save_user(callback.from_user.id, user)
            await callback.message.answer(f"✅ *Ты купил рамку {frames[frame_type]['name']}!*", parse_mode="Markdown")
        else:
            await callback.message.answer(f"❌ *Не хватает алмазов!* Нужно {frames[frame_type]['cost']}💎", parse_mode="Markdown")
    await callback.answer()

# ============ ПРОФИЛЬ ============
@dp.message(lambda msg: msg.text == "⭐ Профиль")
async def profile(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    rank, next_rank, need = get_rank_info(message.from_user.id)
    await message.answer(
        f"👤 **ПРОФИЛЬ** 👤\n\n"
        f"📛 Ник: {user['name']}\n"
        f"💰 Баланс: {user['balance']:,} ₽\n"
        f"🏦 В банке: {user.get('bank', 0):,} ₽\n"
        f"💎 Алмазов: {user.get('diamonds', 0)}\n"
        f"⚙ Руды: {user.get('ore', 0)}\n"
        f"🌌 Звёздной пыли: {user.get('stardust', 0)}\n"
        f"🏆 Ранг: {rank}\n"
        f"🎨 Рамка: {user.get('frame', '📄 Обычная')}\n"
        f"⭐ Опыт: {user['exp']}\n"
        f"🎚️ Уровень: {user['level']}\n"
        f"🏆 Побед в играх: {user.get('wins', 0)}\n"
        f"🎮 Сыграно игр: {user.get('games_played', 0)}\n"
        f"👹 Урон по боссу: {user.get('boss_damage', 0)}\n"
        f"💪 Сила атаки: {user.get('boss_power', 100)}\n"
        f"💒 Брак: {user.get('married_to') or '❌ Нет'}\n"
        f"🏛 Клан: {user.get('clan') or '❌ Нет'}",
        parse_mode="Markdown"
    )

# ============ РАНГИ ============
@dp.message(lambda msg: msg.text == "🏆 Ранги")
async def show_rank(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    rank, next_rank, need = get_rank_info(message.from_user.id)
    achievements = user.get('achievements', {})
    ach_text = ""
    for ach in achievements:
        ach_text += f"✅ {ach}\n"
    if not ach_text:
        ach_text = "Пока нет достижений"
    await message.answer(
        f"🏆 **ТВОЙ РАНГ** 🏆\n\n"
        f"📛 {rank}\n"
        f"💰 Баланс: {user['balance']:,} ₽\n"
        f"➡️ Следующий ранг: {next_rank}\n"
        f"📊 Осталось: {need:,} ₽\n\n"
        f"🏅 **ДОСТИЖЕНИЯ:**\n{ach_text}",
        parse_mode="Markdown"
    )

# ============ АЛМАЗЫ ============
@dp.message(lambda msg: msg.text == "💎 Алмазы")
async def show_diamonds(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"💎 **ТВОИ АЛМАЗЫ** 💎\n\n"
        f"📊 У тебя: {user.get('diamonds', 0)} 💎\n\n"
        f"✨ Алмазы можно получить за:\n"
        f"• Выполнение квестов\n"
        f"• Победы на арене\n"
        f"• Достижения\n"
        f"• Повышение уровня\n\n"
        f"🎨 Тратить алмазы можно в разделе «Оформление» и «Магазин»",
        parse_mode="Markdown"
    )

# ============ КВЕСТЫ ============
@dp.message(lambda msg: msg.text == "📋 Квесты")
async def show_quests(message: types.Message):
    quests = get_daily_quests(message.from_user.id)
    text = "📋 **ЕЖЕДНЕВНЫЕ КВЕСТЫ** 📋\n━━━━━━━━━━━━━━━━━━━━━\n"
    for q in quests:
        text += f"• {q['name']}: {q['progress']}/{q['target']} (награда: {q['reward']}₽ + {q['reward']//2}💎)\n"
    await message.answer(text, parse_mode="Markdown")

# ============ БОНУС ============
@dp.message(lambda msg: msg.text == "🎁 Бонус")
async def daily_bonus(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if now - user.get('last_daily', 0) < 86400:
        left = int(24 - (now - user.get('last_daily', 0)) // 3600)
        await message.answer(f"⏰ *Бонус через {left} часов*", parse_mode="Markdown")
        return
    bonus = 500
    user['balance'] += bonus
    user['last_daily'] = now
    save_user(message.from_user.id, user)
    await message.answer(f"🎁 *ЕЖЕДНЕВНЫЙ БОНУС!*\n💰 +{bonus} ₽\n💰 Баланс: {user['balance']:,} ₽", parse_mode="Markdown")

# ============ ПОМОЩЬ ============
@dp.message(lambda msg: msg.text == "❓ Помощь")
async def help_command(message: types.Message):
    await message.answer(
        "📖 **ПОМОЩЬ** 📖\n\n"
        "💰 **Баланс** — проверить деньги и ресурсы\n"
        "🏦 **Банк** — пополнить/снять (налог 4%), прокачка уровня\n"
        "🗄 **Бизнес** — купить/продать/улучшить (500₽/час)\n"
        "🏭 **Генератор** — купить/продать/улучшить (300₽/2ч)\n"
        "🧰 **Майнинг** — купить/продать/улучшить (300₽/30мин)\n"
        "⚠️ **Карьер** — купить/продать/улучшить (500₽/1.5ч)\n"
        "🌳 **Дерево** — купить/продать/улучшить (200₽/день)\n"
        "🌿 **Сады** — купить/продать/улучшить/полить (400₽/6ч)\n"
        "📦 **Кейсы** — купить/открыть (Обычный, Золотой, Рудный, Материальный)\n"
        "💒 **Браки** — /marry, /divorce, /marriage\n"
        "🎮 **Игры** — !слот, !кубик, !баскетбол (любая ставка)\n"
        "🏆 **Ранги** — система рангов и достижения\n"
        "💎 **Алмазы** — новая валюта для магазина\n"
        "🎨 **Оформление** — рамки для профиля\n"
        "📋 **Квесты** — ежедневные задания\n"
        "⚔️ **Арена** — PvP битвы на ставку\n"
        "💰 **Инвестиции** — биржевая игра\n"
        "👹 **Босс** — атакуй босса, топ-100 получают Золотой кейс\n"
        "🏛 **Кланы** — создавай/вступай в кланы\n"
        "🎰 **Лотерея** — купи билет, выиграй джекпот\n"
        "🛒 **Магазин** — покупай предметы за алмазы\n"
        "🎁 **Бонус** — 500₽ раз в день\n"
        "⭐ **Профиль** — полная статистика\n\n"
        "🔐 **Промокод `Ванёк`** — 10 квинтиллионов (1000 активаций)",
        parse_mode="Markdown"
    )

# ============ НАЗАД ============
@dp.callback_query(lambda c: c.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.answer("◀️ *Главное меню*", parse_mode="Markdown", reply_markup=main_keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_games")
async def back_to_games(callback: types.CallbackQuery):
    await callback.message.answer("🎲 *ВЫБЕРИ ИГРУ* 🎲", parse_mode="Markdown", reply_markup=games_keyboard)
    await callback.answer()

# ============ ПРОЦЕНТЫ НА БАНК (ФОН) ============
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
        print("✅ Проценты на банк начислены")

# ============ ЛОТЕРЕЯ (ФОН) ============
async def lottery_worker():
    while True:
        await asyncio.sleep(3600)
        lottery = load_lottery()
        tickets = lottery.get('tickets', [])
        if tickets:
            winner_id = random.choice(tickets)
            prize = lottery.get('jackpot', 10000)
            try:
                await bot.send_message(int(winner_id), f"🎉 **ВЫ ВЫИГРАЛИ В ЛОТЕРЕЮ!** 🎉\n💰 +{prize:,} ₽", parse_mode="Markdown")
                user = init_user(int(winner_id), "")
                user['balance'] += prize
                save_user(int(winner_id), user)
            except:
                pass
            lottery['jackpot'] = 10000
            lottery['tickets'] = []
        save_lottery(lottery)
        print("✅ Лотерея разыграна")

# ============ ЗАПУСК ============
async def main():
    print("🤖 Бот запущен!")
    print("✅ Retro 19? — полная экономическая игра")
    print("✅ Все команды работают!")
    
    # Запускаем фоновые задачи
    asyncio.create_task(bank_profit_worker())
    asyncio.create_task(lottery_worker())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
