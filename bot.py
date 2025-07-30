import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import re

# Get secrets from environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")

app = Client("yt_downloader_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "👋 Welcome to *YouTube Downloader Bot!*\n\n"
        "📥 Just send me any YouTube link and choose MP3 or MP4 to download.",
        quote=True
    )
@app.on_message(filters.text & filters.private)
async def handle_link(client, message):
    url = message.text.strip()

    if "youtu" not in url:
        return await message.reply("❌ Please send a valid YouTube video link.")

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎵 Download MP3", callback_data=f"mp3|{url}"),
        InlineKeyboardButton("🎥 Download MP4", callback_data=f"mp4|{url}")
    ]])

    await message.reply("👇 Choose format:", reply_markup=keyboard)
@app.on_callback_query()
async def callback(client, callback_query):
    format_type, url = callback_query.data.split("|", 1)
    msg = await callback_query.message.reply("⏬ Downloading... Please wait.")

    if "youtube.com/shorts/" in url:
        match = re.findall(r"shorts/([a-zA-Z0-9_-]{11})", url)
        if match:
            url = f"https://youtube.com/watch?v={match[0]}"

    output = "file.mp3" if format_type == "mp3" else "file.mp4"
    ydl_opts = {
        "outtmpl": output,
        "format": "bestaudio/best" if format_type == "mp3" else "bestvideo+bestaudio/best",
        "quiet": True,
        "noplaylist": True
    }

    if format_type == "mp3":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await client.send_document(callback_query.message.chat.id, document=output)
        os.remove(output)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Failed:\n`{str(e)}`")

app.run()
