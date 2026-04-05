import asyncio  # Importerar asyncio för att köra asynkron kod
from playwright.async_api import async_playwright  # Importerar Playwright för webbläsarautomation
import config  # Importerar konfigurationsinställningar
from logger_setup import setup_logger  # Importerar funktion för att konfigurera loggning
from scraper import NodeHillScraper  # Importerar skraparklassen

async def main() -> None:  # Asynkron huvudfunktion som kör hela programmet
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # Skapar utdatakatalogen om den inte finns
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)  # Skapar loggkatalogen om den inte finns

    logger = setup_logger(config.LOG_DIR)  # Skapar och konfigurerar loggaren
    scraper = NodeHillScraper(logger)  # Skapar en instans av skraparen med loggaren

    logger.info("Startar programmet...")  # Loggar att programmet startar

    async with async_playwright() as p:  # Startar Playwright-kontexten
        browser = await p.chromium.launch(  # Startar Chromium-webbläsaren
            headless=config.HEADLESS,  # Styr om webbläsaren körs utan grafiskt gränssnitt
            slow_mo=config.SLOW_MO_MS  # Lägger till fördröjning mellan åtgärder för stabilitet
        )

        try:  # Försöker köra skrapningen
            results = await scraper.run(browser, config.OUTPUT_DIR)  # Kör hela skrapningen och samlar resultat

            success_count = sum(1 for r in results if r.success)  # Räknar antalet lyckade exporter
            fail_count = sum(1 for r in results if not r.success)  # Räknar antalet misslyckade exporter

            logger.info("Klart. Lyckade exporter: %s", success_count)  # Loggar antal lyckade exporter
            logger.info("Misslyckade exporter: %s", fail_count)  # Loggar antal misslyckade exporter

        finally:  # Körs alltid oavsett om skrapningen lyckades
            await browser.close()  # Stänger webbläsaren

if __name__ == "__main__":  # Kontrollerar att skriptet körs direkt och inte importeras
    asyncio.run(main())  # Startar den asynkrona huvudfunktionen