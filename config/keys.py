from loguru import logger
from dotenv import load_dotenv
from pyngrok import ngrok
import os

load_dotenv()

TELEGRAM_BOT_API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
PORT = int(os.getenv("PORT"))
HOST = os.getenv("HOST")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
if not WEBHOOK_HOST:
    WEBHOOK_HOST = ngrok.connect(PORT, "http").public_url
    logger.warning(f"WEBHOOK_HOST not found in .env, initializing ngrok tunnel at: {WEBHOOK_HOST}")
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST.split('//')[1]}"
WEBHOOK_URL_PATH = f"/{TELEGRAM_BOT_API_TOKEN}/"
