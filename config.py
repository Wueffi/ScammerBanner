import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Add it to your .env file.")

LOGS_CHANNEL_ID: int = os.getenv("LOGS_CHANNEL_ID", 0)

TEMPBAN_ROLE_NAME: str = os.getenv("TEMPBAN_ROLE_NAME", "Temporarily Banned")

TEMPBAN_CHANNEL_NAME: str = os.getenv("TEMPBAN_CHANNEL_NAME", "🔒get-access-back")

TEMPBAN_ROLE_COLOUR: int = int(os.getenv("TEMPBAN_ROLE_COLOUR", "0xC0392B"), 16)

TEMPBAN_CHANNEL_WELCOME: str = os.getenv(
    "TEMPBAN_CHANNEL_WELCOME",
    (
        "If you are reading this, **you have been temporarily restricted!**\n\n"
        "Your access to the rest of this server has been suspended. Please confirm you are not a bot by clicking the button below."
    ),
)