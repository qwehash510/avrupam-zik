import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Başlatma ve kullanım paneli
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎬 <b>Link / Video Downloader Bot</b>\n\n"
        "📌 Kullanım Paneli:\n"
        "/download <i>link</i> - Video / MP4 indirir\n"
        "/help - Komutları gösterir\n\n"
        "💡 Developer: @voidsafarov"
    )
    await update.effective_message.reply_html(text)

# Yardım komutu
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🛠️ <b>Komutlar</b>\n"
        "/download <i>link</i> - Video indirir ve chat'e gönderir\n"
        "/help - Bu paneli gösterir\n\n"
        "💡 Developer: @voidsafarov"
    )
    await update.effective_message.reply_html(text)

# Video indirme
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("❌ Lütfen bir link girin!")
        return

    link = context.args[0]
    msg = await update.effective_message.reply_text(f"🔎 Video aranıyor ve indiriliyor...\n{link}")

    try:
        ydl_opts = {
            "format": "best",
            "outtmpl": "video.%(ext)s",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info)
            title = info.get("title", "Video")
        
        await update.effective_message.reply_video(video=open(file_path, "rb"),
                                                   caption=f"🎬 {title}\n💡 Developer: @voidsafarov")
        await msg.edit_text(f"✅ Video indirildi: {title}")
        os.remove(file_path)

    except Exception as e:
        await msg.edit_text("❌ Bir hata oluştu. Lütfen linki kontrol edin veya farklı bir link deneyin.")
        logging.error(e)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("download", download))
    print("🚀 Link/Video Downloader Bot çalışıyor... Developer: @voidsafarov")
    app.run_polling()
