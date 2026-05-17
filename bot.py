# =========================================
# ADVANCED TELEGRAM GAMING BOT
# Features:
# ✅ XP & Level System
# ✅ Coins System
# ✅ Daily Rewards
# ✅ Matchmaking Queue
# ✅ Leaderboard
# ✅ Profile System
# ✅ SQLite Database
# =========================================

import sqlite3
import random
from datetime import datetime, timedelta

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================================
# DATABASE SETUP
# =========================================

conn = sqlite3.connect("gaming_bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    coins INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    last_daily TEXT
)
""")

conn.commit()

# =========================================
# FUNCTIONS
# =========================================

def calculate_level(xp):
    return (xp // 100) + 1

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def create_user(user_id, username):
    cursor.execute("""
    INSERT OR IGNORE INTO users
    (user_id, username, xp, level, coins, wins, losses)
    VALUES (?, ?, 0, 1, 100, 0, 0)
    """, (user_id, username))
    conn.commit()

def update_user(user_id, xp=0, coins=0, wins=0, losses=0):
    user = get_user(user_id)

    current_xp = user[2] + xp
    current_level = calculate_level(current_xp)
    current_coins = user[4] + coins
    current_wins = user[5] + wins
    current_losses = user[6] + losses

    cursor.execute("""
    UPDATE users
    SET xp=?, level=?, coins=?, wins=?, losses=?
    WHERE user_id=?
    """, (
        current_xp,
        current_level,
        current_coins,
        current_wins,
        current_losses,
        user_id
    ))

    conn.commit()

# =========================================
# MATCHMAKING
# =========================================

match_queue = []

# =========================================
# COMMANDS
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    create_user(user.id, user.first_name)

    keyboard = [
        ["👤 Profile", "🎁 Daily"],
        ["⚔ Match", "🏆 Leaderboard"],
    ]

    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"🔥 Welcome {user.first_name}!\n"
        f"🎮 Gaming Bot Activated!",
        reply_markup=markup
    )

# =========================================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user = get_user(user_id)

    msg = (
        f"👤 PROFILE\n\n"
        f"⭐ Level: {user[3]}\n"
        f"🔥 XP: {user[2]}\n"
        f"💰 Coins: {user[4]}\n"
        f"🏆 Wins: {user[5]}\n"
        f"❌ Losses: {user[6]}"
    )

    await update.message.reply_text(msg)

# =========================================

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user = get_user(user_id)

    last_daily = user[7]

    now = datetime.now()

    if last_daily:
        old = datetime.fromisoformat(last_daily)

        if now - old < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - old)

            await update.message.reply_text(
                f"⏳ Daily already claimed.\n"
                f"Try again in: {remaining}"
            )
            return

    reward = random.randint(50, 200)

    update_user(user_id, coins=reward, xp=25)

    cursor.execute("""
    UPDATE users
    SET last_daily=?
    WHERE user_id=?
    """, (now.isoformat(), user_id))

    conn.commit()

    await update.message.reply_text(
        f"🎁 Daily Reward Claimed!\n"
        f"💰 Coins: +{reward}\n"
        f"⭐ XP: +25"
    )

# =========================================

async def match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    user_id = update.effective_user.id

    if user_id in match_queue:
        await update.message.reply_text(
            "⏳ Already searching for match..."
        )
        return

    match_queue.append(user_id)

    if len(match_queue) >= 2:
        p1 = match_queue.pop(0)
        p2 = match_queue.pop(0)

        winner = random.choice([p1, p2])

        loser = p2 if winner == p1 else p1

        update_user(winner, xp=50, coins=100, wins=1)
        update_user(loser, xp=20, coins=25, losses=1)

        await update.message.reply_text(
            f"⚔ MATCH FOUND!\n\n"
            f"🏆 Winner gets:\n"
            f"+50 XP\n"
            f"+100 Coins"
        )

    else:
        await update.message.reply_text(
            "🔍 Searching for opponent..."
        )

# =========================================

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("""
    SELECT username, level, xp, wins
    FROM users
    ORDER BY xp DESC
    LIMIT 10
    """)

    top = cursor.fetchall()

    text = "🏆 LEADERBOARD\n\n"

    for i, player in enumerate(top, start=1):
        text += (
            f"{i}. {player[0]}\n"
            f"⭐ Level: {player[1]}\n"
            f"🔥 XP: {player[2]}\n"
            f"🏆 Wins: {player[3]}\n\n"
        )

    await update.message.reply_text(text)

# =========================================
# BUTTON HANDLER
# =========================================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "👤 Profile":
        await profile(update, context)

    elif text == "🎁 Daily":
        await daily(update, context)

    elif text == "⚔ Match":
        await match(update, context)

    elif text == "🏆 Leaderboard":
        await leaderboard(update, context)

# =========================================
# MAIN
# =========================================

TOKEN = "8893932606:AAF0OEPfScrIDXTOVH56tb_jyW1Yg2gxNx0"

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.TEXT, buttons))

print("🔥 Gaming Bot Running...")
app.run_polling()