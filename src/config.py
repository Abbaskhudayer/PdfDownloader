from pathlib import Path  # Importerar Path för att hantera filsökvägar på ett plattformsoberoende sätt

BASE_URL = "https://sys9-newton.lms.nodehill.se/"  # Bas-URL till NodeHill-webbplatsen som skrapas

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # Beräknar projektets rotkatalog baserat på denna fils placering
OUTPUT_DIR = PROJECT_ROOT / "output"  # Katalog där de exporterade PDF-filerna sparas
LOG_DIR = PROJECT_ROOT / "logs"  # Katalog där loggfiler sparas

HEADLESS = False  # Styr om webbläsaren körs utan grafiskt gränssnitt (False = synlig webbläsare)
SLOW_MO_MS = 100  # Fördröjning i millisekunder mellan Playwright-åtgärder för stabilitet
NAVIGATION_TIMEOUT_MS = 30000  # Maximal väntetid i millisekunder för sidnavigering
WAIT_AFTER_LOAD_MS = 1500  # Extra väntetid i millisekunder efter att en sida laddats klart

PDF_FORMAT = "A4"  # Sidformat för exporterade PDF-filer
PDF_PRINT_BACKGROUND = True  # Anger om bakgrundsbilder och -färger ska inkluderas i PDF:en

# Samla fortfarande artikellänkar från startsidan
ARTICLE_CARD_SELECTOR = "a"  # CSS-selektor för att hitta artikellänkar på startsidan

# NodeHill-selectors vi hittade i DevTools
ARTICLE_CONTAINER_SELECTOR = ".article-page.main-content-anim"  # CSS-selektor för artikelns container-element
ARTICLE_TITLE_SELECTOR = "#article-title-text"  # CSS-selektor för artikelns rubrikelement
ARTICLE_BODY_SELECTOR = "#markdown-text"  # CSS-selektor för artikelns innehållselement

REMOVE_SELECTORS = [  # Lista med CSS-selektorer för element som ska tas bort från artikeln
    ".prev-next-links",  # Navigeringslänkar till föregående/nästa artikel
    ".favorites-button",  # Knapp för att markera som favorit
]