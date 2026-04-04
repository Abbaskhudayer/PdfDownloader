from pathlib import Path

BASE_URL = "https://sys9-newton.lms.nodehill.se/"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "logs"

HEADLESS = False
SLOW_MO_MS = 100
NAVIGATION_TIMEOUT_MS = 30000
WAIT_AFTER_LOAD_MS = 1500

PDF_FORMAT = "A4"
PDF_PRINT_BACKGROUND = True

# Justeras senare när du har inspekterat sidan
ARTICLE_CARD_SELECTOR = "a"
ARTICLE_TITLE_SELECTORS = [
    "h1",
    "main h1",
    "article h1",
    "[role='main'] h1"
]