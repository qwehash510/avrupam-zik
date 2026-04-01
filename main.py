import os
import requests
from telethon import TelegramClient, events, Button

# ---------------- AYARLAR ----------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN"))

# Grup reklamı
GROUP_LINK = "https://t.me/vxtikan"

# ---------------- TELETHON CLIENT ----------------
client = TelegramClient("instabot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ---------------- YARDIMCI FONKSİYONLAR ----------------
def is_instagram(url):
    return "instagram.com" in url

def download_instagram(url):
    """
    Basit bir API kullanımı ile Instagram linkinden video veya fotoğraf indirir.
    Burada örnek olarak 'https://api.instagram.com/oembed/?url={url}' kullanılabilir.
    Daha güvenilir seçenekler: InstaDownloader API veya instaloader.
    """
    try:
        # Örnek: InstaDownloader API
        api_url = f"https://api-instagram-downloader.com/?url={url}"
        r = requests.get(api_url).json()
        if r.get("status") != "success":
            return None
        return r.get("media_url")
    except:
        return None

def usage_text():
    return (
        "✨ *Merhaba! Instagram Downloader Bot’a Hoşgeldiniz!* ✨\n\n"
        "📌 Bu bot sayesinde Instagram video ve fotoğraflarını kolayca indirebilirsiniz.\n\n"
        f"📣 Eğer grubumuza katılırsanız çok seviniriz: [Katılmak İçin Tıkla]({GROUP_LINK})\n\n"
        "📌 *Kullanım Adımları:*\n"
        "1️⃣ Instagram paylaşım linkini kopyala\n"
        "2️⃣ Bu linki bot’a gönder\n"
        "3️⃣ Bot size video veya fotoğrafı gönderecek\n\n"
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

# ---------------- INSTAGRAM MESAJLARI ----------------
@client.on(events.NewMessage)
async def handler(event):
    if event.out:
        return

    text = event.raw_text
    if is_instagram(text):
        msg = await event.reply("⏳ Instagram içerik indiriliyor, lütfen bekleyin...")
        media_url = download_instagram(text)
        if not media_url:
            await msg.edit("❌ İçerik indirilemedi, linki kontrol edin!")
            return
        await msg.edit("✅ İçerik hazır, gönderiliyor...")
        await client.send_file(event.chat_id, media_url, caption="📸 Instagram İçerik")
        await msg.delete()
    else:
        if not text.startswith("/start") and not text.startswith("/help"):
            await event.reply("📎 Lütfen geçerli bir Instagram paylaşım linki gönderin!")

# ---------------- RUN ----------------
print("🤖 Instagram Bot çalışıyor...")
client.run_until_disconnected()
