from pathlib import Path
import os

BOT_ID = 5023321394
"""
Bot ID
"""

RANDOM_MESSAGE_SEND_INTERVAL = 3600 * 3
"""
Interval for generating a random sentence
"""

MESSAGES_FLUSH_INTERVAL = 30
"""
Interval for flushing messages to the storage
"""

BOT_PREFIX = "/"
"""
Bot's prefix
"""

BOT_MENTION_PREFIX = "@itmo_neura_bot"
"""
Bot's mention prefix
"""

ROOT_DIR = Path(__file__).parent.parent
"""
Path for directory of the project. Used to locate storage folders
"""

MESSAGES_SAMPLES_DIR = os.path.join(ROOT_DIR, "messages")
"""
Path for directory of messages samples
"""
