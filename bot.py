import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")

app = Client("yt_downloader_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("👋 Send me any YouTube link and I’ll give you download options (MP3/MP4).")

@app.on_message(filters.regex(r'^https?://(www\.)?(youtube\.com|youtu\.be)'))
async def handle_yt_link(client, message):
    url = message.text
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎵 Download MP3", callback_data=f"mp3|{url}"),
        InlineKeyboardButton("🎥 Download MP4", callback_data=f"mp4|{url}")
    ]])
    await message.reply("Choose format:", reply_markup=keyboard)
@app.on_callback_query()
async def callback(client, callback_query):
    format_type, url = callback_query.data.split("|", 1)
    msg = await callback_query.message.reply("⏬ Downloading...")

    out_file = "download.mp3" if format_type == "mp3" else "download.mp4"

    ydl_opts = {
        "outtmpl": out_file,
        "format": "bestaudio/best" if format_type == "mp3" else "bestvideo+bestaudio/best",
    }

    if format_type == "mp3":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await client.send_document(
            chat_id=callback_query.message.chat.id,
            document=out_file,
            caption=f"✅ Here is your {format_type.upper()} file",
        )
        os.remove(out_file)
        await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ Failed: {e}")

app.run()
