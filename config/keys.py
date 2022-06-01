from loguru import logger
from dotenv import load_dotenv
from pyngrok import ngrok
import os

load_dotenv()

ENV_TYPE = os.getenv('ENV_TYPE')
IS_PRODUCTION = ENV_TYPE == 'PRODUCTION'

TELEGRAM_BOT_API_TOKEN = os.getenv(
    "PRODUCTION_BOT_TOKEN") if IS_PRODUCTION else os.getenv("DEVELOPMENT_BOT_TOKEN")

PORT = int(os.getenv("PORT"))
HOST = os.getenv("HOST")

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
if not WEBHOOK_HOST:
    WEBHOOK_HOST = ngrok.connect(PORT, "http").public_url
    logger.warning(
        f"WEBHOOK_HOST not found in .env, initializing ngrok tunnel at: {WEBHOOK_HOST}"
    )
WEBHOOK_URL_BASE = (
    f"https://{WEBHOOK_HOST.split('//')[1]}"
    if WEBHOOK_HOST.startswith("http")
    else WEBHOOK_HOST
)
WEBHOOK_URL_PATH = f"/{TELEGRAM_BOT_API_TOKEN}/"
