from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")
PORT = int(os.getenv("PORT"))
HOST = os.getenv("HOST")
