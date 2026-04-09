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
            "yen": 0,
            "bitcoin": 0,
            "bank": 0,
            "bank_deposit": 0,
            "bank_deposit_time": 0,
            "exp": 0,
            "level": 1,
            "rating": 0,
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
            "last_daily": 0,
            "last_business": 0,
            "last_generator": 0,
            "last_farm": 0,
            "last_quarry": 0,
            "last_tree": 0,
            "last_garden": 0,
            "married_to": None,
            "married_id": None,
            "cases": {"common": 0, "rare": 0, "epic": 0, "legendary": 0},
            "potions": {"luck": 0, "exp": 0, "wealth": 0}
        }
        save_users(users)
    return users[user_id]

def save_user(user_id, data):
    users = load_users()
    users[str(user_id)] = data
    save_users(users)

def add_exp(user_id, amount):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        return
    users[uid]["exp"] += amount
    new_level = 1 + users[uid]["exp"] // 500
    if new_level > users[uid]["level"]:
        users[uid]["level"] = new_level
        asyncio.create_task(bot.send_message(user_id, f"🎉 Поздравляем! Вы достигли {new_level} уровня!"))
    save_users(users)

def get_bank_status(bank_amount):
    if bank_amount >= 1000000:
        return "💎 Платиновый", 12, 2
    elif bank_amount >= 100000:
        return "🏆 Золотой", 9, 3
    elif bank_amount >= 10000:
        return "🥈 Серебряный", 7, 4
    else:
        return "📄 Обычный", 6, 5

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏦 Банк"), KeyboardButton(text="🎮 Игры")],
        [KeyboardButton(text="🎭 Развлекательное"), KeyboardButton(text="💒 Браки")],
        [KeyboardButton(text="📦 Кейсы"), KeyboardButton(text="🏆 Топы")],
        [KeyboardButton(text="🗄 Бизнес"), KeyboardButton(text="🏭 Генератор")],
        [KeyboardButton(text="🧰 Майнинг"), KeyboardButton(text="⚠️ Карьер")],
        [KeyboardButton(text="🌳 Дерево"), KeyboardButton(text="🌿 Сады")],
        [KeyboardButton(text="⭐ Профиль"), KeyboardButton(text="🎁 Бонус")],
        [KeyboardButton(text="💢 Сменить ник"), KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True
)

games_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎮 Спин", callback_data="game_spin"), InlineKeyboardButton(text="🎲 Кубик", callback_data="game_dice")],
    [InlineKeyboardButton(text="🏀 Баскетбол", callback_data="game_basketball"), InlineKeyboardButton(text="🎯 Дартс", callback_data="game_dart")],
    [InlineKeyboardButton(text="🎳 Боулинг", callback_data="game_bowling"), InlineKeyboardButton(text="📉 Трейд", callback_data="game_trade")],
    [InlineKeyboardButton(text="🎰 Казино", callback_data="game_casino"), InlineKeyboardButton(text="🎲 Игра в слова", callback_data="game_words")],
    [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
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

@dp.message(lambda msg: msg.text == "❓ Помощь")
async def help_command(message: types.Message):
    help_text = """
📖 *ПОМОЩЬ ПО ИГРЕ* 📖

🎮 *ИГРЫ*
• Спин [ставка] — игровой автомат (x2-x10)
• Кубик [число] [ставка] — угадай число 1-6 (x5)
• Баскетбол [ставка] — шанс 50% (x2)
• Дартс [ставка] — шанс 33% (x3)
• Боулинг [ставка] — страйк x3, спэр x2
• Трейд [вверх/вниз] [ставка] — биржевая игра
• Казино [ставка] — шанс 48% (x2)
• Игра в слова — пиши слово по буквам

🎭 *РАЗВЛЕКАТЕЛЬНОЕ*
• Шар [фраза] — магический шар предскажет
• Выбери [A] или [B] — я выберу за тебя
• Инфа [тема] — получу информацию
• Испытать удачу — проверь свою удачу

💒 *БРАКИ*
• /marry @username — жениться
• /divorce — развестись
• /marriage — показать свой брак

📦 *КЕЙСЫ*
• Кейсы — список доступных кейсов
• Купить кейс [номер] [кол-во] — купить кейсы
• Открыть кейс [номер] [кол-во] — открыть кейсы

🏢 *БИЗНЕС*
• Бизнес — информация
• Построить бизнес (50к) — построить бизнес
• Мой бизнес — посмотреть свой бизнес

🏭 *ГЕНЕРАТОР*
• Генератор — информация
• Построить генератор (100к) — построить генератор
• Мой генератор — посмотреть генератор

🧰 *МАЙНИНГ*
• Майнинг — информация
• Построить ферму (30к) — построить ферму
• Моя ферма — посмотреть ферму

⚠️ *КАРЬЕР*
• Карьер — информация
• Построить карьер (80к) — построить карьер
• Мой карьер — посмотреть карьер

🌳 *ДЕРЕВО*
• Дерево — информация
• Построить участок (20к) — посадить дерево
• Моё дерево — посмотреть дерево

🌿 *САДЫ*
• Сады — информация
• Построить сад (40к) — построить сад
• Мой сад — посмотреть сад
• Сад полить — полить сад (+100-500₽)
• Зелья — посмотреть зелья
• Создать зелье [номер] — создать зелье

🏦 *БАНК*
• Банк — посмотреть счёт
• Банк положить [сумма] — положить деньги
• Банк снять [сумма] — снять деньги
• Банк депозит [сумма] — открыть депозит на 3 дня

⭐ *ПРОФИЛЬ*
• Профиль — вся информация о тебе
• /setnick [ник] — сменить ник
• /nick — узнать свой ник

🎁 *БОНУСЫ*
• Бонус — ежедневный бонус
• Топы — топы игроков

📌 *Примеры команд:*
• Спин 500
• Кубик 3 500
• Баскетбол 300
• Трейд вверх 1000
• /marry @Анна
• Купить кейс 1 5
• Создать зелье 1
    """
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("start"))
async def start(message: types.Message):
    init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "✨ *Добро пожаловать в Retro 19?* ✨\n\n"
        "🎮 *Экономическая игра с уклоном в удачу!*\n\n"
        "📌 *Что тебя ждёт:*\n"
        "• 🏦 Банк с депозитами и статусами\n"
        "• 🎮 7 азартных игр\n"
        "• 💒 Браки с другими игроками\n"
        "• 📦 Кейсы с редкими предметами\n"
        "• 🏢 Бизнес, генератор, ферма, карьер\n"
        "• 🌳 Денежное дерево и сады\n"
        "• 🎁 Ежедневные бонусы\n"
        "• 🏆 Топы игроков\n\n"
        "👇 *Нажми ❓ Помощь для списка команд!* 👇",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )

@dp.message(lambda msg: msg.text == "🏆 Топы")
async def tops_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Топ денег", callback_data="top_money"), InlineKeyboardButton(text="⭐ Топ опыта", callback_data="top_exp")],
        [InlineKeyboardButton(text="💴 Топ йен", callback_data="top_yen"), InlineKeyboardButton(text="₿ Топ биткоинов", callback_data="top_bitcoin")],
        [InlineKeyboardButton(text="🏆 Топ рейтинга", callback_data="top_rating"), InlineKeyboardButton(text="📦 Топ кейсов", callback_data="top_cases")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
    ])
    await message.answer("🏆 *Выбери топ который хочешь открыть:* 🏆", parse_mode="Markdown", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("top_"))
async def show_top(callback: types.CallbackQuery):
    top_type = callback.data.replace("top_", "")
    users = load_users()
    
    if top_type == "money":
        sorted_users = sorted(users.values(), key=lambda x: x['balance'] + x.get('bank', 0), reverse=True)[:15]
        title = "💰 ТОП ДЕНЕГ 💰"
        value_key = lambda u: u['balance'] + u.get('bank', 0)
        value_format = lambda v: f"{v:,} ₽"
    elif top_type == "exp":
        sorted_users = sorted(users.values(), key=lambda x: x['exp'], reverse=True)[:15]
        title = "⭐ ТОП ОПЫТА ⭐"
        value_key = lambda u: u['exp']
        value_format = lambda v: f"{v} опыта"
    elif top_type == "yen":
        sorted_users = sorted(users.values(), key=lambda x: x.get('yen', 0), reverse=True)[:15]
        title = "💴 ТОП ЙЕН 💴"
        value_key = lambda u: u.get('yen', 0)
        value_format = lambda v: f"{v:,} ¥"
    elif top_type == "bitcoin":
        sorted_users = sorted(users.values(), key=lambda x: x.get('bitcoin', 0), reverse=True)[:15]
        title = "₿ ТОП БИТКОИНОВ ₿"
        value_key = lambda u: u.get('bitcoin', 0)
        value_format = lambda v: f"{v:.8f} BTC"
    elif top_type == "rating":
        sorted_users = sorted(users.values(), key=lambda x: x.get('rating', 0), reverse=True)[:15]
        title = "🏆 ТОП РЕЙТИНГА 🏆"
        value_key = lambda u: u.get('rating', 0)
        value_format = lambda v: f"{v} ⭐"
    elif top_type == "cases":
        sorted_users = sorted(users.values(), key=lambda x: sum(x.get('cases', {}).values()), reverse=True)[:15]
        title = "📦 ТОП КЕЙСОВ 📦"
        value_key = lambda u: sum(u.get('cases', {}).values())
        value_format = lambda v: f"{v} кейсов"
    else:
        await callback.answer()
        return
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    text = f"{title}\n\n"
    for i, u in enumerate(sorted_users[:15]):
        medal = medals[i] if i < len(medals) else f"{i+1}️⃣"
        value = value_key(u)
        text += f"{medal} {u['name']} — {value_format(value)}\n"
    
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.message(lambda msg: msg.text == "🎭 Развлекательное")
async def fun_menu(message: types.Message):
    await message.answer(
        "🎭 *РАЗВЛЕКАТЕЛЬНЫЕ КОМАНДЫ* 🎭\n\n"
        "🔮 *Шар [фраза]* — магический шар предскажет будущее\n"
        "   📌 Пример: Шар Я буду богатым?\n\n"
        "💬 *Выбери [A] или [B]* — я выберу за тебя\n"
        "   📌 Пример: Выбери пицца или суши\n\n"
        "📊 *Инфа [тема]* — получу информацию\n"
        "   📌 Пример: Инфа Погода\n\n"
        "🍀 *Испытать удачу* — проверишь свою удачу\n\n"
        "👇 *Напиши команду прямо в чат!* 👇",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text.startswith("Шар"))
async def magic_ball(message: types.Message):
    question = message.text.replace("Шар", "").strip()
    if not question:
        await message.answer("❓ *Задай вопрос!*\n📌 Пример: Шар Я буду богатым?", parse_mode="Markdown")
        return
    answers = [
        "🔮 Да, определённо!", "🔮 Нет", "🔮 Скорее да, чем нет",
        "🔮 Спроси позже", "🔮 Не могу сказать сейчас", "🔮 Да!",
        "🔮 Шансы высоки", "🔮 Лучше не рисковать", "🔮 Абсолютно точно",
        "🔮 Мой ответ — нет", "🔮 Возможно", "🔮 Вероятность низкая",
        "🔮 Звёзды говорят — да", "🔮 Сомневаюсь", "🔮 Определённо да"
    ]
    await message.answer(f"{random.choice(answers)}\n\n❓ *Вопрос:* {question}", parse_mode="Markdown")

@dp.message(lambda msg: msg.text.startswith("Выбери"))
async def choose_command(message: types.Message):
    text = message.text.replace("Выбери", "").strip()
    if " или " not in text:
        await message.answer("❌ *Напиши:* Выбери вариант1 или вариант2\n📌 Пример: Выбери пицца или суши", parse_mode="Markdown")
        return
    parts = text.split(" или ")
    option1 = parts[0].strip()
    option2 = parts[1].strip()
    choice = random.choice([option1, option2])
    await message.answer(f"💬 *Я выбираю:* **{choice}**!\n\n📌 *Варианты:* {option1} или {option2}", parse_mode="Markdown")

@dp.message(lambda msg: msg.text.startswith("Инфа"))
async def info_command(message: types.Message):
    topic = message.text.replace("Инфа", "").strip()
    if not topic:
        await message.answer("📊 *О чём узнать?*\n📌 Пример: Инфа Погода", parse_mode="Markdown")
        return
    
    facts = {
        "погода": "☀️ *Погода:* Солнечно, +25°C, без осадков",
        "новости": "📰 *Новости:* Бот Retro 19? набирает популярность!",
        "бот": "🤖 *О боте:* Я экономический бот с играми, бизнесом и браками!",
        "игры": "🎮 *Игры:* У меня 7 игр: Спин, Кубик, Баскетбол, Дартс, Боулинг, Трейд, Казино",
        "бизнес": "🏢 *Бизнес:* Приносит 500 ₽/час. Стоимость: 50,000 ₽",
        "ферма": "🔋 *Ферма:* Приносит 300 ₽/30 мин. Стоимость: 30,000 ₽"
    }
    
    found = False
    for key, fact in facts.items():
        if key in topic.lower():
            await message.answer(fact, parse_mode="Markdown")
            found = True
            break
    
    if not found:
        await message.answer(f"📊 *Информация по теме '{topic}':*\n\nСкоро появится! Следите за обновлениями.", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🍀 Испытать удачу")
async def test_luck(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    luck = random.randint(1, 100)
    
    if luck <= 5:
        win = 10000
        user['balance'] += win
        await message.answer(f"🍀 *НЕВЕРОЯТНАЯ УДАЧА!* 🍀\n\n✨ Ты выиграл {win} ₽! ✨\n\n🎉 Это 5% везения!", parse_mode="Markdown")
    elif luck <= 20:
        win = 2000
        user['balance'] += win
        await message.answer(f"🍀 *БОЛЬШАЯ УДАЧА!* 🍀\n\n💰 +{win} ₽", parse_mode="Markdown")
    elif luck <= 45:
        win = 500
        user['balance'] += win
        await message.answer(f"🍀 *ХОРОШАЯ УДАЧА!* 🍀\n\n💰 +{win} ₽", parse_mode="Markdown")
    elif luck <= 70:
        await message.answer(f"🍀 *ТАК СЕБЕ* 🍀\n\n😐 Ты ничего не выиграл", parse_mode="Markdown")
    else:
        lose = random.randint(200, 1000)
        user['balance'] = max(0, user['balance'] - lose)
        await message.answer(f"🍀 *НЕ ПОВЕЗЛО* 🍀\n\n💔 Ты проиграл {lose} ₽", parse_mode="Markdown")
    
    save_user(message.from_user.id, user)
    add_exp(message.from_user.id, 5)

@dp.message(lambda msg: msg.text == "💢 Сменить ник")
async def change_nick_prompt(message: types.Message):
    await message.answer("💢 *СМЕНА НИКА* 💢\n\n📌 *Команда:* `/setnick НовыйНик`\n📌 *Пример:* `/setnick Алекс`\n\n⚠️ Ник не должен содержать оскорблений!", parse_mode="Markdown")

@dp.message(Command("setnick"))
async def set_nickname(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ *Используй:* `/setnick НовыйНик`\n📌 *Пример:* `/setnick Алекс`", parse_mode="Markdown")
        return
    new_nick = parts[1][:20]
    user = init_user(message.from_user.id, message.from_user.username)
    old_nick = user['name']
    user['name'] = new_nick
    save_user(message.from_user.id, user)
    await message.answer(f"✅ *Ник изменён!*\n\n👤 *Старый:* {old_nick}\n👤 *Новый:* {new_nick}", parse_mode="Markdown")

@dp.message(Command("nick"))
async def show_nick(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(f"👤 *Твой ник:* {user['name']}", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "⭐ Профиль")
async def profile(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    status, dp_percent, tax_percent = get_bank_status(user.get("bank", 0))
    total_cases = sum(user.get('cases', {}).values())
    await message.answer(
        f"👤 *ПРОФИЛЬ* 👤\n\n"
        f"📛 *Ник:* {user['name']}\n"
        f"💰 *Деньги:* {user['balance']:,} ₽\n"
        f"💴 *Йены:* {user.get('yen', 0):,} ¥\n"
        f"₿ *Биткоины:* {user.get('bitcoin', 0):.8f} BTC\n"
        f"🏦 *Банк:* {user.get('bank', 0):,} ₽\n"
        f"💎 *Статус банка:* {status}\n"
        f"⭐ *Опыт:* {user['exp']}\n"
        f"🎚️ *Уровень:* {user['level']}\n"
        f"🏆 *Рейтинг:* {user.get('rating', 0)}\n"
        f"📦 *Кейсов открыто:* {total_cases}\n"
        f"💒 *Брак:* {user.get('married_to') or '❌ Нет'}\n\n"
        f"🏢 *Бизнес:* {user.get('business') or '❌ Нет'} (ур. {user.get('business_level', 1)})\n"
        f"🏭 *Генератор:* {user.get('generator') or '❌ Нет'} (ур. {user.get('generator_level', 1)})\n"
        f"🔋 *Ферма:* {user.get('farm') or '❌ Нет'} (ур. {user.get('farm_level', 1)})\n"
        f"⚠️ *Карьер:* {user.get('quarry') or '❌ Нет'} (ур. {user.get('quarry_level', 1)})\n"
        f"🌳 *Дерево:* {user.get('tree') or '❌ Нет'} (ур. {user.get('tree_level', 1)})\n"
        f"🌿 *Сад:* {user.get('garden') or '❌ Нет'} (ур. {user.get('garden_level', 1)})",
        parse_mode="Markdown"
    )

@dp.message(Command("balance"))
async def show_balance(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"💰 *БАЛАНС* 💰\n\n"
        f"👤 *Ник:* {user['name']}\n"
        f"💰 *Деньги:* {user['balance']:,} ₽\n"
        f"💴 *Йены:* {user.get('yen', 0):,} ¥\n"
        f"₿ *Биткоины:* {user.get('bitcoin', 0):.8f} BTC\n"
        f"🏦 *Банк:* {user.get('bank', 0):,} ₽",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🎁 Бонус")
async def daily_bonus(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    if now - user.get('last_daily', 0) < 86400:
        left = int(86400 - (now - user.get('last_daily', 0)))
        await message.answer(f"⏳ *Бонус уже получен!*\n\nСледующий через {left // 3600} часов.", parse_mode="Markdown")
        return
    bonus = random.randint(500, 2000)
    user['balance'] += bonus
    user['last_daily'] = now
    save_user(message.from_user.id, user)
    await message.answer(f"🎁 *ЕЖЕДНЕВНЫЙ БОНУС!* 🎁\n\n💰 +{bonus} ₽\n\nЗаходи завтра снова!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🏦 Банк")
async def bank_account(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    status, deposit_percent, tax_percent = get_bank_status(user.get("bank", 0))
    
    deposit_text = "Нет"
    withdraw_text = "—"
    if user.get("bank_deposit", 0) > 0:
        deposit_time = user.get("bank_deposit_time", 0)
        now = datetime.now().timestamp()
        days_passed = (now - deposit_time) / 86400
        if days_passed >= 3:
            withdraw_text = "✅ ГОТОВО к снятию!"
        else:
            left = int(3 - days_passed)
            withdraw_text = f"⏳ через {left} дн."
        deposit_text = f"{user['bank_deposit']:,} ₽"
    
    await message.answer(
        f"🏦 *Retro 19?, ваш банковский счёт:* 🏦\n\n"
        f"👫 *Владелец:* {user['name']}\n"
        f"💰 *Деньги в банке:* {user.get('bank', 0):,} ₽\n"
        f"💎 *Статус:* {status}\n\n"
        f"〽 *Процент под депозит:* {deposit_percent}%\n"
        f"💱 *Налог на снятие:* {tax_percent}%\n\n"
        f"💵 *Под депозитом:* {deposit_text}\n"
        f"⏳ *Можно снять:* {withdraw_text}\n\n"
        f"📌 *Команды:*\n"
        f"• Банк положить [сумма]\n"
        f"• Банк снять [сумма]\n"
        f"• Банк депозит [сумма] (на 3 дня)\n"
        f"• Банк снять депозит",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text.startswith("Банк положить"))
async def bank_deposit(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ *Пример:* Банк положить 5000", parse_mode="Markdown")
        return
    try:
        amount = int(parts[2])
    except:
        await message.answer("❌ *Сумма должна быть числом!*", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    if user['balance'] < amount:
        await message.answer(f"❌ *Не хватает!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= amount
    user['bank'] = user.get('bank', 0) + amount
    save_user(message.from_user.id, user)
    await message.answer(f"💰 *Ты положил {amount:,} ₽ в банк!*\n\n🏦 *В банке:* {user['bank']:,} ₽", parse_mode="Markdown")

@dp.message(lambda msg: msg.text.startswith("Банк снять"))
async def bank_withdraw(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ *Пример:* Банк снять 5000", parse_mode="Markdown")
        return
    try:
        amount = int(parts[2])
    except:
        await message.answer("❌ *Сумма должна быть числом!*", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('bank', 0) < amount:
        await message.answer(f"❌ *В банке только {user.get('bank', 0):,} ₽*", parse_mode="Markdown")
        return
    status, deposit_percent, tax_percent = get_bank_status(user.get('bank', 0))
    tax = int(amount * tax_percent / 100)
    after_tax = amount - tax
    user['bank'] -= amount
    user['balance'] += after_tax
    save_user(message.from_user.id, user)
    await message.answer(
        f"💰 *Ты снял {amount:,} ₽ из банка*\n\n"
        f"💱 *Налог ({tax_percent}%):* -{tax:,} ₽\n"
        f"✅ *Получено:* {after_tax:,} ₽",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text.startswith("Банк депозит"))
async def bank_deposit_start(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ *Пример:* Банк депозит 10000", parse_mode="Markdown")
        return
    try:
        amount = int(parts[2])
    except:
        await message.answer("❌ *Сумма должна быть числом!*", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('bank_deposit', 0) > 0:
        await message.answer("❌ *У тебя уже есть активный депозит!*\nСначала сними его: `Банк снять депозит`", parse_mode="Markdown")
        return
    if user['balance'] < amount:
        await message.answer(f"❌ *Не хватает!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= amount
    user['bank_deposit'] = amount
    user['bank_deposit_time'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    status, deposit_percent, tax_percent = get_bank_status(user.get('bank', 0))
    await message.answer(
        f"💵 *Депозит открыт!* 💵\n\n"
        f"💰 *Сумма:* {amount:,} ₽\n"
        f"📈 *Процент:* {deposit_percent}%\n"
        f"⏳ *Срок:* 3 дня\n"
        f"💰 *Через 3 дня ты получишь:* {amount + int(amount * deposit_percent / 100):,} ₽\n\n"
        f"📌 Чтобы снять: `Банк снять депозит`",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "Банк снять депозит")
async def bank_withdraw_deposit(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    deposit = user.get('bank_deposit', 0)
    if deposit == 0:
        await message.answer("❌ *У тебя нет активного депозита!*", parse_mode="Markdown")
        return
    deposit_time = user.get('bank_deposit_time', 0)
    now = datetime.now().timestamp()
    days_passed = (now - deposit_time) / 86400
    if days_passed < 3:
        left = int(3 - days_passed)
        await message.answer(f"⏳ *Депозит можно снять через {left} дн.*", parse_mode="Markdown")
        return
    status, deposit_percent, tax_percent = get_bank_status(user.get('bank', 0))
    profit = int(deposit * deposit_percent / 100)
    total = deposit + profit
    user['balance'] += total
    user['bank_deposit'] = 0
    user['bank_deposit_time'] = 0
    save_user(message.from_user.id, user)
    await message.answer(
        f"💵 *Депозит снят!* 💵\n\n"
        f"💰 *Сумма вклада:* {deposit:,} ₽\n"
        f"📈 *Проценты:* +{profit:,} ₽\n"
        f"✅ *Итого:* {total:,} ₽",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🗄 Бизнес")
async def business_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    
    if user.get('business') and now - user.get('last_business', 0) >= 3600:
        income = 500 * user.get('business_level', 1)
        user['balance'] += income
        user['last_business'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"🏢 *Бизнес принёс доход!*\n💰 +{income} ₽", parse_mode="Markdown")
    
    await message.answer(
        "🏢 *БИЗНЕС* 🏢\n\n"
        "💰 *Мой бизнес* — посмотреть свой бизнес\n"
        "🏗 *Построить бизнес* — открыть бизнес (50,000 ₽)\n"
        "💸 *Продать бизнес* — продать бизнес (временно недоступно)\n\n"
        "📌 *Доход:* 500 ₽/час (можно улучшать!)\n"
        "📌 *Улучшение:* повышает доход на +500 ₽/час",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "💰 Мой бизнес")
async def my_business(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('business'):
        income = 500 * user.get('business_level', 1)
        await message.answer(
            f"🏢 *ТВОЙ БИЗНЕС* 🏢\n\n"
            f"📛 *Название:* {user['business']}\n"
            f"📈 *Уровень:* {user.get('business_level', 1)}\n"
            f"💰 *Доход:* {income} ₽/час\n\n"
            f"📌 Чтобы улучшить бизнес, нужно развивать его!",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ *У тебя нет бизнеса!*\nПострой его: `Построить бизнес`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🏗 Построить бизнес")
async def build_business(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('business'):
        await message.answer("❌ *У тебя уже есть бизнес!*", parse_mode="Markdown")
        return
    if user['balance'] < 50000:
        await message.answer(f"❌ *Не хватает!* Нужно 50,000 ₽, у тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= 50000
    user['business'] = "Магазин"
    user['last_business'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("🏢 *Ты построил бизнес!* 🏢\n\n💰 Теперь ты получаешь 500 ₽ каждый час!\n📌 Чтобы улучшить бизнес, развивай его!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🏭 Генератор")
async def generator_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    
    if user.get('generator') and now - user.get('last_generator', 0) >= 7200:
        income = 300 * user.get('generator_level', 1)
        user['balance'] += income
        user['last_generator'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"🏭 *Генератор произвёл энергию!*\n💰 +{income} ₽", parse_mode="Markdown")
    
    await message.answer(
        "🏭 *ГЕНЕРАТОР* 🏭\n\n"
        "🏭 *Мой генератор* — посмотреть генератор\n"
        "🏗 *Построить генератор* — построить генератор (100,000 ₽)\n"
        "💷 *Продать генератор* — продать (временно недоступно)\n\n"
        "📌 *Доход:* 300 ₽/2 часа (можно улучшать!)\n"
        "📌 *Улучшение:* повышает доход на +300 ₽/2 часа",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🏭 Мой генератор")
async def my_generator(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('generator'):
        income = 300 * user.get('generator_level', 1)
        await message.answer(
            f"🏭 *ТВОЙ ГЕНЕРАТОР* 🏭\n\n"
            f"📛 *Название:* {user['generator']}\n"
            f"📈 *Уровень:* {user.get('generator_level', 1)}\n"
            f"💰 *Доход:* {income} ₽/2 часа",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ *У тебя нет генератора!*\nПострой его: `Построить генератор`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🏗 Построить генератор")
async def build_generator(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('generator'):
        await message.answer("❌ *У тебя уже есть генератор!*", parse_mode="Markdown")
        return
    if user['balance'] < 100000:
        await message.answer(f"❌ *Не хватает!* Нужно 100,000 ₽, у тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= 100000
    user['generator'] = "Солнечный генератор"
    user['last_generator'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("🏭 *Ты построил генератор!* 🏭\n\n💰 Теперь ты получаешь 300 ₽ каждые 2 часа!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🧰 Майнинг")
async def mining_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    
    if user.get('farm') and now - user.get('last_farm', 0) >= 1800:
        income = 300 * user.get('farm_level', 1)
        user['balance'] += income
        user['last_farm'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"🔋 *Ферма намайнила монеты!*\n💰 +{income} ₽", parse_mode="Markdown")
    
    await message.answer(
        "🔋 *МАЙНИНГ ФЕРМА* 🔋\n\n"
        "🔋 *Моя ферма* — посмотреть ферму\n"
        "🏗 *Построить ферму* — построить ферму (30,000 ₽)\n"
        "💰 *Продать ферму* — продать (временно недоступно)\n\n"
        "📌 *Доход:* 300 ₽/30 мин (можно улучшать!)",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🔋 Моя ферма")
async def my_farm(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('farm'):
        income = 300 * user.get('farm_level', 1)
        await message.answer(
            f"🔋 *ТВОЯ ФЕРМА* 🔋\n\n"
            f"📛 *Название:* {user['farm']}\n"
            f"📈 *Уровень:* {user.get('farm_level', 1)}\n"
            f"💰 *Доход:* {income} ₽/30 мин",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ *У тебя нет фермы!*\nПострой её: `Построить ферму`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🏗 Построить ферму")
async def build_farm(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('farm'):
        await message.answer("❌ *У тебя уже есть ферма!*", parse_mode="Markdown")
        return
    if user['balance'] < 30000:
        await message.answer(f"❌ *Не хватает!* Нужно 30,000 ₽, у тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= 30000
    user['farm'] = "Майнинг ферма"
    user['last_farm'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("🔋 *Ты построил майнинг ферму!* 🔋\n\n💰 Теперь ты получаешь 300 ₽ каждые 30 минут!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "⚠️ Карьер")
async def quarry_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    
    if user.get('quarry') and now - user.get('last_quarry', 0) >= 5400:
        income = 500 * user.get('quarry_level', 1)
        user['balance'] += income
        user['last_quarry'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"⚠️ *Карьер добыл ресурсы!*\n💰 +{income} ₽", parse_mode="Markdown")
    
    await message.answer(
        "⚠️ *КАРЬЕР* ⚠️\n\n"
        "⚠️ *Мой карьер* — посмотреть карьер\n"
        "🏗 *Построить карьер* — построить карьер (80,000 ₽)\n"
        "💰 *Продать карьер* — продать (временно недоступно)\n\n"
        "📌 *Доход:* 500 ₽/1.5 часа (можно улучшать!)",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "⚠️ Мой карьер")
async def my_quarry(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('quarry'):
        income = 500 * user.get('quarry_level', 1)
        await message.answer(
            f"⚠️ *ТВОЙ КАРЬЕР* ⚠️\n\n"
            f"📛 *Название:* {user['quarry']}\n"
            f"📈 *Уровень:* {user.get('quarry_level', 1)}\n"
            f"💰 *Доход:* {income} ₽/1.5 часа",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ *У тебя нет карьера!*\nПострой его: `Построить карьер`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🏗 Построить карьер")
async def build_quarry(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('quarry'):
        await message.answer("❌ *У тебя уже есть карьер!*", parse_mode="Markdown")
        return
    if user['balance'] < 80000:
        await message.answer(f"❌ *Не хватает!* Нужно 80,000 ₽, у тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= 80000
    user['quarry'] = "Каменный карьер"
    user['last_quarry'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("⚠️ *Ты построил карьер!* ⚠️\n\n💰 Теперь ты получаешь 500 ₽ каждые 1.5 часа!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🌳 Дерево")
async def tree_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    
    if user.get('tree') and now - user.get('last_tree', 0) >= 86400:
        income = 200 * user.get('tree_level', 1)
        user['balance'] += income
        user['last_tree'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"🌳 *Денежное дерево принесло плоды!*\n💰 +{income} ₽", parse_mode="Markdown")
    
    await message.answer(
        "🌳 *ДЕНЕЖНОЕ ДЕРЕВО* 🌳\n\n"
        "🌳 *Денежное дерево* — информация\n"
        "🌳 *Моё дерево* — посмотреть дерево\n"
        "🏗 *Построить участок* — посадить дерево (20,000 ₽)\n"
        "💰 *Продать участок* — продать (временно недоступно)\n\n"
        "📌 *Доход:* 200 ₽/день (можно улучшать!)",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🌳 Моё дерево")
async def my_tree(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('tree'):
        income = 200 * user.get('tree_level', 1)
        await message.answer(
            f"🌳 *ТВОЁ ДЕРЕВО* 🌳\n\n"
            f"📛 *Название:* {user['tree']}\n"
            f"📈 *Уровень:* {user.get('tree_level', 1)}\n"
            f"💰 *Доход:* {income} ₽/день",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ *У тебя нет дерева!*\nПосади его: `Построить участок`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🏗 Построить участок")
async def build_tree(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('tree'):
        await message.answer("❌ *У тебя уже есть дерево!*", parse_mode="Markdown")
        return
    if user['balance'] < 20000:
        await message.answer(f"❌ *Не хватает!* Нужно 20,000 ₽, у тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= 20000
    user['tree'] = "Денежное дерево"
    user['last_tree'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("🌳 *Ты посадил денежное дерево!* 🌳\n\n💰 Теперь ты получаешь 200 ₽ каждый день!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🌿 Сады")
async def garden_menu(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    now = datetime.now().timestamp()
    
    if user.get('garden') and now - user.get('last_garden', 0) >= 21600:
        income = 400 * user.get('garden_level', 1)
        user['balance'] += income
        user['last_garden'] = now
        save_user(message.from_user.id, user)
        await message.answer(f"🌿 *Сад принёс урожай!*\n💰 +{income} ₽", parse_mode="Markdown")
    
    await message.answer(
        "🌿 *САДЫ* 🌿\n\n"
        "🪧 *Мой сад* — посмотреть сад\n"
        "🏗 *Построить сад* — построить сад (40,000 ₽)\n"
        "💰 *Продать сад* — продать (временно недоступно)\n"
        "💦 *Сад полить* — полить сад (+100-500 ₽)\n"
        "🍸 *Зелья* — посмотреть зелья\n"
        "🔮 *Создать зелье [номер]* — создать зелье\n\n"
        "📌 *Доход:* 400 ₽/6 часов (можно улучшать!)\n"
        "📌 *Полив:* каждые 3 часа даёт бонус",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🪧 Мой сад")
async def my_garden(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('garden'):
        income = 400 * user.get('garden_level', 1)
        await message.answer(
            f"🌿 *ТВОЙ САД* 🌿\n\n"
            f"📛 *Название:* {user['garden']}\n"
            f"📈 *Уровень:* {user.get('garden_level', 1)}\n"
            f"💰 *Доход:* {income} ₽/6 часов",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ *У тебя нет сада!*\nПострой его: `Построить сад`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🏗 Построить сад")
async def build_garden(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('garden'):
        await message.answer("❌ *У тебя уже есть сад!*", parse_mode="Markdown")
        return
    if user['balance'] < 40000:
        await message.answer(f"❌ *Не хватает!* Нужно 40,000 ₽, у тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    user['balance'] -= 40000
    user['garden'] = "Волшебный сад"
    user['last_garden'] = datetime.now().timestamp()
    save_user(message.from_user.id, user)
    await message.answer("🌿 *Ты построил сад!* 🌿\n\n💰 Теперь ты получаешь 400 ₽ каждые 6 часов!", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "💦 Сад полить")
async def water_garden(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('garden'):
        await message.answer("❌ *У тебя нет сада!* Сначала построй его.", parse_mode="Markdown")
        return
    now = datetime.now().timestamp()
    if now - user.get('last_water', 0) < 10800:
        left = int(10800 - (now - user.get('last_water', 0)))
        await message.answer(f"⏳ *Сад уже полит!*\nПолить можно через {left // 60} минут.", parse_mode="Markdown")
        return
    user['last_water'] = now
    bonus = random.randint(100, 500)
    user['balance'] += bonus
    save_user(message.from_user.id, user)
    await message.answer(f"💦 *Ты полил сад!* 🌿\n\n💰 Урожай вырос! +{bonus} ₽", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "🍸 Зелья")
async def potions_list(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    potions = user.get('potions', {})
    await message.answer(
        f"🍸 *ТВОИ ЗЕЛЬЯ* 🍸\n\n"
        f"🍀 *Зелье удачи:* {potions.get('luck', 0)} шт. (+500 ₽)\n"
        f"📈 *Зелье опыта:* {potions.get('exp', 0)} шт. (+100 опыта)\n"
        f"💰 *Зелье богатства:* {potions.get('wealth', 0)} шт. (+1000 ₽)\n\n"
        f"📌 *Создать зелье:*\n"
        f"• `Создать зелье 1` — Зелье удачи (200 ₽)\n"
        f"• `Создать зелье 2` — Зелье опыта (150 ₽)\n"
        f"• `Создать зелье 3` — Зелье богатства (500 ₽)\n\n"
        f"📌 *Использовать зелье:*\n"
        f"• `Использовать зелье 1` — выпить зелье удачи\n"
        f"• `Использовать зелье 2` — выпить зелье опыта\n"
        f"• `Использовать зелье 3` — выпить зелье богатства",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text.startswith("Создать зелье"))
async def create_potion(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ *Пример:* `Создать зелье 1`\n\n1 — Зелье удачи (200 ₽)\n2 — Зелье опыта (150 ₽)\n3 — Зелье богатства (500 ₽)", parse_mode="Markdown")
        return
    try:
        potion_num = int(parts[2])
    except:
        await message.answer("❌ *Введи номер зелья:* 1, 2 или 3", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    
    if potion_num == 1:
        if user['balance'] < 200:
            await message.answer(f"❌ *Не хватает!* Нужно 200 ₽, у тебя {user['balance']:,} ₽", parse_mode="Markdown")
            return
        user['balance'] -= 200
        user['potions']['luck'] = user['potions'].get('luck', 0) + 1
        await message.answer("🍀 *Ты создал Зелье удачи!* 🍀\n\nИспользуй: `Использовать зелье 1`", parse_mode="Markdown")
    elif potion_num == 2:
        if user['balance'] < 150:
            await message.answer(f"❌ *Не хватает!* Нужно 150 ₽, у тебя {user['balance']:,} ₽", parse_mode="Markdown")
            return
        user['balance'] -= 150
        user['potions']['exp'] = user['potions'].get('exp', 0) + 1
        await message.answer("📈 *Ты создал Зелье опыта!* 📈\n\nИспользуй: `Использовать зелье 2`", parse_mode="Markdown")
    elif potion_num == 3:
        if user['balance'] < 500:
            await message.answer(f"❌ *Не хватает!* Нужно 500 ₽, у тебя {user['balance']:,} ₽", parse_mode="Markdown")
            return
        user['balance'] -= 500
        user['potions']['wealth'] = user['potions'].get('wealth', 0) + 1
        await message.answer("💰 *Ты создал Зелье богатства!* 💰\n\nИспользуй: `Использовать зелье 3`", parse_mode="Markdown")
    else:
        await message.answer("❌ *Номера зелий:* 1, 2 или 3", parse_mode="Markdown")
        return
    
    save_user(message.from_user.id, user)

@dp.message(lambda msg: msg.text.startswith("Использовать зелье"))
async def use_potion(message: types.Message):
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ *Пример:* `Использовать зелье 1`\n\n1 — Зелье удачи (+500 ₽)\n2 — Зелье опыта (+100 опыта)\n3 — Зелье богатства (+1000 ₽)", parse_mode="Markdown")
        return
    try:
        potion_num = int(parts[2])
    except:
        await message.answer("❌ *Введи номер зелья:* 1, 2 или 3", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    potions = user.get('potions', {})
    
    if potion_num == 1:
        if potions.get('luck', 0) == 0:
            await message.answer("❌ *У тебя нет Зелья удачи!*\nСначала создай его: `Создать зелье 1`", parse_mode="Markdown")
            return
        user['potions']['luck'] -= 1
        user['balance'] += 500
        await message.answer("🍀 *Ты выпил Зелье удачи!* 🍀\n\n💰 +500 ₽", parse_mode="Markdown")
    elif potion_num == 2:
        if potions.get('exp', 0) == 0:
            await message.answer("❌ *У тебя нет Зелья опыта!*\nСначала создай его: `Создать зелье 2`", parse_mode="Markdown")
            return
        user['potions']['exp'] -= 1
        add_exp(message.from_user.id, 100)
        await message.answer("📈 *Ты выпил Зелье опыта!* 📈\n\n⭐ +100 опыта", parse_mode="Markdown")
    elif potion_num == 3:
        if potions.get('wealth', 0) == 0:
            await message.answer("❌ *У тебя нет Зелья богатства!*\nСначала создай его: `Создать зелье 3`", parse_mode="Markdown")
            return
        user['potions']['wealth'] -= 1
        user['balance'] += 1000
        await message.answer("💰 *Ты выпил Зелье богатства!* 💰\n\n✨ +1000 ₽", parse_mode="Markdown")
    else:
        await message.answer("❌ *Номера зелий:* 1, 2 или 3", parse_mode="Markdown")
        return
    
    save_user(message.from_user.id, user)

@dp.message(lambda msg: msg.text == "💒 Браки")
async def marriage_menu(message: types.Message):
    await message.answer(
        "💒 *БРАКИ* 💒\n\n"
        "💖 *Свадьба [ID пользователя]* — жениться на игроке\n"
        "   📌 Пример: `/marry @Анна`\n\n"
        "💔 *Развод* — развестись\n"
        "   📌 Команда: `/divorce`\n\n"
        "💌 *Мой брак* — посмотреть свой брак\n"
        "   📌 Команда: `/marriage`\n\n"
        "✨ *Преимущества брака:*\n"
        "• Общий доход +5%\n"
        "• Совместные кейсы\n"
        "• И многое другое!",
        parse_mode="Markdown"
    )

@dp.message(Command("marry"))
async def marry_user(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ *Используй:* `/marry @username`\n📌 *Пример:* `/marry @Анна`", parse_mode="Markdown")
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
        await message.answer("❌ *Игрок не найден!*\nУбедись, что ник написан правильно.", parse_mode="Markdown")
        return
    
    if user.get('married_to'):
        await message.answer(f"❌ *Ты уже в браке с {user['married_to']}!*\nСначала разведись: `/divorce`", parse_mode="Markdown")
        return
    
    if target_user.get('married_to'):
        await message.answer(f"❌ *{target_user['name']} уже в браке!*", parse_mode="Markdown")
        return
    
    user['married_to'] = target_user['name']
    user['married_id'] = target_id
    target_user['married_to'] = user['name']
    target_user['married_id'] = str(message.from_user.id)
    save_user(message.from_user.id, user)
    save_user(int(target_id), target_user)
    
    await message.answer(
        f"💒 *ПОЗДРАВЛЯЮ!* 💒\n\n"
        f"👰‍♀️ *{user['name']}* и *{target_user['name']}* теперь в браке!\n\n"
        f"🎉 Желаем счастья! 🎉\n\n"
        f"✨ *Бонус:* Общий доход +5%!",
        parse_mode="Markdown"
    )
    await bot.send_message(int(target_id), f"💒 *Поздравляем!* Ты вступил(а) в брак с {user['name']}! 💒", parse_mode="Markdown")

@dp.message(Command("divorce"))
async def divorce_user(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if not user.get('married_to'):
        await message.answer("❌ *Ты не в браке!*\nЧтобы пожениться: `/marry @username`", parse_mode="Markdown")
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
        await bot.send_message(int(partner_id), f"💔 *Развод!* Твой брак с {user['name']} расторгнут. 💔", parse_mode="Markdown")
    
    await message.answer(f"💔 *Развод оформлен!*\nТвой брак с {partner_name} расторгнут. 💔", parse_mode="Markdown")

@dp.message(Command("marriage"))
async def my_marriage(message: types.Message):
    user = init_user(message.from_user.id, message.from_user.username)
    if user.get('married_to'):
        await message.answer(
            f"💒 *ТВОЙ БРАК* 💒\n\n"
            f"👰‍♀️ *Супруг(а):* {user['married_to']}\n"
            f"💖 *Статус:* В браке\n"
            f"✨ *Бонус:* +5% к доходу\n\n"
            f"📌 Чтобы развестись: `/divorce`",
            parse_mode="Markdown"
        )
    else:
        await message.answer("💔 *Ты не в браке!*\n\nЧтобы найти любовь: `/marry @username`", parse_mode="Markdown")

@dp.message(lambda msg: msg.text == "📦 Кейсы")
async def cases_menu(message: types.Message):
    await message.answer(
        "📦 *КЕЙСЫ* 📦\n\n"
        "🔰 *Доступные кейсы:*\n"
        "• 1️⃣ *Обычный кейс* — 100 ₽\n"
        "  🎁 Шансы: 500-2000 ₽, + опыт\n"
        "• 2️⃣ *Редкий кейс* — 500 ₽\n"
        "  🎁 Шансы: 1000-5000 ₽, + опыт, + рейтинг\n"
        "• 3️⃣ *Эпический кейс* — 2000 ₽\n"
        "  🎁 Шансы: 5000-20000 ₽, + опыт, + рейтинг\n"
        "• 4️⃣ *Легендарный кейс* — 10000 ₽\n"
        "  🎁 Шансы: 20000-100000 ₽, + опыт, + рейтинг\n\n"
        "📌 *Команды:*\n"
        "• `Купить кейс [номер] [количество]`\n"
        "  📌 Пример: Купить кейс 1 5\n"
        "• `Открыть кейс [номер] [количество]`\n"
        "  📌 Пример: Открыть кейс 1 3",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text.startswith("Купить кейс"))
async def buy_case(message: types.Message):
    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("❌ *Пример:* Купить кейс 1 5\n\n1 — Обычный (100 ₽)\n2 — Редкий (500 ₽)\n3 — Эпический (2000 ₽)\n4 — Легендарный (10000 ₽)", parse_mode="Markdown")
        return
    try:
        case_num = int(parts[2])
        amount = int(parts[3])
    except:
        await message.answer("❌ *Введи номер кейса и количество!*", parse_mode="Markdown")
        return
    
    prices = {1: 100, 2: 500, 3: 2000, 4: 10000}
    case_names = {1: "common", 2: "rare", 3: "epic", 4: "legendary"}
    case_names_ru = {1: "Обычный", 2: "Редкий", 3: "Эпический", 4: "Легендарный"}
    
    if case_num not in prices:
        await message.answer("❌ *Номера кейсов:* 1, 2, 3 или 4", parse_mode="Markdown")
        return
    
    price = prices[case_num] * amount
    user = init_user(message.from_user.id, message.from_user.username)
    
    if user['balance'] < price:
        await message.answer(f"❌ *Не хватает!* Нужно {price:,} ₽, у тебя {user['balance']:,} ₽", parse_mode="Markdown")
        return
    
    user['balance'] -= price
    user['cases'][case_names[case_num]] = user['cases'].get(case_names[case_num], 0) + amount
    save_user(message.from_user.id, user)
    await message.answer(f"📦 *Ты купил {amount} {case_names_ru[case_num]} кейс(ов)!*\n\n💰 Цена: {price:,} ₽\n📦 Всего кейсов: {user['cases'][case_names[case_num]]}", parse_mode="Markdown")

@dp.message(lambda msg: msg.text.startswith("Открыть кейс"))
async def open_case(message: types.Message):
    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("❌ *Пример:* Открыть кейс 1 3\n\n1 — Обычный\n2 — Редкий\n3 — Эпический\n4 — Легендарный", parse_mode="Markdown")
        return
    try:
        case_num = int(parts[2])
        amount = int(parts[3])
    except:
        await message.answer("❌ *Введи номер кейса и количество!*", parse_mode="Markdown")
        return
    
    case_names = {1: "common", 2: "rare", 3: "epic", 4: "legendary"}
    case_names_ru = {1: "Обычный", 2: "Редкий", 3: "Эпический", 4: "Легендарный"}
    rewards = {
        1: {"money": (500, 2000), "exp": (10, 50), "rating": (0, 0)},
        2: {"money": (1000, 5000), "exp": (30, 100), "rating": (1, 5)},
        3: {"money": (5000, 20000), "exp": (50, 200), "rating": (5, 20)},
        4: {"money": (20000, 100000), "exp": (100, 500), "rating": (20, 100)}
    }
    
    if case_num not in case_names:
        await message.answer("❌ *Номера кейсов:* 1, 2, 3 или 4", parse_mode="Markdown")
        return
    
    user = init_user(message.from_user.id, message.from_user.username)
    case_type = case_names[case_num]
    
    if user['cases'].get(case_type, 0) < amount:
        await message.answer(f"❌ *У тебя только {user['cases'].get(case_type, 0)} {case_names_ru[case_num]} кейс(ов)!*", parse_mode="Markdown")
        return
    
    user['cases'][case_type] -= amount
    
    total_money = 0
    total_exp = 0
    total_rating = 0
    results = []
    
    for i in range(amount):
        money = random.randint(*rewards[case_num]["money"])
        exp = random.randint(*rewards[case_num]["exp"])
        rating = random.randint(*rewards[case_num]["rating"])
        total_money += money
        total_exp += exp
        total_rating += rating
        results.append(f"  {i+1}. 💰 +{money} ₽, ⭐ +{exp} опыта, 🏆 +{rating} рейтинга")
    
    user['balance'] += total_money
    add_exp(message.from_user.id, total_exp)
    user['rating'] = user.get('rating', 0) + total_rating
    save_user(message.from_user.id, user)
    
    result_text = "\n".join(results[:10])
    if amount > 10:
        result_text += f"\n  ... и ещё {amount - 10} кейсов"
    
    await message.answer(
        f"📦 *ОТКРЫТИЕ {amount} {case_names_ru[case_num]} КЕЙСОВ* 📦\n\n"
        f"{result_text}\n\n"
        f"📊 *ИТОГО:*\n"
        f"💰 +{total_money:,} ₽\n"
        f"⭐ +{total_exp} опыта\n"
        f"🏆 +{total_rating} рейтинга\n\n"
        f"📦 Осталось кейсов: {user['cases'][case_type]}",
        parse_mode="Markdown"
    )

@dp.message(lambda msg: msg.text == "🎮 Игры")
async def games_menu(message: types.Message):
    await message.answer(
        "🎲 *ВЫБЕРИ ИГРУ* 🎲\n\n"
        "👇 *Нажми на кнопку с игрой:* 👇",
        parse_mode="Markdown",
        reply_markup=games_keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("game_"))
async def handle_game_choice(callback: types.CallbackQuery):
    game = callback.data.replace("game_", "")
    user_game_state[callback.from_user.id] = f"game_{game}"
    
    if game == "spin":
        await callback.message.answer(
            "🎰 *СПИН* 🎰\n\n"
            "💰 *Множители:* x2, x3, x4, x5, x10\n"
            "📊 *Шанс выигрыша:* 40%\n\n"
            "👇 *Выбери ставку:*",
            parse_mode="Markdown",
            reply_markup=bet_keyboard
        )
    elif game == "dice":
        await callback.message.answer(
            "🎲 *КУБИК* 🎲\n\n"
            "💰 *Выигрыш:* x5\n"
            "📊 *Шанс:* 1/6\n\n"
            "👇 *Сначала выбери число:*",
            parse_mode="Markdown",
            reply_markup=dice_keyboard
        )
    elif game == "basketball":
        await callback.message.answer(
            "🏀 *БАСКЕТБОЛ* 🏀\n\n"
            "💰 *Выигрыш:* x2\n"
            "📊 *Шанс:* 50%\n\n"
            "👇 *Выбери ставку:*",
            parse_mode="Markdown",
            reply_markup=bet_keyboard
        )
    elif game == "dart":
        await callback.message.answer(
            "🎯 *ДАРТС* 🎯\n\n"
            "💰 *Выигрыш:* x3\n"
            "📊 *Шанс:* 33%\n\n"
            "👇 *Выбери ставку:*",
            parse_mode="Markdown",
            reply_markup=bet_keyboard
        )
    elif game == "bowling":
        await callback.message.answer(
            "🎳 *БОУЛИНГ* 🎳\n\n"
            "💰 *Страйк:* x3 (20%)\n"
            "💰 *Спэр:* x2 (30%)\n"
            "📊 *Общий шанс:* 50%\n\n"
            "👇 *Выбери ставку:*",
            parse_mode="Markdown",
            reply_markup=bet_keyboard
        )
    elif game == "trade":
        await callback.message.answer(
            "📉 *ТРЕЙД* 📈\n\n"
            "💰 *Выигрыш:* x1.5 до x3\n"
            "📊 *Шанс:* 50%\n\n"
            "👇 *Сначала выбери направление:*",
            parse_mode="Markdown",
            reply_markup=trade_keyboard
        )
    elif game == "casino":
        await callback.message.answer(
            "🎰 *КАЗИНО* 🎰\n\n"
            "💰 *Выигрыш:* x2\n"
            "📊 *Шанс:* 48%\n\n"
            "👇 *Выбери ставку:*",
            parse_mode="Markdown",
            reply_markup=bet_keyboard
        )
    elif game == "words":
        await callback.message.answer(
            "🎲 *ИГРА В СЛОВА* 🎲\n\n"
            "📖 *Правила:*\n"
            "Первый игрок пишет слово, следующий продолжает последнюю букву!\n\n"
            "📌 *Пример:*\n"
            "Игрок 1: Кот\n"
            "Игрок 2: Торт\n"
            "Игрок 3: Туча\n\n"
            "👇 *Напиши слово в чат!* 👇",
            parse_mode="Markdown"
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("dice_"))
async def handle_dice_choice(callback: types.CallbackQuery):
    guess = int(callback.data.split("_")[1])
    user_dice_guess[callback.from_user.id] = guess
    await callback.message.answer(f"🎲 *Ты выбрал число {guess}!*\n\n👇 *Теперь выбери ставку:*", parse_mode="Markdown", reply_markup=bet_keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("trade_"))
async def handle_trade_choice(callback: types.CallbackQuery):
    direction = callback.data.split("_")[1]
    user_trade_direction[callback.from_user.id] = direction
    await callback.message.answer(f"📉 *Ты выбрал направление {direction.upper()}!*\n\n👇 *Теперь выбери ставку:*", parse_mode="Markdown", reply_markup=bet_keyboard)
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
        await callback.message.answer(f"❌ *Не хватает!* У тебя {user['balance']:,} ₽", parse_mode="Markdown")
        await callback.answer()
        return
    
    game = game_state.replace("game_", "")
    
    msg = await callback.message.answer("🎲 *ИГРАЕМ...* 🎲\n\nПодбрасываю кубик...", parse_mode="Markdown")
    await asyncio.sleep(1.5)
    
    if game == "spin":
        multiplier = random.choice([2, 2, 3, 3, 4, 5, 10])
        if random.random() < 0.4:
            win = bet * multiplier
            user['balance'] += win
            await msg.edit_text(f"🎰 *СПИН* 🎰\n\n✨ ВЫПАЛ x{multiplier}! ✨\n\n🎉 ПОБЕДА! +{win:,} ₽", parse_mode="Markdown")
            add_exp(user_id, 10 * multiplier)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🎰 *СПИН* 🎰\n\n💔 НИЧЕГО НЕ ВЫПАЛО...\n\n😞 ПРОИГРЫШ! -{bet:,} ₽", parse_mode="Markdown")
    
    elif game == "dice":
        guess = user_dice_guess.get(user_id)
        if not guess:
            await callback.message.answer("❌ *Сначала выбери число!*", parse_mode="Markdown")
            await callback.answer()
            return
        roll = random.randint(1, 6)
        if roll == guess:
            win = bet * 5
            user['balance'] += win
            await msg.edit_text(f"🎲 *КУБИК* 🎲\n\nВыпало: {roll}\nТвоё число: {guess}\n\n🎉 УГАДАЛ! +{win:,} ₽", parse_mode="Markdown")
            add_exp(user_id, 25)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🎲 *КУБИК* 🎲\n\nВыпало: {roll}\nТвоё число: {guess}\n\n😞 НЕ УГАДАЛ! -{bet:,} ₽", parse_mode="Markdown")
        user_dice_guess[user_id] = None
    
    elif game == "basketball":
        if random.choice([True, False]):
            win = bet * 2
            user['balance'] += win
            await msg.edit_text(f"🏀 *БАСКЕТБОЛ* 🏀\n\n🏀 ПОПАДАНИЕ! 🏀\n\n🎉 ПОБЕДА! +{win:,} ₽", parse_mode="Markdown")
            add_exp(user_id, 10)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🏀 *БАСКЕТБОЛ* 🏀\n\n💔 ПРОМАХ!\n\n😞 ПРОИГРЫШ! -{bet:,} ₽", parse_mode="Markdown")
    
    elif game == "dart":
        if random.random() < 0.33:
            win = bet * 3
            user['balance'] += win
            await msg.edit_text(f"🎯 *ДАРТС* 🎯\n\n🎯 ЯБЛОЧКО! 🎯\n\n🎉 ПОБЕДА! +{win:,} ₽", parse_mode="Markdown")
            add_exp(user_id, 15)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🎯 *ДАРТС* 🎯\n\n💔 МИМО!\n\n😞 ПРОИГРЫШ! -{bet:,} ₽", parse_mode="Markdown")
    
    elif game == "bowling":
        rand = random.random()
        if rand < 0.2:
            win = bet * 3
            user['balance'] += win
            await msg.edit_text(f"🎳 *БОУЛИНГ* 🎳\n\n🎳 СТРАЙК! 🎳\n\n🎉 ПОБЕДА! +{win:,} ₽", parse_mode="Markdown")
            add_exp(user_id, 20)
        elif rand < 0.5:
            win = bet * 2
            user['balance'] += win
            await msg.edit_text(f"🎳 *БОУЛИНГ* 🎳\n\n🎳 СПЭР! 🎳\n\n🎉 ПОБЕДА! +{win:,} ₽", parse_mode="Markdown")
            add_exp(user_id, 10)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🎳 *БОУЛИНГ* 🎳\n\n💔 ПРОМАХ!\n\n😞 ПРОИГРЫШ! -{bet:,} ₽", parse_mode="Markdown")
    
    elif game == "trade":
        direction = user_trade_direction.get(user_id)
        if not direction:
            await callback.message.answer("❌ *Сначала выбери направление!*", parse_mode="Markdown")
            await callback.answer()
            return
        result = random.choice(["вверх", "вниз"])
        multiplier = random.uniform(1.5, 3.0)
        if direction == result:
            win = int(bet * multiplier)
            user['balance'] += win
            await msg.edit_text(f"📉 *ТРЕЙД* 📈\n\nКурс пошёл {result.upper()}! x{multiplier:.1f}\n\n🎉 ВЫИГРЫШ! +{win:,} ₽", parse_mode="Markdown")
            add_exp(user_id, 15)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"📉 *ТРЕЙД* 📈\n\nКурс пошёл {result.upper()}...\n\n😞 ПРОИГРЫШ! -{bet:,} ₽", parse_mode="Markdown")
        user_trade_direction[user_id] = None
    
    elif game == "casino":
        if random.random() < 0.48:
            win = bet * 2
            user['balance'] += win
            await msg.edit_text(f"🎰 *КАЗИНО* 🎰\n\n🍀 ВЕЗЁТ! 🍀\n\n🎉 ВЫИГРЫШ! +{win:,} ₽", parse_mode="Markdown")
            add_exp(user_id, 10)
        else:
            user['balance'] -= bet
            await msg.edit_text(f"🎰 *КАЗИНО* 🎰\n\n💔 НЕ ПОВЕЗЛО...\n\n😞 ПРОИГРЫШ! -{bet:,} ₽", parse_mode="Markdown")
    
    save_user(user_id, user)
    user_game_state[user_id] = None
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.answer("◀️ *Главное меню:*", parse_mode="Markdown", reply_markup=main_keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_games")
async def back_to_games(callback: types.CallbackQuery):
    await callback.message.answer("🎲 *ВЫБЕРИ ИГРУ* 🎲", parse_mode="Markdown", reply_markup=games_keyboard)
    await callback.answer()

async def main():
    print("🤖 Бот запущен!")
    print("✅ Retro 19? — полная экономическая игра")
    print("✅ Все команды работают!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
