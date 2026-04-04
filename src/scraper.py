from pathlib import Path
from typing import List
from playwright.async_api import Browser, BrowserContext, Page
from models import ArticleLink, ExportResult
from pdf_exporter import export_page_to_pdf
from utils import clean_text, make_safe_filename, normalize_url
import config

class NodeHillScraper:
    def __init__(self, logger):
        self.logger = logger
        self.seen_urls: set[str] = set()

    async def open_start_page(self, page: Page) -> None:
        self.logger.info("Öppnar startsidan: %s", config.BASE_URL)

        await page.goto(
            config.BASE_URL,
            wait_until="networkidle",
            timeout=config.NAVIGATION_TIMEOUT_MS,
        )

        await page.wait_for_timeout(config.WAIT_AFTER_LOAD_MS)

    async def collect_article_links(self, page: Page) -> List[ArticleLink]:
        self.logger.info("Samlar artikellänkar...")

        raw_links = await page.eval_on_selector_all(
            config.ARTICLE_CARD_SELECTOR,
            """
            elements => elements.map(el => ({
                title: (el.textContent || '').trim(),
                url: el.href || ''
            }))
            """
        )

        articles: list[ArticleLink] = []

        for item in raw_links:
            title = clean_text(item.get("title", ""))
            url = item.get("url", "").strip()

            if not title or not url:
                continue

            if "sys9-newton.lms.nodehill.se" not in url:
                continue

            normalized = normalize_url(url)

            if normalized in self.seen_urls:
                continue

            self.seen_urls.add(normalized)
            articles.append(ArticleLink(title=title, url=url))

        self.logger.info("Antal hittade unika artikellänkar: %s", len(articles))
        return articles

    async def get_best_title(self, page: Page, fallback: str) -> str:
        for selector in config.ARTICLE_TITLE_SELECTORS:
            locator = page.locator(selector).first
            count = await locator.count()
            if count > 0:
                text = clean_text(await locator.inner_text())
                if text:
                    return text
        return fallback

    async def prepare_page_for_pdf(self, page: Page) -> None:
        await page.add_style_tag(
            content="""
            @media print {
                nav, aside, footer {
                    display: none !important;
                }
            }
            """
        )

    async def export_article(
        self,
        context: BrowserContext,
        article: ArticleLink,
        index: int,
        output_dir: Path
    ) -> ExportResult:
        page = await context.new_page()

        try:
            self.logger.info("Öppnar artikel %s: %s", index, article.url)

            await page.goto(
                article.url,
                wait_until="networkidle",
                timeout=config.NAVIGATION_TIMEOUT_MS,
            )

            await page.wait_for_timeout(config.WAIT_AFTER_LOAD_MS)

            title = await self.get_best_title(page, article.title)
            safe_title = make_safe_filename(title)
            file_name = f"{index:03d}_{safe_title}.pdf"
            pdf_path = output_dir / file_name

            await self.prepare_page_for_pdf(page)
            await export_page_to_pdf(page, pdf_path)

            self.logger.info("Sparade PDF: %s", pdf_path)

            return ExportResult(
                title=title,
                url=article.url,
                pdf_path=str(pdf_path),
                success=True
            )

        except Exception as ex:
            self.logger.exception("Fel vid export av artikel: %s", article.url)

            return ExportResult(
                title=article.title,
                url=article.url,
                pdf_path="",
                success=False,
                error_message=str(ex)
            )

        finally:
            await page.close()

    async def run(self, browser: Browser, output_dir: Path) -> list[ExportResult]:
        output_dir.mkdir(parents=True, exist_ok=True)

        context = await browser.new_context(
            viewport={"width": 1600, "height": 1200}
        )

        start_page = await context.new_page()
        await self.open_start_page(start_page)

        input("När sidan är helt laddad, tryck Enter för att fortsätta...")

        articles = await self.collect_article_links(start_page)

        results: list[ExportResult] = []

        for index, article in enumerate(articles, start=1):
            result = await self.export_article(
                context=context,
                article=article,
                index=index,
                output_dir=output_dir
            )
            results.append(result)

        await start_page.close()
        await context.close()

        return results