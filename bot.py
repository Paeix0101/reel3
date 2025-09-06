import os
import requests
import yt_dlp
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render env variable
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

# ✅ Home route (for testing)
@app.route("/", methods=["GET"])
def home():
    return "✅ Telegram Bot is running on Render!"


# ✅ Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if not update:
        return {"ok": False}

    print("📩 Update received:", update)

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "👋 Hello! Send me a YouTube or Instagram link.")
        elif "youtube.com" in text or "youtu.be" in text:
            handle_youtube(chat_id, text)
        elif "instagram.com/reel" in text or "instagram.com/p" in text:
            handle_instagram(chat_id, text)
        else:
            send_message(chat_id, "⚠️ Please send a valid YouTube or Instagram link.")

    return {"ok": True}


# ✅ Helper: send text message
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("❌ Error sending message:", e)


# ✅ Helper: send video
def send_video(chat_id, video_path):
    url = f"{BASE_URL}/sendVideo"
    try:
        with open(video_path, "rb") as video:
            requests.post(url, data={"chat_id": chat_id}, files={"video": video})
    except Exception as e:
        print("❌ Error sending video:", e)


# ✅ Download YouTube video
def handle_youtube(chat_id, url):
    send_message(chat_id, "⏳ Downloading YouTube video...")
    try:
        ydl_opts = {"outtmpl": "downloads/%(id)s.%(ext)s", "format": "mp4"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        send_video(chat_id, file_path)
    except Exception as e:
        send_message(chat_id, f"❌ Failed to download YouTube video.\n{e}")


# ✅ Download Instagram reel/post
def handle_instagram(chat_id, url):
    send_message(chat_id, "⏳ Downloading Instagram video...")
    try:
        clean_url = url.split("?")[0]  # remove ?igsh=...
        ydl_opts = {"outtmpl": "downloads/%(id)s.%(ext)s", "format": "mp4"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            file_path = ydl.prepare_filename(info)
        send_video(chat_id, file_path)
    except Exception as e:
        send_message(chat_id, f"❌ Failed to download Instagram video.\n{e}")


if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)
    app.run(host="0.0.0.0", port=10000)
