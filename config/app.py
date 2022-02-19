from fastapi import FastAPI
from config.keys import TELEGRAM_BOT_API_TOKEN
import telebot
from config.bot import bot


app = FastAPI()

# Process webhook calls
@app.post(f"/{TELEGRAM_BOT_API_TOKEN}/")
async def process_webhook(update: dict):
    if update:
        update = telebot.types.Update.de_json(update)
        await bot.process_new_updates([update])
    else:
        return
