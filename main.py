import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from mutagen.mp3 import MP3
import logging
import yt_dlp

# Logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB Telegram limiti

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎶 <b>Hoşgeldin!</b>\n\n"
        "Ben bir <i>Telegram Müzik Botu</i>yım. 💿\n\n"
        "🔹 Kullanımı çok kolay:\n"
        "1️⃣ /play <i>Şarkı ismi</i> → Şarkıyı arayıp indiririm ve sana gönderirim.\n"
        "2️⃣ Büyük dosyalar gönderilemiyorsa uyarı alırsınız.\n\n"
        "💡 Developer: @voidsafarov"
    )
    await update.message.reply_html(welcome_text)

# /play komutu
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text(
            "❌ Lütfen bir şarkı ismi girin.\nÖrnek: /play Imagine Dragons Believer"
        )
        return

    song_name = " ".join(context.args)
    msg = await update.message.reply_text(f"⏳ '{song_name}' aranıyor ve hazırlanıyor, lütfen bekleyin...")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'ytsearch1',  # şarkı ismi ile arama
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_name, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)

        file_size = os.path.getsize(filename)
        if file_size > MAX_FILE_SIZE:
            await msg.edit_text("❌ Dosya çok büyük! Maksimum 2GB.")
            os.remove(filename)
            return

        await update.message.reply_audio(audio=open(filename, 'rb'), title=title)
        await msg.edit_text(f"✅ Şarkı gönderildi: {title} ({duration//60}dk {duration%60}sn)")

        os.remove(filename)

    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
        await msg.edit_text(
            "❌ Bir hata oluştu. Lütfen şarkı ismini kontrol edin veya farklı bir şarkı deneyin."
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))

    print("Bot başlatıldı... Developer: @voidsafarov")
    app.run_polling()
