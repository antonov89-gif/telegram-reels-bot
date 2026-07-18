import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_TEXT = os.getenv("GEMINI_MODEL_TEXT", "gemini-1.5-flash")
GEMINI_MODEL_VIDEO = os.getenv("GEMINI_MODEL_VIDEO", "veo-3.0-generate-001")

IG_USER_ID = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")

BOT_ADMIN_ID = os.getenv("BOT_ADMIN_ID")
DEFAULT_NICHE = os.getenv("DEFAULT_NICHE", "бизнес, саморазвитие")
DEFAULT_STYLE = os.getenv("DEFAULT_STYLE", "динамичный, вирусный, вертикальный 9:16, субтитры")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не задан в .env")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не задан в .env")
