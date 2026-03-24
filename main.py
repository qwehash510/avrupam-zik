import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pytgcalls import PyTgCalls
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputAudioStream
from pydub import AudioSegment
import requests

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Başlatma
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎵 <b>Voice Music Bot</b>\n\n"
        "Kullanım Paneli:\n"
        "1️⃣ /play <i>Şarkı Adı</i> → Sesli sohbette çalar\n"
        "2️⃣ /pause → Durdur\n"
        "3️⃣ /resume → Devam ettir\n"
        "4️⃣ /stop → Oynatmayı durdur\n\n"
        "💡 Developer: @voidsafarov"
    )
    await update.effective_message.reply_html(welcome_text)

# Müzik oynatma
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("❌ Şarkı ismi yazın.")
        return

    query = " ".join(context.args)
    msg = await update.effective_message.reply_text(f"🔎 Şarkı aranıyor: {query}")

    try:
        # iTunes API ile preview
        search_url = f"https://itunes.apple.com/search?term={query}&limit=1"
        res = requests.get(search_url, timeout=10).json()

        if not res["results"]:
            await msg.edit_text("❌ Şarkı bulunamadı.")
            return

        track = res["results"][0]
        preview_url = track.get("previewUrl")
        title = track.get("trackName")
        artist = track.get("artistName")

        await msg.edit_text(f"⬇️ İndiriliyor: {artist} - {title}")

        audio = requests.get(preview_url, timeout=10)
        if audio.status_code != 200:
            await msg.edit_text("❌ Şarkı indirilemedi.")
            return

        with open("song.mp3", "wb") as f:
            f.write(audio.content)

        # 15sn ortadan kes (en popüler kısım)
        song = AudioSegment.from_file("song.mp3")
        middle = len(song) // 2
        clip = song[middle - 7500: middle + 7500]  # 15 saniye
        clip.export("best_part.mp3", format="mp3")

        # Sesli chat botu başlat
        app.client = PyTgCalls(context.bot)
        await app.client.start()

        # Grup chat ID (sesli chatte bulunmalı)
        chat_id = update.effective_chat.id

        await app.client.join_group_call(
            chat_id,
            InputAudioStream(
                "best_part.mp3",
                stream_type=StreamType().pulse_stream
            )
        )

        await msg.edit_text(f"✅ Şarkı çalıyor: {artist} - {title}")
        os.remove("song.mp3")
        os.remove("best_part.mp3")

    except Exception as e:
        logging.error(e)
        await msg.edit_text("❌ Bir hata oluştu.")

# Pause / Resume / Stop (temel kontrol)
async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("⏸️ Durduruldu (sesli chat kontrolü eklenebilir)")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("▶️ Devam ettiriliyor (sesli chat kontrolü eklenebilir)")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("⏹️ Oynatma durduruldu (sesli chat kontrolü eklenebilir)")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("pause", pause))
    app.add_handler(CommandHandler("resume", resume))
    app.add_handler(CommandHandler("stop", stop))

    print("Voice Music Bot çalışıyor... Developer: @voidsafarov")
    app.run_polling()
