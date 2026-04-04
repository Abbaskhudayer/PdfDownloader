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

# Samla fortfarande artikellänkar från startsidan
ARTICLE_CARD_SELECTOR = "a"

# NodeHill-selectors vi hittade i DevTools
ARTICLE_CONTAINER_SELECTOR = ".article-page.main-content-anim"
ARTICLE_TITLE_SELECTOR = "#article-title-text"
ARTICLE_BODY_SELECTOR = "#markdown-text"

REMOVE_SELECTORS = [
    ".prev-next-links",
    ".favorites-button",
]