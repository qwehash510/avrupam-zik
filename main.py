import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL
from config import API_ID, API_HASH, BOT_TOKEN

# SES DOSYA KAYIT LOKASYONU
DOWNLOADS = "downloads"
if not os.path.exists(DOWNLOADS):
    os.makedirs(DOWNLOADS)

bot = Client(
    "iso_music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

call = PyTgCalls(bot)
queues = {}

ytdl_opts = {
    "format": "bestaudio",
    "outtmpl": f"{DOWNLOADS}/%(title)s.%(ext)s",
    "quiet": True,
    "noplaylist": True
}

def download_audio(query):
    with YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)["entries"][0]
        file = ydl.prepare_filename(info)
        title = info.get("title", "Unknown")
    return file, title

@bot.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    text = """✨ **ISO. MUSIC BOT** 🎧

📌 Sesli sohbette müzik çalar

🎵  /play şarkı adı  
⏸  /pause  
▶   /resume  
⏭  /skip  
⏹  /stop  
📜  /queue  
👋  /leave
"""
    await message.reply(text)

@bot.on_message(filters.command("play"))
async def play_music(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ **Şarkı adı yaz!**")

    query = message.text.split(None,1)[1]
    loading = await message.reply("🔎 **Aranıyor...**")

    file, title = download_audio(query)
    chat_id = message.chat.id

    if chat_id not in queues:
        queues[chat_id] = []

    queues[chat_id].append((file,title))

    if len(queues[chat_id]) == 1:
        await call.join_group_call(chat_id, AudioPiped(file))
        await loading.edit_text(f"🎶 **Çalıyor:** `{title}`")
    else:
        await loading.edit_text(f"📥 **Queue'ya eklendi:** `{title}`")

@bot.on_message(filters.command("skip"))
async def skip_music(client, message: Message):
    chat_id = message.chat.id

    if chat_id not in queues or len(queues[chat_id]) < 2:
        return await message.reply("⚠️ **Atlanacak şarkı yok!**")

    queues[chat_id].pop(0)
    next_file, next_title = queues[chat_id][0]

    await call.change_stream(chat_id, AudioPiped(next_file))
    await message.reply(f"⏭ **Atlandı! Şimdi:** `{next_title}`")

@bot.on_message(filters.command("pause"))
async def pause_music(client, message: Message):
    await call.pause_stream(message.chat.id)
    await message.reply("⏸️ **Müzik duraklatıldı!**")

@bot.on_message(filters.command("resume"))
async def resume_music(client, message: Message):
    await call.resume_stream(message.chat.id)
    await message.reply("▶️ **Müzik devam ediyor!**")

@bot.on_message(filters.command("stop"))
async def stop_music(client, message: Message):
    chat_id = message.chat.id
    queues[chat_id] = []
    await call.leave_group_call(chat_id)
    await message.reply("⏹️ **Müzik durduruldu!**")

@bot.on_message(filters.command("queue"))
async def show_queue(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in queues or not queues[chat_id]:
        return await message.reply("📭 **Queue boş!**")
    text = "📜 **Queue Listesi:**\n\n"
    for i, (_, title) in enumerate(queues[chat_id]):
        text += f"{i+1}. `{title}`\n"
    await message.reply(text)

@bot.on_message(filters.command("leave"))
async def leave_group(client, message: Message):
    await call.leave_group_call(message.chat.id)
    await message.reply("👋 **Sohbetten ayrıldım!**")

async def main():
    await bot.start()
    print("✅ ISO. MUSIC BOT AKTİF")
    await asyncio.Event().wait()

asyncio.run(main())
