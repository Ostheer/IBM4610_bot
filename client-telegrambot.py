import logging
import requests
from io import BytesIO
from threading import Lock
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

import os

# === Configuration ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_USER_ID = int(os.environ["BOT_ADMIN"])
BACKEND_PASS = os.environ["SUREMARK_SECRET"]
_BACKEND_ADDR = os.environ.get("SUREMARK_BACKEND_ADDRESS", "localhost")
BACKEND_URL = f"http://{_BACKEND_ADDR}:8000/chat"
AUTH_FILE = "authorized_users.txt"

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Authorization State ===
auth_lock = Lock()
authorized_users = set()

# Load existing authorized users from file
if os.path.exists(AUTH_FILE):
    with open(AUTH_FILE, "r") as f:
        for line in f:
            authorized_users.add(int(line.strip()))

def save_authorized_user(user_id: int):
    with auth_lock:
        if user_id not in authorized_users:
            with open(AUTH_FILE, "a") as f:
                f.write(f"{user_id}\n")
            authorized_users.add(user_id)

# === Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authorized_users:
        await update.message.reply_text("Goeiedag, wat is het wachtwoord?")
        context.user_data['awaiting_password'] = True
    else:
        await update.message.reply_text("Jou kenne we al")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message

    # Awaiting password?
    if context.user_data.get('awaiting_password'):
        if message.text.strip() == BACKEND_PASS:
            save_authorized_user(user_id)
            context.user_data['awaiting_password'] = False
            await message.reply_text("Yess lekker man.")
        else:
            await message.reply_text("Dat is niet helemaal wat ik verwacht had.")
        return

    # If not authenticated
    if user_id not in authorized_users:
        await message.reply_text("Ge moet ff inloggen. Doe es /start.")
        return

    # Notify admin
    try:
        username = update.effective_user.username or update.effective_user.full_name or f"User {user_id}"
        if user_id != ADMIN_USER_ID:
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=f"📩 {username} heeft u een fax gestuurd."
            )
    except Exception as e:
        logger.warning(f"Failed to notify admin: {e}")

    # Prepare multipart request
    files = {}
    data = {}

    if message.photo:
        largest_photo = message.photo[-1]

        file = await context.bot.get_file(largest_photo.file_id)
        file_bytes = BytesIO()
        await file.download_to_memory(out=file_bytes)
        file_bytes.seek(0)

        files['file'] = ('image.jpg', file_bytes, 'image/jpeg')
        data['text'] = message.caption or ""
    elif message.sticker:
        file = await context.bot.get_file(message.sticker.file_id)
        file_bytes = BytesIO()
        await file.download_to_memory(out=file_bytes)
        file_bytes.seek(0)

        files['file'] = ('sticker.webp', file_bytes, "image/webp")
        data['text'] = ""
    elif message.text:
        data['text'] = message.text
    else:
        await message.reply_text("Doe ff normaal man, stuur gewoon tekst of prent.")
        return

    headers = {
        "Authorization": BACKEND_PASS
    }

    try:
        response = requests.post(
            BACKEND_URL,
            headers=headers,
            data=data,
            files=files if files else None,
            timeout=10
        )
        if response.ok:
            await message.reply_text("Uw bonnetje is onderweges.")
        else:
            await message.reply_text("Godverdomme het is helemaal kapot. Sorry man.")
    except Exception as e:
        logger.exception(f"Error sending request to backend. {type(e).__name__}: {e}.")
        await message.reply_text("Lol nu is het echt stuk")

# === Main Application ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_message))

    app.run_polling()

