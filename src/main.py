import asyncio
from playwright.async_api import async_playwright
import config
from logger_setup import setup_logger
from scraper import NodeHillScraper

async def main() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(config.LOG_DIR)
    scraper = NodeHillScraper(logger)

    logger.info("Startar programmet...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO_MS
        )

        try:
            results = await scraper.run(browser, config.OUTPUT_DIR)

            success_count = sum(1 for r in results if r.success)
            fail_count = sum(1 for r in results if not r.success)

            logger.info("Klart. Lyckade exporter: %s", success_count)
            logger.info("Misslyckade exporter: %s", fail_count)

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())