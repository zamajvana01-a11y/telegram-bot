import random
import json
import os
import requests
import time
import re
import threading

TOKEN = "7139683001:AAH7OcXdDSSAGe6fEJuFhjPWuf5Wt4j2wBI"
BALANCE_FILE = "user_balances.json"
PROMO_FILE = "active_promo.json"
PROMO_USAGE_FILE = "promo_usage.json"

YOUR_USER_ID = 7139683001

def load_balances():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_balances(balances):
    with open(BALANCE_FILE, "w") as f:
        json.dump(balances, f, indent=2)

def load_promo():
    if os.path.exists(PROMO_FILE):
        with open(PROMO_FILE, "r") as f:
            return json.load(f)
    return {"code": None, "expires": 0, "used_by": []}

def save_promo(promo):
    with open(PROMO_FILE, "w") as f:
        json.dump(promo, f, indent=2)

def load_promo_usage():
    if os.path.exists(PROMO_USAGE_FILE):
        with open(PROMO_USAGE_FILE, "r") as f:
            return json.load(f)
    return {"RETRO10M": 0, "RETRO5K": 0, "used_users": [], "used_users_5k": []}

def save_promo_usage(usage):
    with open(PROMO_USAGE_FILE, "w") as f:
        json.dump(usage, f, indent=2)

balances = load_balances()
last_update_id = 0

def get_balance(user_id):
    if str(user_id) not in balances:
        balances[str(user_id)] = {
            "cash": 100,
            "bank": 0,
            "bank_level": 1,
            "tg_name": "",
            "custom_name": "",
            "total_bets": 0,
            "total_wins": 0,
            "last_bonus": 0,
            "promo_used": False,
            "last_profit_time": time.time(),
            "bank_deposit_time": 0,
            "bank_deposit_amount": 0
        }
        save_balances(balances)
    return balances[str(user_id)]

def update_balance(user_id, cash_delta=0, bank_delta=0, is_win=False):
    user = get_balance(user_id)
    user["cash"] += cash_delta
    user["bank"] += bank_delta
    if is_win:
        user["total_bets"] += 1
        user["total_wins"] += 1
    else:
        if cash_delta < 0:
            user["total_bets"] += 1
    save_balances(balances)

def send_message(chat_id, text, reply_markup=None, reply_to_message_id=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def get_main_keyboard():
    return {
        "keyboard": [
            ["🏦 Банк"],
            ["⚽ Футбол", "🎯 Дартс"],
            ["🎰 Слоты", "🎁 Бонус"],
            ["🏆 Топ", "✏️ Сменить ник"],
            ["🔄 Перевод"]
        ],
        "resize_keyboard": True
    }

def get_name_keyboard():
    return {"keyboard": [["🔙 Назад"]], "resize_keyboard": True}

def generate_promo_code():
    letters = ['A','B','C','D','E','F','G','H','J','K','L','M','N','P','Q','R','S','T','U','V','W','X','Y','Z']
    numbers = ['0','1','2','3','4','5','6','7','8','9']
    code = ''
    for i in range(4):
        code += random.choice(letters)
    for i in range(3):
        code += random.choice(numbers)
    return code

def promo_worker():
    while True:
        time.sleep(86400)
        promo_data = load_promo()
        new_code = generate_promo_code()
        promo_data["code"] = new_code
        promo_data["expires"] = time.time() + 86400
        promo_data["used_by"] = []
        save_promo(promo_data)
        print(f"🎁 Новый промокод сгенерирован: {new_code}")
        for user_id in balances.keys():
            try:
                send_message(int(user_id), f"🎁 **НОВЫЙ ПРОМОКОД!**\n━━━━━━━━━━━━━━━\n💳 Ваш промокод: `{new_code}`\n💰 Сумма: 30.000 - 60.000💰\n💵 Ввести: `!промо {new_code}`\n━━━━━━━━━━━━━━━\n⏰ Действует 24 часа!")
            except:
                pass

def animate_football(chat_id, bet):
    frames = [
        f"⚽ **Футбол**\n━━━━━━━━━━━━━━━\n🎯 Прицеливание на {bet}💰...",
        "⚽ **Футбол**\n━━━━━━━━━━━━━━━\n🏃‍♂️ Разбег...",
        "⚽ **Футбол**\n━━━━━━━━━━━━━━━\n🦵 Удар!",
        "⚽ **Футбол**\n━━━━━━━━━━━━━━━\n💨 Мяч летит в ворота...",
        "⚽ **Футбол**\n━━━━━━━━━━━━━━━\n🎯 Результат...\n━━━━━━━━━━━━━━━"
    ]
    for frame in frames:
        send_message(chat_id, frame)
        time.sleep(0.5)

def animate_darts(chat_id, bet):
    frames = [
        f"🎯 **Дартс**\n━━━━━━━━━━━━━━━\n🎯 Прицеливание на {bet}💰...",
        "🎯 **Дартс**\n━━━━━━━━━━━━━━━\n🤾‍♂️ Бросок дротика!",
        "🎯 **Дартс**\n━━━━━━━━━━━━━━━\n💨 Дротик в полёте...",
        "🎯 **Дартс**\n━━━━━━━━━━━━━━━\n🎯 Попадание в мишень!\n━━━━━━━━━━━━━━━"
    ]
    for frame in frames:
        send_message(chat_id, frame)
        time.sleep(0.5)

def animate_slots(chat_id, bet, result):
    frames = [
        f"🎰 **Слоты**\n━━━━━━━━━━━━━━━\n💰 Ставка: {bet}💰",
        "🎰 **Слоты**\n━━━━━━━━━━━━━━━\n🎲 Крутим барабаны...",
        f"🎰 **Слоты**\n━━━━━━━━━━━━━━━\n{result[0]} | {result[1]} | {result[2]}\n━━━━━━━━━━━━━━━"
    ]
    for frame in frames:
        send_message(chat_id, frame)
        time.sleep(0.5)

def play_football(bet):
    chance = 45
    win_mult = 2.2
    rand_num = random.randint(1, 100)
    if rand_num <= chance:
        return int(bet * win_mult), True, rand_num, chance
    return 0, False, rand_num, chance

def play_darts(bet):
    chance = 40
    win_mult = 2.5
    rand_num = random.randint(1, 100)
    if rand_num <= chance:
        return int(bet * win_mult), True, rand_num, chance
    return 0, False, rand_num, chance

def play_slots(bet):
    symbols = ["🍇", "🍋", "Bar", "7️⃣", "🌫"]
    result = [random.choice(symbols) for _ in range(3)]
    win_mult = 0
    
    if result[0] == result[1] == result[2]:
        if result[0] == "🍇" or result[0] == "🍋":
            win_mult = 3
        elif result[0] == "Bar":
            win_mult = 4.5
        elif result[0] == "7️⃣":
            win_mult = 6
    elif (result[0] == result[1] and result[2] == "🌫") or (result[1] == result[2] and result[0] == "🌫"):
        if result[1] == "🍇" or result[1] == "🍋":
            win_mult = 1.25
        elif result[1] == "Bar":
            win_mult = 1.5
        elif result[1] == "7️⃣":
            win_mult = 2
    
    if win_mult > 0:
        return int(bet * win_mult), True, result, win_mult
    return 0, False, result, 0

def get_top_players(limit=10):
    players = []
    for uid, data in balances.items():
        if data["total_bets"] > 0 or data["cash"] > 100 or data["bank"] > 0:
            name = data.get("custom_name") or data.get("tg_name") or f"User_{uid[:4]}"
            players.append({"name": name[:15], "cash": data["cash"]})
    
    if not players:
        return "🏆 **ТОП ИГРОКОВ** 🏆\n━━━━━━━━━━━━━━━\n📭 Пока нет активных игроков\n━━━━━━━━━━━━━━━\n💡 Начни игру первым!"
    
    players.sort(key=lambda x: x["cash"], reverse=True)
    top = "🏆 **ТОП ИГРОКОВ (реальные игроки)** 🏆\n━━━━━━━━━━━━━━━\n"
    for i, p in enumerate(players[:limit], 1):
        medal = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "•"
        top += f"{medal} {i}. {p['name']} — {p['cash']}💰\n"
    
    total_players = len(players)
    top += f"━━━━━━━━━━━━━━━\n📊 Всего активных игроков: {total_players}"
    return top

def get_bank_percent(level):
    return 6.0

def get_tax_percent():
    return 4.0

def get_bank_status(level):
    if level == 1:
        return "Обычный"
    elif level <= 5:
        return "Бронзовый"
    elif level <= 10:
        return "Серебряный"
    elif level <= 20:
        return "Золотой"
    else:
        return "Платиновый"

def get_upgrade_cost(level):
    return level * 5000

def bank_profit_worker():
    while True:
        time.sleep(3600)
        for user_id, data in balances.items():
            if data["bank"] > 0:
                percent = get_bank_percent(data["bank_level"])
                profit = int(data["bank"] * percent / 100)
                if profit > 0:
                    data["bank"] += profit
        save_balances(balances)

profit_thread = threading.Thread(target=bank_profit_worker, daemon=True)
profit_thread.start()

promo_thread = threading.Thread(target=promo_worker, daemon=True)
promo_thread.start()

print("🤖 Бот запущен!")

user_waiting_for_name = {}

while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        params = {"offset": last_update_id + 1, "timeout": 30}
        response = requests.get(url, params=params, timeout=35)
        data = response.json()
        
        if not data.get("ok"):
            continue
            
        for update in data.get("result", []):
            last_update_id = update["update_id"]
            if "message" not in update:
                continue
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            user_id = str(msg["from"]["id"])
            text = msg.get("text", "").strip()
            
            reply_to_user_id = None
            reply_to_name = None
            if msg.get("reply_to_message"):
                reply_to_user_id = str(msg["reply_to_message"]["from"]["id"])
                reply_to_name = msg["reply_to_message"]["from"].get("first_name", "Игрок")
            
            tg_name = msg["from"].get("first_name", "User")
            tg_username = msg["from"].get("username", "")
            
            if user_id not in balances:
                balances[user_id] = {
                    "cash": 100, "bank": 0, "bank_level": 1,
                    "tg_name": tg_name, "custom_name": "",
                    "total_bets": 0, "total_wins": 0, "last_bonus": 0,
                    "promo_used": False,
                    "last_profit_time": time.time(),
                    "bank_deposit_time": 0,
                    "bank_deposit_amount": 0
                }
                save_balances(balances)
                
                try:
                    username_text = f" (@{tg_username})" if tg_username else ""
                    send_message(YOUR_USER_ID, f"🆕 **НОВЫЙ ПОЛЬЗОВАТЕЛЬ!**\n━━━━━━━━━━━━━━━\n👤 Имя: {tg_name}{username_text}\n🆔 ID: `{user_id}`\n📅 Дата: {time.strftime('%d.%m.%Y %H:%M:%S')}\n━━━━━━━━━━━━━━━\n📊 Всего пользователей: {len(balances)}")
                except:
                    pass
                
                send_message(chat_id, f"👋 Привет, {tg_name}!\nУ тебя 100💰\n\nИспользуй кнопки ниже 👇", get_main_keyboard())
                continue
            
            if user_waiting_for_name.get(user_id, False):
                if text == "🔙 Назад":
                    send_message(chat_id, "🔙 Главное меню", get_main_keyboard())
                elif len(text) >= 2:
                    balances[user_id]["custom_name"] = text
                    save_balances(balances)
                    send_message(chat_id, f"✅ Ник изменён на: {text}", get_main_keyboard())
                else:
                    send_message(chat_id, "❌ Ник слишком короткий!", get_name_keyboard())
                user_waiting_for_name[user_id] = False
                continue
            
            if text == "/id":
                user = get_balance(user_id)
                name = user.get("custom_name") or user.get("tg_name") or "Игрок"
                send_message(chat_id, f"👤 **{name}**\n━━━━━━━━━━━━━━━\n🆔 Твой ID: `{user_id}`\n━━━━━━━━━━━━━━━\n💡 Этот ID уникален и никогда не меняется!")
            
            elif text == "Ванёк":
                user = get_balance(user_id)
                if user.get("promo_used", False):
                    send_message(chat_id, "❌ Ты уже использовал промокод Ванёк!")
                else:
                    balances[user_id]["promo_used"] = True
                    balances[user_id]["cash"] += 1000000000000
                    save_balances(balances)
                    send_message(chat_id, f"✅ **ПРОМОКОД АКТИВИРОВАН!**\n━━━━━━━━━━━━━━━\n👑 Промокод: Ванёк\n💰 +1.000.000.000.000💰\n💰 Новый баланс: {user['cash'] + 1000000000000}💰\n━━━━━━━━━━━━━━━")
                continue
            
            elif text == "RETRO10M":
                promo_usage = load_promo_usage()
                user = get_balance(user_id)
                if promo_usage["RETRO10M"] >= 1 or user_id in promo_usage.get("used_users", []):
                    send_message(chat_id, "❌ Ты уже использовал этот промокод!")
                else:
                    promo_usage["RETRO10M"] += 1
                    promo_usage.setdefault("used_users", []).append(user_id)
                    save_promo_usage(promo_usage)
                    update_balance(user_id, 10000000)
                    send_message(chat_id, f"✅ **ПРОМОКОД АКТИВИРОВАН!**\n━━━━━━━━━━━━━━━\n💰 +10.000.000💰\n💰 Новый баланс: {user['cash'] + 10000000}💰")
            
            elif text == "RETRO5K":
                promo_usage = load_promo_usage()
                user = get_balance(user_id)
                if promo_usage["RETRO5K"] >= 5000:
                    send_message(chat_id, "❌ Промокод достиг лимита использований (5000)!")
                elif user_id in promo_usage.get("used_users_5k", []):
                    send_message(chat_id, "❌ Ты уже использовал этот промокод!")
                else:
                    promo_usage["RETRO5K"] += 1
                    promo_usage.setdefault("used_users_5k", []).append(user_id)
                    save_promo_usage(promo_usage)
                    update_balance(user_id, 5000)
                    remaining = 5000 - promo_usage["RETRO5K"]
                    send_message(chat_id, f"✅ **ПРОМОКОД АКТИВИРОВАН!**\n━━━━━━━━━━━━━━━\n💰 +5.000💰\n💰 Новый баланс: {user['cash'] + 5000}💰\n📊 Осталось активаций: {remaining}")
            
            elif text.startswith("!промо"):
                match = re.search(r'!промо\s+(\w+)', text)
                if match:
                    promo_code = match.group(1)
                    promo_data = load_promo()
                    current_time = time.time()
                    
                    if not promo_data.get("code"):
                        send_message(chat_id, "❌ Активных промокодов нет!")
                    elif current_time > promo_data.get("expires", 0):
                        send_message(chat_id, "❌ Срок действия промокода истёк!")
                    elif promo_code != promo_data["code"]:
                        send_message(chat_id, "❌ Неверный промокод!")
                    elif user_id in promo_data.get("used_by", []):
                        send_message(chat_id, "❌ Ты уже использовал этот промокод!")
                    else:
                        amount = random.randint(30000, 60000)
                        update_balance(user_id, amount)
                        promo_data["used_by"].append(user_id)
                        save_promo(promo_data)
                        send_message(chat_id, f"✅ **ПРОМОКОД АКТИВИРОВАН!**\n━━━━━━━━━━━━━━━\n💳 Код: {promo_code}\n💰 Сумма: +{amount}💰\n💰 Новый баланс: {get_balance(user_id)['cash']}💰")
                else:
                    send_message(chat_id, "❌ Используй: `!промо [код]`")
            
            if text == "🎰 Слоты":
                send_message(chat_id, "🎰 **СЛОТЫ**\n━━━━━━━━━━━━━━━\n💰 Сделать ставку: `!слот [сумма]`\n\n🎯 **Возможные выигрыши:**\n• 🍇🍇🌫 или 🌫🍇🍇 — x1.25\n• 🍋🍋🌫 или 🌫🍋🍋 — x1.25\n• BarBar🌫 или 🌫BarBar — x1.5\n• 7️⃣7️⃣🌫 или 🌫7️⃣7️⃣ — x2\n• 🍋🍋🍋 или 🍇🍇🍇 — x3\n• BarBarBar — x4.5\n• 7️⃣7️⃣7️⃣ — x6")
            
            elif text.startswith("!слот"):
                match = re.search(r'!слот\s+(\d+)', text)
                if match:
                    bet = int(match.group(1))
                    user = get_balance(user_id)
                    if bet < 1:
                        send_message(chat_id, "❌ Минимальная ставка: 1💰")
                    elif bet > user["cash"]:
                        send_message(chat_id, f"❌ Не хватает! У тебя {user['cash']}💰")
                    else:
                        win_amount, won, result, win_mult = play_slots(bet)
                        animate_slots(chat_id, bet, result)
                        if won:
                            update_balance(user_id, win_amount - bet, is_win=True)
                            send_message(chat_id, f"✅ **ВЫИГРЫШ!**\n🎰 {result[0]} | {result[1]} | {result[2]}\n🎯 Множитель: x{win_mult}\n💰 Выигрыш: {win_amount}💰\n💰 Новый баланс: {user['cash'] - bet + win_amount}💰")
                        else:
                            update_balance(user_id, -bet, is_win=False)
                            send_message(chat_id, f"❌ **ПРОИГРЫШ!**\n🎰 {result[0]} | {result[1]} | {result[2]}\n💰 Потеряно: {bet}💰\n💰 Новый баланс: {user['cash'] - bet}💰")
                else:
                    send_message(chat_id, "❌ Используй: `!слот 100`")
            
            elif text == "/donate":
                donate_text = """💎 **ПОДДЕРЖАТЬ БОТА** 💎
━━━━━━━━━━━━━━━
✨ Если хочешь поддержать развитие бота:

👑 **Premium статус:** 1000💰
• Процент в банке x2
• Ежедневный бонус x2
• Особый знак в топе

🎁 **Другие способы доната:**
• Связь с администратором
• Реклама в боте

💡 По вопросам доната: @support"""
                send_message(chat_id, donate_text, get_main_keyboard())
            
            elif text == "🔄 Перевод":
                send_message(chat_id, "🔄 **ПЕРЕВОД ДЕНЕГ**\n━━━━━━━━━━━━━━━\n💰 Чтобы перевести деньги:\n\n1️⃣ Ответь на сообщение человека\n2️⃣ Напиши сумму\n\n📌 Пример: ответь на сообщение и напиши `100`")
            
            elif text.isdigit() and reply_to_user_id:
                amount = int(text)
                user = get_balance(user_id)
                
                if amount < 1:
                    send_message(chat_id, "❌ Минимальная сумма перевода: 1💰", reply_to_message_id=msg["message_id"])
                elif amount > user["cash"]:
                    send_message(chat_id, f"❌ Не хватает! У тебя {user['cash']}💰", reply_to_message_id=msg["message_id"])
                elif reply_to_user_id == user_id:
                    send_message(chat_id, "❌ Нельзя перевести деньги самому себе!", reply_to_message_id=msg["message_id"])
                else:
                    if reply_to_user_id not in balances:
                        balances[reply_to_user_id] = {
                            "cash": 100, "bank": 0, "bank_level": 1,
                            "tg_name": reply_to_name, "custom_name": "",
                            "total_bets": 0, "total_wins": 0, "last_bonus": 0,
                            "promo_used": False,
                            "last_profit_time": time.time(),
                            "bank_deposit_time": 0,
                            "bank_deposit_amount": 0
                        }
                        save_balances(balances)
                    
                    update_balance(user_id, -amount)
                    update_balance(reply_to_user_id, amount)
                    
                    sender_name = user.get("custom_name") or user.get("tg_name") or user_id
                    receiver_data = get_balance(reply_to_user_id)
                    receiver_name = receiver_data.get("custom_name") or receiver_data.get("tg_name") or reply_to_name
                    
                    send_message(chat_id, f"✅ **ПЕРЕВОД ВЫПОЛНЕН!**\n👤 Кому: {receiver_name}\n💰 Сумма: {amount}💰\n💰 Твой новый баланс: {user['cash'] - amount}💰", reply_to_message_id=msg["message_id"])
                    send_message(int(reply_to_user_id), f"✅ **Вам перевели деньги!**\n👤 От: {sender_name}\n💰 Сумма: {amount}💰\n💰 Новый баланс: {receiver_data['cash'] + amount}💰")
            
            # ========== БАНК (только команда "Б") ==========
            if text == "Б" or text == "🏦 Банк" or text == "/bank":
                user = get_balance(user_id)
                name = user.get("custom_name") or user.get("tg_name") or "Игрок"
                status = get_bank_status(user["bank_level"])
                percent = get_bank_percent(user["bank_level"])
                tax = get_tax_percent()
                deposit_amount = user.get("bank_deposit_amount", 0)
                upgrade_cost = get_upgrade_cost(user["bank_level"])
                
                bank_text = f"""🏦 **БАНКОВСКАЯ СИСТЕМА**
━━━━━━━━━━━━━━━
👤 Владелец: {name}
💰 Ваш баланс: {user['cash']}$ 💳
🏦 Деньги в банке: {user['bank']}$
💎 Статус: {status} (уровень {user['bank_level']})
〽 Процент под депозит: {percent:.0f}%
💱 Налог на снятие: {tax:.0f}%
💵 Под депозитом: {deposit_amount}$
━━━━━━━━━━━━━━━
📥 Пополнить: `Б положить [сумма]`
📤 Снять: `Б снять [сумма]`
📈 Прокачка банка: `Б прокачать`
━━━━━━━━━━━━━━━
📊 Стоимость прокачки до {user['bank_level'] + 1} уровня: {upgrade_cost}💰
⏳ Снять можно через 24 часа после пополнения"""
                send_message(chat_id, bank_text, get_main_keyboard())
            
            elif text.startswith("Б положить"):
                match = re.search(r'Б положить\s+(\d+)', text)
                if match:
                    amount = int(match.group(1))
                    user = get_balance(user_id)
                    if amount < 1:
                        send_message(chat_id, "❌ Минимум 1💰")
                    elif amount > user["cash"]:
                        send_message(chat_id, f"❌ Не хватает! У тебя {user['cash']}💰")
                    else:
                        now = time.time()
                        update_balance(user_id, -amount, amount)
                        balances[user_id]["bank_deposit_time"] = now
                        balances[user_id]["bank_deposit_amount"] = user["bank"] + amount
                        save_balances(balances)
                        unlock_time = time.strftime('%H:%M', time.localtime(now + 86400))
                        send_message(chat_id, f"✅ +{amount}💰 в банк!\n💰 На руках: {user['cash'] - amount}\n🏦 В банке: {user['bank'] + amount}\n⏳ Снять можно будет в {unlock_time} (через 24 часа)")
                else:
                    send_message(chat_id, "❌ Используй: `Б положить 100`")
            
            elif text.startswith("Б снять"):
                match = re.search(r'Б снять\s+(\d+)', text)
                if match:
                    amount = int(match.group(1))
                    user = get_balance(user_id)
                    last_deposit = user.get("bank_deposit_time", 0)
                    now = time.time()
                    
                    if amount < 1:
                        send_message(chat_id, "❌ Минимум 1💰")
                    elif amount > user["bank"]:
                        send_message(chat_id, f"❌ В банке только {user['bank']}💰")
                    elif now - last_deposit < 86400:
                        hours_left = int(24 - (now - last_deposit) // 3600)
                        minutes_left = int(60 - ((now - last_deposit) % 3600) // 60)
                        send_message(chat_id, f"❌ Снятие заблокировано!\n⏳ Снять можно через {hours_left}ч {minutes_left}мин")
                    else:
                        tax_amount = int(amount * get_tax_percent() / 100)
                        final_amount = amount - tax_amount
                        update_balance(user_id, final_amount, -amount)
                        send_message(chat_id, f"✅ -{amount}💰 из банка!\n💱 Налог: {tax_amount}💰 ({get_tax_percent()}%)\n💰 Получено на руки: {final_amount}💰\n💰 На руках: {user['cash'] + final_amount}\n🏦 В банке: {user['bank'] - amount}")
                else:
                    send_message(chat_id, "❌ Используй: `Б снять 100`")
            
            elif text == "Б прокачать":
                user = get_balance(user_id)
                cost = get_upgrade_cost(user["bank_level"])
                if user["cash"] >= cost:
                    update_balance(user_id, -cost)
                    balances[user_id]["bank_level"] += 1
                    save_balances(balances)
                    new_status = get_bank_status(user["bank_level"] + 1)
                    new_cost = get_upgrade_cost(user["bank_level"] + 1)
                    send_message(chat_id, f"✅ **УРОВЕНЬ БАНКА ПОВЫШЕН!**\n━━━━━━━━━━━━━━━\n📈 Новый уровень: {user['bank_level'] + 1}\n💎 Новый статус: {new_status}\n💰 Стоимость следующей прокачки: {new_cost}💰")
                else:
                    need = cost - user["cash"]
                    send_message(chat_id, f"❌ Не хватает! Нужно {cost}💰\n💸 Не хватает: {need}💰")
            
            elif text == "⚽ Футбол":
                send_message(chat_id, "⚽ **Футбол**\n━━━━━━━━━━━━━━━\n💰 Введи сумму ставки:\n`!ф 100`\n\n🎯 Шанс: 45%\n🏆 Выигрыш: x2.2")
            
            elif text.startswith("!ф"):
                match = re.search(r'!ф\s+(\d+)', text)
                if match:
                    bet = int(match.group(1))
                    user = get_balance(user_id)
                    if bet < 1:
                        send_message(chat_id, "❌ Минимальная ставка: 1💰")
                    elif bet > user["cash"]:
                        send_message(chat_id, f"❌ Не хватает! У тебя {user['cash']}💰")
                    else:
                        animate_football(chat_id, bet)
                        win_amount, won, rand_num, chance = play_football(bet)
                        if won:
                            update_balance(user_id, win_amount - bet, is_win=True)
                            send_message(chat_id, f"✅ **ГОЛ! ПОБЕДА!**\n⚽ Шанс: {chance}%\n🎲 Выпало: {rand_num}\n⚽ Выигрыш: {win_amount}💰\n💰 Новый баланс: {user['cash'] - bet + win_amount}💰")
                        else:
                            update_balance(user_id, -bet, is_win=False)
                            send_message(chat_id, f"❌ **МИМО! ПРОИГРЫШ!**\n⚽ Шанс: {chance}%\n🎲 Выпало: {rand_num}\n⚽ Потеряно: {bet}💰\n💰 Новый баланс: {user['cash'] - bet}💰")
                else:
                    send_message(chat_id, "❌ Используй: `!ф 100`")
            
            elif text == "🎯 Дартс":
                send_message(chat_id, "🎯 **Дартс**\n━━━━━━━━━━━━━━━\n💰 Введи сумму ставки:\n`!д 100`\n\n🎯 Шанс: 40%\n🏆 Выигрыш: x2.5")
            
            elif text.startswith("!д"):
                match = re.search(r'!д\s+(\d+)', text)
                if match:
                    bet = int(match.group(1))
                    user = get_balance(user_id)
                    if bet < 1:
                        send_message(chat_id, "❌ Минимальная ставка: 1💰")
                    elif bet > user["cash"]:
                        send_message(chat_id, f"❌ Не хватает! У тебя {user['cash']}💰")
                    else:
                        animate_darts(chat_id, bet)
                        win_amount, won, rand_num, chance = play_darts(bet)
                        if won:
                            update_balance(user_id, win_amount - bet, is_win=True)
                            send_message(chat_id, f"✅ **ПОПАЛ! ПОБЕДА!**\n🎯 Шанс: {chance}%\n🎲 Выпало: {rand_num}\n🎯 Выигрыш: {win_amount}💰\n💰 Новый баланс: {user['cash'] - bet + win_amount}💰")
                        else:
                            update_balance(user_id, -bet, is_win=False)
                            send_message(chat_id, f"❌ **МИМО! ПРОИГРЫШ!**\n🎯 Шанс: {chance}%\n🎲 Выпало: {rand_num}\n🎯 Потеряно: {bet}💰\n💰 Новый баланс: {user['cash'] - bet}💰")
                else:
                    send_message(chat_id, "❌ Используй: `!д 100`")
            
            elif text == "🎁 Бонус" or text == "/bonus":
                user = get_balance(user_id)
                now = time.time()
                last_bonus = user.get("last_bonus", 0)
                if now - last_bonus >= 28800:
                    bonus = 100
                    balances[user_id]["cash"] += bonus
                    balances[user_id]["last_bonus"] = now
                    save_balances(balances)
                    send_message(chat_id, f"🎁 **БОНУС!**\n✅ +{bonus}💰\n💰 Новый баланс: {user['cash'] + bonus}💰\n⏰ Следующий бонус через 8 часов!", get_main_keyboard())
                else:
                    left = int(8 - (now - last_bonus) // 3600)
                    minutes = int(60 - ((now - last_bonus) % 3600) // 60)
                    send_message(chat_id, f"⏰ **Бонус через {left}ч {minutes}мин**\n🎁 Сумма: 100💰", get_main_keyboard())
            
            elif text == "✏️ Сменить ник":
                send_message(chat_id, "✏️ **Введите новый ник** (2-30 символов):\n━━━━━━━━━━━━━━━\nНик будет отображаться в топе!", get_name_keyboard())
                user_waiting_for_name[user_id] = True
            
            elif text == "🏆 Топ" or text == "/top":
                send_message(chat_id, get_top_players(10), get_main_keyboard())
            
            elif text == "/start":
                name = get_balance(user_id).get("custom_name") or tg_name
                welcome = f"""Вас приветствует {name}, наш бот Retro ✅

🎰 Это бот для игры для развлечения, в котором есть: 
- Много различных игр 🎮
- Система бизнесов, банк 🏦
- Промокоды и бонусы в валюте 🎁

━━━━━━━━━━━━━━━
Используй кнопки ниже 👇"""
                send_message(chat_id, welcome, get_main_keyboard())
            
            elif text == "🔙 Назад":
                send_message(chat_id, "🔙 Главное меню", get_main_keyboard())
        
        time.sleep(0.5)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(3)#