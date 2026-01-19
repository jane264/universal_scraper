import os
from dotenv import load_dotenv

load_dotenv()

MAX_PAGES = int(os.getenv("MAX_PAGES", 20))
STATIC_SCORE_THRESHOLD = int(os.getenv("STATIC_SCORE_THRESHOLD", 4000))
DOMINANCE_RATIO = float(os.getenv("DOMINANCE_RATIO", 1.15))

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 15))
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

FIELD_MAP = {
    "Text Content": "text",
    "Links": "href",
    "Images": "src"
}
