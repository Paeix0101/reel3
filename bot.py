import os
import requests
import yt_dlp
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render pe env var me set karna
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

# ✅ Home route
@app.route("/", methods=["GET"])
def home():
    return "✅ Telegram Bot is running!"


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
            send_message(chat_id, "👋 Send me a public Instagram Reels link and I will download it for you.")
        elif "instagram.com/reel" in text:
            send_message(chat_id, "⏳ Downloading your reel... Please wait.")
            video_path = download_instagram_reel(text)
            if video_path:
                send_video(chat_id, video_path)
                os.remove(video_path)  # clean up after sending
            else:
                send_message(chat_id, "❌ Failed to download. Make sure it's a *public* reel link.")
        else:
            send_message(chat_id, "⚠️ Please send a valid Instagram Reel link.")

    return {"ok": True}


# ✅ Helper function: send text
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("❌ Error sending message:", e)


# ✅ Helper function: send video
def send_video(chat_id, video_path):
    url = f"{BASE_URL}/sendVideo"
    try:
        with open(video_path, "rb") as video:
            requests.post(url, data={"chat_id": chat_id}, files={"video": video})
    except Exception as e:
        print("❌ Error sending video:", e)


# ✅ Download Instagram reel using yt-dlp
def download_instagram_reel(url):
    output_path = "reel.mp4"
    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4[height<=720]",  # max 720p
        "quiet": True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path
    except Exception as e:
        print("❌ Error downloading reel:", e)
        return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
