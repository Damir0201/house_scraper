import os
import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest
from src.database import add_user, get_all_users, get_latest_tracks

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8798214070:AAG9jE_HPrWLnNx0hwnuUgy-BOOiD66TaFQ")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    add_user(chat_id)
    await update.message.reply_text("Special for ghost producers")


async def tracks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tracks = get_latest_tracks(limit=5)

    if not tracks:
        await update.message.reply_text("Nothing new uploaded")
        return

    message = "Последние треки:\n\n"
    for track in tracks:
        message += f"• [{track['title']}]({track['track_url']}) — {track['price']}\n"

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


async def send_broadcast_notifications(hot_picks, catalog_tracks):
    bot = Bot(token=TELEGRAM_TOKEN)
    users = get_all_users()

    if not users:
        return

    messages = []

    if hot_picks:
        hot_message = "New Hot-Picks: \n\n"
        for track in hot_picks:
            hot_message += f"• [{track['title']}]({track['track_url']}) — {track['price']}\n"
        messages.append(hot_message)

    if catalog_tracks:
        for i in range(0, len(catalog_tracks), 10):
            chunk = catalog_tracks[i:i + 10]
            catalog_message = "New releases: \n\n"
            for track in chunk:
                catalog_message += f"• [{track['title']}]({track['track_url']}) — {track['price']}\n"
            messages.append(catalog_message)

    for chat_id in users:
        for msg in messages:
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=msg,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Error on sending message {chat_id}: {e}")


def run_bot_listener():
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("tracks", tracks_command))
    print("Bot working...")
    app.run_polling()