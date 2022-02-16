from pathlib import Path
import os


RANDOM_MESSAGE_SEND_INTERVAL = 3600 * 3
BOT_PREFIX = "/"
BOT_MENTION_PREFIX = "@itmo_neura_bot"
ROOT_DIR = Path(__file__).parent.parent
MESSAGES_MODELS_DIR = os.path.join(ROOT_DIR, "messages")
