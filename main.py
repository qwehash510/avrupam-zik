import os
import asyncio
from pytube import YouTube
from telegram import Update, InputMediaAudio
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from mutagen.mp3 import MP3
from PIL import Image
import logging

# Logging ayarı
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

BOT_TOKEN = os.environ.get("8746073140:AAE6up6COUFccy9OIVqImDDY_HM_cDxaRHg")
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB Telegram limiti

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎶 <b>Hoşgeldin!</b>\n\n"
        "Ben bir <i>Telegram Müzik Botu</i>yım. 💿\n"
        "Komutlarım:\n"
        "1️⃣ /play <i>YouTube linki</i> → Şarkıyı indirir ve gönderirim.\n"
        "2️⃣ Büyük dosyalar gönderilemiyorsa uyarı alırsınız.\n\n"
        "💡 Developer: @voidsafarov"
    )
    await update.message.reply_html(welcome_text)

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Lütfen bir YouTube linki girin.\nÖrnek: /play https://youtu.be/...")
        return

    url = context.args[0]
    msg = await update.message.reply_text("⏳ Şarkınız hazırlanıyor, lütfen bekleyin...")

    try:
        yt = YouTube(url)
        title = yt.title
        length = yt.length  # saniye
        stream = yt.streams.filter(only_audio=True).first()
        temp_file = f"{title}.mp4"

        stream.download(filename=temp_file)

        file_size = os.path.getsize(temp_file)
        if file_size > MAX_FILE_SIZE:
            await msg.edit_text("❌ Dosya çok büyük! Maksimum 2GB.")
            os.remove(temp_file)
            return

        # mp3 olarak gönder
        await update.message.reply_audio(audio=open(temp_file, 'rb'), title=title)
        await msg.edit_text(f"✅ Şarkı gönderildi: {title} ({length//60}dk {length%60}sn)")

        os.remove(temp_file)

    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
        await msg.edit_text(f"❌ Bir hata oluştu: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))

    print("Bot başlatıldı... Developer: @voidsafarov")
    app.run_polling()
