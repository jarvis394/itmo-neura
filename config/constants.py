from pathlib import Path
import os


"""
Interval for generating a random sentence
"""
RANDOM_MESSAGE_SEND_INTERVAL = 3600 * 3

"""
Interval for flushing messages to the storage
"""
MESSAGES_FLUSH_INTERVAL = 30

"""
Bot's prefix
"""
BOT_PREFIX = "/"

"""
Bot's mention prefix
"""
BOT_MENTION_PREFIX = "@itmo_neura_bot"

"""
Path for directory of the project. Used to locate storage folders
"""
ROOT_DIR = Path(__file__).parent.parent

"""
Path for directory of messages samples
"""
MESSAGES_SAMPLES_DIR = os.path.join(ROOT_DIR, "messages")
