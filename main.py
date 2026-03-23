import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp
from googleapiclient.discovery import build

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
YOUTUBE_API_KEY = os.environ.get("AIzaSyDreCejh0Rl0w5jpwvhqqLCTZEOWB2YpZA")
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎵 <b>Hoşgeldin!</b>\n\n"
        "Ben bir <i>Telegram Müzik Botu</i>yım. 💿\n\n"
        "🔹 Kullanımı:\n"
        "1️⃣ /play <i>Sanatçı - Şarkı</i> → Şarkıyı arayıp gönderirim.\n"
        "2️⃣ Büyük dosyalar gönderilemiyorsa uyarı alırsınız.\n\n"
        "💡 Developer: @voidsafarov"
    )
    await update.message.reply_html(welcome_text)

# Video ID arama
def search_youtube(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part="id",
        type="video",
        maxResults=1
    )
    response = request.execute()
    items = response.get("items")
    if items:
        return "https://www.youtube.com/watch?v=" + items[0]["id"]["videoId"]
    return None

# /play komutu
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text(
            "❌ Lütfen bir şarkı ismi girin.\nÖrnek: /play Imagine Dragons - Believer"
        )
        return

    song_query = " ".join(context.args)
    msg = await update.message.reply_text(f"⏳ '{song_query}' aranıyor, lütfen bekleyin...")

    try:
        video_url = search_youtube(song_query)
        if not video_url:
            await msg.edit_text("❌ Şarkı bulunamadı. Lütfen başka bir isim deneyin.")
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get("title", "Unknown")
            uploader = info.get("uploader", "Unknown")
            duration = info.get("duration", 0)

        file_size = os.path.getsize(filename)
        if file_size > MAX_FILE_SIZE:
            await msg.edit_text("❌ Dosya çok büyük! Maksimum 2GB.")
            os.remove(filename)
            return

        await update.message.reply_audio(
            audio=open(filename, "rb"),
            title=title,
            performer=uploader
        )
        await msg.edit_text(f"✅ Şarkı gönderildi: {title} ({duration//60}dk {duration%60}sn)")
        os.remove(filename)

    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
        await msg.edit_text("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    print("Bot başlatıldı... Developer: @voidsafarov")
    app.run_polling()
