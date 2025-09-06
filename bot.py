import os
import requests
import yt_dlp
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render → Environment Variable me set karo
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

# ✅ Home route
@app.route("/", methods=["GET"])
def home():
    return "✅ Telegram Instagram Downloader Bot is running on Render!"

# ✅ Webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if not update:
        return {"ok": False}

    print("📩 Update received:", update)

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # /start command
        if text == "/start":
            send_message(chat_id, "👋 Hello! Send me any *public Instagram reel/post link* and I'll download it for you.")
        
        # Instagram link handler
        elif text.startswith("http") and "instagram.com" in text:
            send_message(chat_id, "⏳ Downloading your Instagram video... Please wait.")

            video_path = download_instagram_video(text)
            if video_path:
                send_video(chat_id, video_path)
                os.remove(video_path)  # cleanup
            else:
                send_message(chat_id, "❌ Failed to download. Maybe it's private?")
        
        else:
            send_message(chat_id, "⚡ Please send a valid Instagram link.")

    return {"ok": True}

# ✅ Send message
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print("❌ Error sending message:", e)

# ✅ Send video
def send_video(chat_id, video_path):
    url = f"{BASE_URL}/sendVideo"
    try:
        with open(video_path, "rb") as video:
            requests.post(url, data={"chat_id": chat_id}, files={"video": video})
    except Exception as e:
        print("❌ Error sending video:", e)

# ✅ yt-dlp Download Function
def download_instagram_video(url):
    try:
        ydl_opts = {
            "outtmpl": "downloaded.%(ext)s",
            "format": "mp4",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print("❌ Download error:", e)
        return None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
