import os
import requests
from telethon import TelegramClient, events, Button
import instaloader

# ---------------- AYARLAR ----------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Grup reklamı
GROUP_LINK = "https://t.me/vxtikan"

# ---------------- TELETHON CLIENT ----------------
client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ---------------- INSTALOADER ----------------
L = instaloader.Instaloader(
    download_videos=True,
    download_video_thumbnails=False,
    download_comments=False,
    save_metadata=False,
    post_metadata_txt_pattern=""
)

# ---------------- YARDIMCI FONKSİYONLAR ----------------
def is_tiktok(url):
    return "tiktok.com" in url

def download_tiktok(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        api = f"https://tikwm.com/api/?url={url}"
        r = requests.get(api, headers=headers, timeout=15).json()
        if r.get("code") != 0:
            return None, None
        return r["data"]["play"], r["data"]["music"]
    except:
        return None, None

def download_instagram(url):
    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Video
        if post.is_video:
            return [post.video_url]

        # Fotoğraf veya carousel
        media = []
        if post.typename == "GraphSidecar":
            for node in post.get_sidecar_nodes():
                media.append(node.display_url)
        else:
            media.append(post.url)

        return media
    except Exception as e:
        print("HATA:", e)
        return None

def usage_text():
    return (
        "✨ *Merhaba! TikTok & Instagram Downloader Bot’a Hoşgeldiniz!* ✨\n\n"
        "🎬 TikTok ve Instagram içeriklerini kolayca indirebilirsiniz.\n\n"
        f"📣 Grubumuza katılırsanız çok seviniriz: [Tıkla]({GROUP_LINK})\n\n"
        "📌 *Kullanım Adımları:*\n"
        "1️⃣ TikTok veya Instagram linkini kopyala\n"
        "2️⃣ Bot’a gönder\n"
        "3️⃣ Video ve MP3/fotoğraf olarak al\n\n"
        "🛠 Developer: @primalamazsin"
    )

# ---------------- /START ve /HELP ----------------
@client.on(events.NewMessage(pattern="/start|/help"))
async def start(event):
    if event.out:
        return
    await event.reply(
        usage_text(),
        buttons=[[Button.url("🌟 Gruba Katıl 🌟", GROUP_LINK)]]
    )

# ---------------- MESAJ HANDLER ----------------
@client.on(events.NewMessage)
async def handler(event):
    if event.out:
        return

    text = event.raw_text

    # TikTok
    if is_tiktok(text):
        msg = await event.reply("⏳ TikTok indiriliyor, lütfen bekleyin...")
        video, music = download_tiktok(text)
        if not video:
            await msg.edit("❌ Video indirilemedi, linki kontrol edin!")
            return
        await msg.edit("✅ Video ve ses hazır, gönderiliyor...")
        await client.send_file(event.chat_id, video, caption="🎥 TikTok Video")
        await client.send_file(event.chat_id, music, caption="🎧 TikTok MP3")
        await msg.delete()
        return

    # Instagram
    if "instagram.com" in text:
        msg = await event.reply("⏳ Instagram içerik indiriliyor...")
        media_list = download_instagram(text)
        if not media_list:
            await msg.edit("❌ İçerik indirilemedi! (Hesap gizli olabilir)")
            return
        await msg.edit("✅ İçerik gönderiliyor...")
        for media in media_list:
            await client.send_file(event.chat_id, media)
        await msg.delete()
        return

    # Geçersiz link
    if not text.startswith("/start") and not text.startswith("/help"):
        await event.reply("📎 Lütfen geçerli bir TikTok veya Instagram linki gönderin!")

# ---------------- RUN ----------------
print("🤖 Bot çalışıyor...")
client.run_until_disconnected()
