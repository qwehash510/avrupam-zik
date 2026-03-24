import logging
import sqlite3
import time
from collections import defaultdict
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "YOUR_BOT_TOKEN"

# ===== DATABASE =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    chat_id INTEGER,
    warns INTEGER DEFAULT 0
)
""")
conn.commit()

# ===== AYARLAR =====
BAD_WORDS = ["salak", "aptal", "mal", "gerizekalı"]
FLOOD_LIMIT = 5
FLOOD_TIME = 5

user_messages = defaultdict(list)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🛡️ <b>VOID KORUMA BOT</b>\n\n"
        "✨ <b>Özellikler:</b>\n"
        "• 🚫 Küfür engelleme\n"
        "• 🔗 Link koruma\n"
        "• ⚡ Flood sistemi\n"
        "• 📊 Warn sistemi (3 = ban)\n\n"
        "📌 <b>Komutlar:</b>\n"
        "• /panel\n"
        "• /warn\n"
        "• /unwarn\n"
        "• /ban\n"
        "• /mute\n\n"
        "👨‍💻 <b>Developer:</b> @voidsafarov"
    )
    await update.message.reply_html(text)

# ===== PANEL =====
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⚙️ <b>𝗬𝗢𝗡𝗘𝗧𝗜𝗠 𝗣𝗔𝗡𝗘𝗟𝗜</b>\n\n"
        "🔨 /ban → Kullanıcıyı banla\n"
        "🔇 /mute → Sustur\n"
        "⚠️ /warn → Uyarı ver\n"
        "♻️ /unwarn → Uyarı sil\n\n"
        "💡 3 warn = otomatik ban"
    )
    await update.message.reply_html(text)

# ===== WELCOME =====
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.new_chat_members[0]
    await update.message.reply_html(
        f"👋 <b>Hoş geldin {user.first_name}!</b>\n\n"
        "🛡️ Kurallar aktif, dikkatli ol 😉"
    )

# ===== WARN =====
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id

    cursor.execute("SELECT warns FROM users WHERE user_id=? AND chat_id=?", (user.id, chat_id))
    row = cursor.fetchone()

    if row:
        warns = row[0] + 1
        cursor.execute("UPDATE users SET warns=? WHERE user_id=? AND chat_id=?", (warns, user.id, chat_id))
    else:
        warns = 1
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user.id, chat_id, warns))

    conn.commit()

    if warns >= 3:
        await context.bot.ban_chat_member(chat_id, user.id)
        await update.message.reply_html(
            f"🚫 <b>{user.first_name} banlandı!</b>\nSebep: 3 warn"
        )
    else:
        await update.message.reply_html(
            f"⚠️ <b>{user.first_name}</b> uyarıldı!\n"
            f"Warn: <b>{warns}/3</b>"
        )

# ===== UNWARN =====
async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id

    cursor.execute("UPDATE users SET warns=0 WHERE user_id=? AND chat_id=?", (user.id, chat_id))
    conn.commit()

    await update.message.reply_html("♻️ Uyarılar sıfırlandı")

# ===== BAN =====
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.message.chat_id, user.id)

    await update.message.reply_html(f"🔨 <b>{user.first_name} banlandı!</b>")

# ===== MUTE =====
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user

    await context.bot.restrict_chat_member(
        update.message.chat_id,
        user.id,
        permissions=ChatPermissions(can_send_messages=False)
    )

    await update.message.reply_html(f"🔇 <b>{user.first_name} susturuldu!</b>")

# ===== MESAJ KONTROL =====
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user_id = msg.from_user.id
    text = msg.text.lower() if msg.text else ""

    # Küfür
    for word in BAD_WORDS:
        if word in text:
            await msg.delete()
            return

    # Link
    if "http://" in text or "https://" in text:
        await msg.delete()
        return

    # Flood
    now = time.time()
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < FLOOD_TIME]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > FLOOD_LIMIT:
        await context.bot.restrict_chat_member(
            msg.chat_id,
            user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=int(now + 60)
        )
        await msg.reply_html("🚫 <b>Spam yasak!</b> 1 dk susturuldun")

# ===== BOT =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("unwarn", unwarn))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("🛡️ PRO Koruma Botu aktif! Developer: @voidsafarov")
    app.run_polling()
