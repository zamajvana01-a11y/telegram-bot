import asyncio
import json
import os
import random
import time
import logging
import asyncpg
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ========== ЛОГГИРОВАНИЕ ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TOKEN = "7139683001:AAFpIMrMSENgZwiKLOpYlROymbXJFOjO5oQ"
DATABASE_URL = os.getenv("DATABASE_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()

YOUR_USER_ID = 8464236397

balance_messages = {}
profile_messages = {}

# ========== БАЗА ДАННЫХ ==========
async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            name TEXT DEFAULT 'Игрок',
            balance BIGINT DEFAULT 5000,
            bank BIGINT DEFAULT 0,
            bank_level INT DEFAULT 1,
            limit_level INT DEFAULT 1,
            last_bonus BIGINT DEFAULT 0,
            last_promo BIGINT DEFAULT 0,
            total_bets INT DEFAULT 0,
            total_wins INT DEFAULT 0,
            invited INT DEFAULT 0,
            premium INT DEFAULT 0
        )
    ''')
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS promos (
            name TEXT PRIMARY KEY,
            used BOOLEAN DEFAULT FALSE
        )
    ''')
    # Добавляем промокоды если их нет
    await conn.execute('''
        INSERT INTO promos (name, used) VALUES ('PROMO_VANEK', FALSE)
        ON CONFLICT (name) DO NOTHING
    ''')
    await conn.execute('''
        INSERT INTO promos (name, used) VALUES ('VANEK_100B', FALSE)
        ON CONFLICT (name) DO NOTHING
    ''')
    await conn.close()
    logger.info("✅ База данных готова")

async def get_user(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
    if not row:
        await conn.execute('''
            INSERT INTO users (user_id, balance) VALUES ($1, 5000)
        ''', user_id)
        row = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
    await conn.close()
    return dict(row)

async def update_user(user_id, **kwargs):
    conn = await asyncpg.connect(DATABASE_URL)
    for key, value in kwargs.items():
        await conn.execute(f'UPDATE users SET {key} = $1 WHERE user_id = $2', value, user_id)
    await conn.close()

async def get_all_users():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch('SELECT * FROM users')
    await conn.close()
    return [dict(row) for row in rows]

async def get_promo(name):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT * FROM promos WHERE name = $1", name)
    await conn.close()
    return dict(row) if row else {"used": False}

async def set_promo_used(name):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("UPDATE promos SET used = TRUE WHERE name = $1", name)
    await conn.close()

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

# ========== ФОНОВЫЕ ЗАДАЧИ ==========
async def bank_profit_worker():
    await asyncio.sleep(10)
    while True:
        try:
            await asyncio.sleep(3600)
            users = await get_all_users()
            for user in users:
                try:
                    if user.get('bank', 0) > 0:
                        percent = get_bank_percent(user.get('bank_level', 1))
                        profit = int(user['bank'] * percent / 100)
                        if profit > 0:
                            await update_user(user['user_id'], bank=user['bank'] + profit)
                            try:
                                await bot.send_message(
                                    user['user_id'],
                                    f"🏦 **Вам пришло: {profit} ₽**\n📊 Процент: {percent}% | Уровень банка: {user.get('bank_level', 1)}",
                                    parse_mode="Markdown"
                                )
                            except:
                                pass
                except Exception as e:
                    logger.error(f"Ошибка в bank_profit для {user.get('user_id')}: {e}")
            logger.info("✅ Проценты на банк начислены")
        except Exception as e:
            logger.error(f"КРИТИЧЕСКАЯ ошибка в bank_profit_worker: {e}")
            await asyncio.sleep(10)

async def personal_bonus_worker():
    await asyncio.sleep(5)
    while True:
        try:
            await asyncio.sleep(7200)
            user = await get_user(YOUR_USER_ID)
            await update_user(YOUR_USER_ID, balance=user['balance'] + 100000000)
            try:
                await bot.send_message(
                    YOUR_USER_ID,
                    f"🎁 **ЛИЧНЫЙ БОНУС!**\n💰 +100.000.000 ₽\n⏰ Следующий через 2 часа!",
                    parse_mode="Markdown"
                )
            except:
                pass
            logger.info("✅ Личный бонус начислен")
        except Exception as e:
            logger.error(f"КРИТИЧЕСКАЯ ошибка в personal_bonus_worker: {e}")
            await asyncio.sleep(10)

async def cleanup_old_messages():
    while True:
        try:
            await asyncio.sleep(3600)
            if len(balance_messages) > 1000:
                balance_messages.clear()
            if len(profile_messages) > 1000:
                profile_messages.clear()
        except Exception as e:
            logger.error(f"Ошибка в cleanup_old_messages: {e}")

# ========== КОМАНДЫ ==========
@dp.message(Command("id"))
async def show_id(message: types.Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Нет username"
        first_name = message.from_user.first_name or ""
        last_name = message.from_user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        await message.answer(
            f"🆔 **ТВОЙ ID**\n\n📛 Имя: {full_name}\n👤 Username: @{username}\n🔢 ID: `{user_id}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка в /id: {e}")

@dp.message(Command("clear_duplicates"))
async def clear_duplicates(message: types.Message):
    if message.from_user.id != YOUR_USER_ID:
        await message.answer("❌ Только для создателя бота!")
        return
    await message.answer("✅ База данных сама не допускает дубликатов!")

@dp.message(Command("start"))
async def start(message: types.Message):
    try:
        await get_user(message.from_user.id)
        promo_vanek = await get_promo('PROMO_VANEK')
        promo_vanek_100b = await get_promo('VANEK_100B')
        promo_text = ""
        if not promo_vanek.get('used', False):
            promo_text += "\n\n🎁 Промокод: ПРОМО: ВАНЁК (1 септиллион, 1 раз)"
        if not promo_vanek_100b.get('used', False):
            promo_text += "\n\n🔥 Промокод: Ванёк (100 миллиардов, 1 раз)"
        await message.answer(
            f"✨ Добро пожаловать!\n\n💰 Баланс\n🏦 Банк\n⚽ Футбол\n🎯 Дартс\n🎁 Бонус\n👤 Профиль\n🏆 Топ\n🔄 Перевести\n✏️ Сменить ник{promo_text}",
            reply_markup=main_keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")

@dp.message(lambda msg: msg.text == "💰 Баланс")
async def show_balance(message: types.Message):
    try:
        user = await get_user(message.from_user.id)
        text = f"💰 Баланс: {user['balance']} ₽\n🏦 В банке: {user['bank']} ₽"
        if message.from_user.id in balance_messages:
            try:
                await balance_messages[message.from_user.id].edit_text(text)
                return
            except:
                pass
        msg = await message.answer(text)
        balance_messages[message.from_user.id] = msg
    except Exception as e:
        logger.error(f"Ошибка в Баланс: {e}")

@dp.message(lambda msg: msg.text == "🏦 Банк")
async def bank_menu(message: types.Message):
    try:
        user = await get_user(message.from_user.id)
        name = user.get('name', 'Игрок')
        percent = get_bank_percent(user['bank_level'])
        upgrade_cost = get_bank_upgrade_cost(user['bank_level'])
        bank_text = f"""👨🏼‍✈️ {name}: /bank

Бот для развлечения 🥃
💵 В банке: {user['bank']} ₽
📊 Процент в час: {percent}%
🏦 Уровень банка: {user['bank_level']}

📥 Пополнить: !банкввод [сумма]
📤 Вывести: !банквывод [сумма]

━━━━━━━━━━━━━━━
📈 Прокачка: {upgrade_cost} ₽"""
        await message.answer(bank_text, parse_mode="Markdown", reply_markup=bank_keyboard)
    except Exception as e:
        logger.error(f"Ошибка в Банк: {e}")

@dp.callback_query(lambda c: c.data == "upgrade_bank")
async def upgrade_bank(callback: types.CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        cost = get_bank_upgrade_cost(user['bank_level'])
        if user['balance'] >= cost:
            await update_user(callback.from_user.id, balance=user['balance'] - cost, bank_level=user['bank_level'] + 1)
            new_percent = get_bank_percent(user['bank_level'] + 1)
            next_cost = get_bank_upgrade_cost(user['bank_level'] + 1)
            await callback.message.answer(f"✅ Банк прокачан!\n📈 Уровень: {user['bank_level'] + 1}\n📊 Процент: {new_percent}%\n💰 Следующая прокачка: {next_cost} ₽")
        else:
            need = cost - user['balance']
            await callback.message.answer(f"❌ Не хватает на прокачку!\n💰 Нужно: {cost} ₽\n💵 У тебя: {user['balance']} ₽\n💸 Не хватает: {need} ₽")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в upgrade_bank: {e}")

@dp.message(lambda msg: msg.text.startswith("!банкввод"))
async def bank_deposit(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Пример: !банкввод 1000")
            return
        amount = int(parts[1])
        if amount < 1:
            await message.answer("❌ Минимум 1 ₽")
            return
        user = await get_user(message.from_user.id)
        if user['balance'] < amount:
            await message.answer(f"❌ Не хватает! У тебя {user['balance']} ₽")
            return
        await update_user(message.from_user.id, balance=user['balance'] - amount, bank=user['bank'] + amount)
        await message.answer(f"✅ +{amount} ₽ в банк!\n💰 На руках: {user['balance'] - amount} ₽\n🏦 В банке: {user['bank'] + amount} ₽")
    except ValueError:
        await message.answer("❌ Введи число!")
    except Exception as e:
        logger.error(f"Ошибка в !банкввод: {e}")

@dp.message(lambda msg: msg.text.startswith("!банквывод"))
async def bank_withdraw(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Пример: !банквывод 1000")
            return
        amount = int(parts[1])
        if amount < 1:
            await message.answer("❌ Минимум 1 ₽")
            return
        user = await get_user(message.from_user.id)
        if user['bank'] < amount:
            await message.answer(f"❌ В банке только {user['bank']} ₽")
            return
        tax = int(amount * 0.04)
        final = amount - tax
        await update_user(message.from_user.id, bank=user['bank'] - amount, balance=user['balance'] + final)
        await message.answer(f"✅ -{amount} ₽ из банка!\n💱 Налог: {tax} ₽ (4%)\n💰 Получено: {final} ₽")
    except ValueError:
        await message.answer("❌ Введи число!")
    except Exception as e:
        logger.error(f"Ошибка в !банквывод: {e}")

@dp.message(lambda msg: msg.text == "🏆 Топ")
async def top_players(message: types.Message):
    try:
        users = await get_all_users()
        real_players = [{"name": u.get('name', f"Игрок{u['user_id']}"), "balance": u.get('balance', 0)} for u in users if u.get('total_bets', 0) > 0 or u.get('balance', 0) > 5000]
        real_players.sort(key=lambda x: x['balance'], reverse=True)
        top_text = "🏆 ТОП ИГРОКОВ 🏆\n\n"
        for i, player in enumerate(real_players[:10], 1):
            top_text += f"{i}. {player['name']} — {player['balance']:,} ₽\n"
        user = await get_user(message.from_user.id)
        position = sum(1 for p in real_players if p['balance'] > user['balance']) + 1
        top_text += f"\n📊 Ваше место в топе: {position}"
        await message.answer(top_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в Топ: {e}")

@dp.message(lambda msg: msg.text == "🔄 Перевести")
async def transfer_menu(message: types.Message):
    try:
        user = await get_user(message.from_user.id)
        max_transfer = get_max_transfer(user.get('limit_level', 1))
        upgrade_cost = get_limit_upgrade_cost(user.get('limit_level', 1))
        await message.answer(
            f"🔄 ПЕРЕВОД ДЕНЕГ\n\n📊 Макс. перевод: {max_transfer} ₽\n🏦 Уровень лимита: {user.get('limit_level', 1)}\n\n📝 перевод @username 1000\n\n📈 Прокачка лимита: {upgrade_cost} ₽",
            reply_markup=limit_keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка в Перевести: {e}")

@dp.callback_query(lambda c: c.data == "upgrade_limit")
async def upgrade_limit(callback: types.CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        cost = get_limit_upgrade_cost(user.get('limit_level', 1))
        if user['balance'] >= cost:
            await update_user(callback.from_user.id, balance=user['balance'] - cost, limit_level=user.get('limit_level', 1) + 1)
            new_max = get_max_transfer(user.get('limit_level', 1) + 1)
            next_cost = get_limit_upgrade_cost(user.get('limit_level', 1) + 1)
            await callback.message.answer(f"✅ Лимит повышен!\n📈 Уровень: {user.get('limit_level', 1) + 1}\n💰 Макс. перевод: {new_max} ₽\n💸 Следующая прокачка: {next_cost} ₽")
        else:
            need = cost - user['balance']
            await callback.message.answer(f"❌ Не хватает на прокачку!\n💰 Нужно: {cost} ₽\n💵 У тебя: {user['balance']} ₽\n💸 Не хватает: {need} ₽")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в upgrade_limit: {e}")

@dp.message(lambda msg: msg.text.startswith("перевод"))
async def transfer_money(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer("❌ Пример: перевод @username 1000")
            return
        target = parts[1].replace("@", "")
        amount = int(parts[2])
        user = await get_user(message.from_user.id)
        max_transfer = get_max_transfer(user.get('limit_level', 1))
        if amount < 1 or amount > max_transfer or amount > user['balance']:
            await message.answer(f"❌ Ошибка суммы!")
            return
        users = await get_all_users()
        target_user = next((u for u in users if u.get('name', '').lower() == target.lower()), None)
        if not target_user or target_user['user_id'] == message.from_user.id:
            await message.answer("❌ Игрок не найден или это вы!")
            return
        await update_user(message.from_user.id, balance=user['balance'] - amount)
        await update_user(target_user['user_id'], balance=target_user['balance'] + amount)
        await message.answer(f"✅ Перевод {amount} ₽ -> {target_user['name']}")
        try:
            await bot.send_message(target_user['user_id'], f"✅ Вам перевели {amount} ₽ от {user['name']}")
        except:
            pass
    except Exception as e:
        logger.error(f"Ошибка в перевод: {e}")

@dp.message(lambda msg: msg.text == "✏️ Сменить ник")
async def change_nick_prompt(message: types.Message):
    await message.answer("✏️ СМЕНА НИКА\n\n/setnik НовыйНик")

@dp.message(Command("setnik"))
async def set_nickname(message: types.Message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("❌ Пример: /setnik Ванёк")
            return
        new_nick = parts[1][:20]
        await update_user(message.from_user.id, name=new_nick)
        await message.answer(f"✅ Ник изменён на {new_nick}!")
    except Exception as e:
        logger.error(f"Ошибка в /setnik: {e}")

@dp.message(lambda msg: msg.text == "РАНДОМ")
async def promo_random(message: types.Message):
    try:
        user = await get_user(message.from_user.id)
        now = time.time()
        if now - user.get('last_promo', 0) < 172800:
            left = int(48 - (now - user.get('last_promo', 0)) // 3600)
            await message.answer(f"⏰ Промокод через {left} часов!")
            return
        amount = random.randint(44444, 122222)
        await update_user(message.from_user.id, balance=user['balance'] + amount, last_promo=int(now))
        await message.answer(f"✅ +{amount} ₽\n💰 Баланс: {user['balance'] + amount:,} ₽")
    except Exception as e:
        logger.error(f"Ошибка в РАНДОМ: {e}")

@dp.message(lambda msg: msg.text == "ПРОМО: ВАНЁК")
async def promo_vanek(message: types.Message):
    try:
        promo = await get_promo('PROMO_VANEK')
        if promo.get('used', False):
            await message.answer("❌ Промокод уже использован!")
            return
        await set_promo_used('PROMO_VANEK')
        user = await get_user(message.from_user.id)
        await update_user(message.from_user.id, balance=user['balance'] + 1000000000000000000000000)
        await message.answer(f"✅ +1 Септиллион ₽!\n👑 Ты первый!")
    except Exception as e:
        logger.error(f"Ошибка в ПРОМО: ВАНЁК: {e}")

@dp.message(lambda msg: msg.text == "Ванёк")
async def promo_vanek_100b(message: types.Message):
    try:
        promo = await get_promo('VANEK_100B')
        if promo.get('used', False):
            await message.answer("❌ Промокод уже использован!")
            return
        await set_promo_used('VANEK_100B')
        user = await get_user(message.from_user.id)
        await update_user(message.from_user.id, balance=user['balance'] + 100000000000)
        await message.answer(f"✅ +100 Миллиардов ₽!\n🔥 Ты успел первым!")
    except Exception as e:
        logger.error(f"Ошибка в Ванёк: {e}")

@dp.message(lambda msg: msg.text == "🎁 Бонус")
async def bonus_8h(message: types.Message):
    try:
        user = await get_user(message.from_user.id)
        now = time.time()
        if now - user.get('last_bonus', 0) < 28800:
            left = int(8 - (now - user.get('last_bonus', 0)) // 3600)
            await message.answer(f"⏰ Бонус через {left} часов!")
            return
        amount = random.randint(2500, 9000)
        await update_user(message.from_user.id, balance=user['balance'] + amount, last_bonus=int(now))
        await message.answer(f"🎁 +{amount} ₽\n💰 Баланс: {user['balance'] + amount} ₽")
    except Exception as e:
        logger.error(f"Ошибка в Бонус: {e}")

@dp.message(lambda msg: msg.text == "⚽ Футбол")
async def football_menu(message: types.Message):
    await message.answer("⚽ ФУТБОЛ\n\n!ф 100\nШанс: 45% | x2.2")

@dp.message(lambda msg: msg.text.startswith("!ф"))
async def football_game(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            return
        bet = int(parts[1])
        user = await get_user(message.from_user.id)
        if bet < 1 or bet > user['balance']:
            await message.answer("❌ Неверная сумма!")
            return
        win = random.random() < 0.45
        await message.answer("⚽ Удар...")
        await asyncio.sleep(1)
        if win:
            win_amount = int(bet * 2.2)
            await update_user(message.from_user.id, balance=user['balance'] + win_amount, total_bets=user['total_bets'] + 1, total_wins=user['total_wins'] + 1)
            await message.answer(f"✅ ГОЛ! +{win_amount} ₽")
        else:
            await update_user(message.from_user.id, balance=user['balance'] - bet, total_bets=user['total_bets'] + 1)
            await message.answer(f"❌ МИМО! -{bet} ₽")
    except Exception as e:
        logger.error(f"Ошибка в !ф: {e}")

@dp.message(lambda msg: msg.text == "🎯 Дартс")
async def darts_menu(message: types.Message):
    await message.answer("🎯 ДАРТС\n\n!д 100\nШанс: 40% | x2.5")

@dp.message(lambda msg: msg.text.startswith("!д"))
async def darts_game(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            return
        bet = int(parts[1])
        user = await get_user(message.from_user.id)
        if bet < 1 or bet > user['balance']:
            await message.answer("❌ Неверная сумма!")
            return
        win = random.random() < 0.40
        await message.answer("🎯 Бросок...")
        await asyncio.sleep(1)
        if win:
            win_amount = int(bet * 2.5)
            await update_user(message.from_user.id, balance=user['balance'] + win_amount, total_bets=user['total_bets'] + 1, total_wins=user['total_wins'] + 1)
            await message.answer(f"✅ ПОПАЛ! +{win_amount} ₽")
        else:
            await update_user(message.from_user.id, balance=user['balance'] - bet, total_bets=user['total_bets'] + 1)
            await message.answer(f"❌ МИМО! -{bet} ₽")
    except Exception as e:
        logger.error(f"Ошибка в !д: {e}")

@dp.message(lambda msg: msg.text == "👤 Профиль")
async def profile(message: types.Message):
    try:
        user = await get_user(message.from_user.id)
        premium = "❌ Нет" if user.get('premium', 0) == 0 else f"✅ {user.get('premium', 0)} 💎"
        users = await get_all_users()
        position = sum(1 for u in users if u.get('balance', 0) > user['balance']) + 1
        profile_text = f"""👤 {user['name']}

👑 Премиум: {premium}
💵 Баланс: {user['balance']:,} ₽
🏦 В банке: {user['bank']:,} ₽
🏆 Место в топе: {position}
🏦 Уровень банка: {user.get('bank_level', 1)}
📊 Лимит: {get_max_transfer(user.get('limit_level', 1))} ₽
🍀 Ставок: {user.get('total_bets', 0)}
🏆 Побед: {user.get('total_wins', 0)}"""
        if message.from_user.id in profile_messages:
            try:
                await profile_messages[message.from_user.id].edit_text(profile_text)
                return
            except:
                pass
        msg = await message.answer(profile_text)
        profile_messages[message.from_user.id] = msg
    except Exception as e:
        logger.error(f"Ошибка в Профиль: {e}")

@dp.callback_query(lambda c: c.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.answer("◀️ Главное меню", reply_markup=main_keyboard)
    await callback.answer()

async def main():
    await init_db()
    logger.info("🤖 Бот запущен!")
    asyncio.create_task(bank_profit_worker())
    asyncio.create_task(personal_bonus_worker())
    asyncio.create_task(cleanup_old_messages())
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"БОТ УПАЛ! Перезапуск через 5 сек... Ошибка: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
