import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎵 <b>Music Bot</b>\n\n"
        "Kullanım Paneli:\n"
        "/play <i>Şarkı Adı</i> - Şarkıyı çalar\n"
        "/stop - Oynatmayı durdurur\n\n"
        "💡 Developer: @voidsafarov"
    )
    await update.effective_message.reply_html(text)

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("❌ Şarkı ismi yazın.")
        return

    query = " ".join(context.args)
    msg = await update.effective_message.reply_text(f"🔎 Şarkı aranıyor: {query}")

    try:
        search_url = f"https://itunes.apple.com/search?term={query}&limit=1"
        res = requests.get(search_url, timeout=10).json()
        if not res["results"]:
            await msg.edit_text("❌ Şarkı bulunamadı.")
            return

        track = res["results"][0]
        preview_url = track.get("previewUrl")
        title = track.get("trackName")
        artist = track.get("artistName")

        audio = requests.get(preview_url, timeout=10)
        with open("song.mp3", "wb") as f:
            f.write(audio.content)

        await update.effective_message.reply_audio(audio=open("song.mp3", "rb"), 
                                                   caption=f"🎵 {artist} - {title}")
        os.remove("song.mp3")
        await msg.edit_text(f"✅ Şarkı gönderildi: {artist} - {title}")
    except Exception as e:
        await msg.edit_text("❌ Bir hata oluştu.")
        print(e)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("⏹️ Oynatma durduruldu.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("stop", stop))
    print("Bot çalışıyor... Developer: @voidsafarov")
    app.run_polling()
