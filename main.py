import os
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "🎵 Müzik Botu Hazır!\n\n"
        "Kullanım:\n"
        "/play Eminem - Mockingbird\n\n"
        "💡 Developer: @voidsafarov"
    )

# Şarkı bul + indir
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("❌ Şarkı ismi yaz.")
        return

    query = " ".join(context.args)
    msg = await update.effective_message.reply_text("🔎 Şarkı aranıyor...")

    try:
        # iTunes API (çok stabil)
        search_url = f"https://itunes.apple.com/search?term={query}&limit=1"
        res = requests.get(search_url).json()

        if not res["results"]:
            await msg.edit_text("❌ Şarkı bulunamadı.")
            return

        track = res["results"][0]
        preview_url = track.get("previewUrl")

        if not preview_url:
            await msg.edit_text("❌ Şarkı bulunamadı.")
            return

        title = track.get("trackName")
        artist = track.get("artistName")

        await msg.edit_text(f"⬇️ İndiriliyor: {artist} - {title}")

        audio = requests.get(preview_url)

        with open("song.mp3", "wb") as f:
            f.write(audio.content)

        await update.effective_message.reply_audio(
            audio=open("song.mp3", "rb"),
            title=title,
            performer=artist
        )

        os.remove("song.mp3")
        await msg.edit_text(f"✅ Gönderildi: {artist} - {title}")

    except Exception as e:
        logging.error(e)
        await msg.edit_text("❌ Bir hata oluştu.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))

    print("Bot çalışıyor... Developer: @voidsafarov")
    app.run_polling()
