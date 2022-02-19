from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
PORT = int(os.getenv("PORT"))
HOST = os.getenv("HOST")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}"
WEBHOOK_URL_PATH = f"/{TELEGRAM_BOT_API_TOKEN}/"
