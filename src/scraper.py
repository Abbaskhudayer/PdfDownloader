from pathlib import Path
from typing import List

from playwright.async_api import Browser, BrowserContext, Page

from models import ArticleLink, ExportResult
from pdf_exporter import export_page_to_pdf, build_clean_article_html
from utils import clean_text, make_safe_filename, normalize_url
import config


class NodeHillScraper:
    def __init__(self, logger):
        self.logger = logger
        self.seen_urls: set[str] = set()

    async def open_start_page(self, page: Page) -> None:
        self.logger.info("Oppnar startsidan: %s", config.BASE_URL)

        await page.goto(
            config.BASE_URL,
            wait_until="networkidle",
            timeout=config.NAVIGATION_TIMEOUT_MS,
        )

        await page.wait_for_timeout(config.WAIT_AFTER_LOAD_MS)

    async def collect_article_links(self, page: Page) -> List[ArticleLink]:
        self.logger.info("Samlar artikellankar...")

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

        self.logger.info("Antal hittade unika artikellankar: %s", len(articles))
        return articles

    async def get_best_title(self, page: Page, fallback: str) -> str:
        locator = page.locator(config.ARTICLE_TITLE_SELECTOR).first
        if await locator.count() > 0:
            text = clean_text(await locator.inner_text())
            if text:
                return text

        return fallback

    async def extract_article_body_html(self, page: Page) -> str:
        body_locator = page.locator(config.ARTICLE_BODY_SELECTOR).first
        if await body_locator.count() == 0:
            raise ValueError(
                f"Kunde inte hitta artikelinnehall med selector: {config.ARTICLE_BODY_SELECTOR}"
            )

        body_html = await page.eval_on_selector(
            config.ARTICLE_BODY_SELECTOR,
            """
            (element) => {
                const clone = element.cloneNode(true);

                // Ta bort oönskade saker inuti artikeln om de finns
                const selectorsToRemove = [
                    ".prev-next-links",
                    ".favorites-button"
                ];

                for (const selector of selectorsToRemove) {
                    clone.querySelectorAll(selector).forEach(node => node.remove());
                }

                // Gör länkar absoluta
                clone.querySelectorAll("a[href]").forEach(a => {
                    try {
                        a.href = new URL(a.getAttribute("href"), document.baseURI).href;
                    } catch (_) {}
                });

                // Gör bildkällor absoluta
                clone.querySelectorAll("img[src]").forEach(img => {
                    try {
                        img.src = new URL(img.getAttribute("src"), document.baseURI).href;
                    } catch (_) {}
                });

                // Ta bort ankarlänkar av typen <a name="..."></a> om de är tomma
                clone.querySelectorAll("a[name]").forEach(a => {
                    const hasVisibleContent = (a.textContent || "").trim().length > 0;
                    const hasHref = a.hasAttribute("href");
                    if (!hasVisibleContent && !hasHref) {
                        a.remove();
                    }
                });

                // Försök veckla ut scrollbara kodrutor / block
                clone.querySelectorAll("*").forEach(node => {
                    const style = node.getAttribute("style") || "";

                    if (style.includes("overflow")) {
                        node.style.overflow = "visible";
                    }

                    if (style.includes("height")) {
                        node.style.height = "auto";
                    }

                    if (style.includes("max-height")) {
                        node.style.maxHeight = "none";
                    }
                });

                clone.querySelectorAll("pre, code").forEach(node => {
                    node.style.whiteSpace = "pre-wrap";
                    node.style.wordBreak = "break-word";
                    node.style.overflow = "visible";
                    node.style.maxHeight = "none";
                    node.style.height = "auto";
                });

                return clone.innerHTML;
            }
            """
        )

        if not body_html or not str(body_html).strip():
            raise ValueError("Artikelinnehållet blev tomt efter extrahering.")

        return str(body_html)

    async def export_article(
        self,
        context: BrowserContext,
        article: ArticleLink,
        index: int,
        output_dir: Path
    ) -> ExportResult:
        source_page = await context.new_page()

        try:
            self.logger.info("Oppnar artikel %s: %s", index, article.url)

            await source_page.goto(
                article.url,
                wait_until="networkidle",
                timeout=config.NAVIGATION_TIMEOUT_MS,
            )

            await source_page.wait_for_timeout(config.WAIT_AFTER_LOAD_MS)

            title = await self.get_best_title(source_page, article.title)
            body_html = await self.extract_article_body_html(source_page)

            safe_title = make_safe_filename(title)
            file_name = f"{index:03d}_{safe_title}.pdf"
            pdf_path = output_dir / file_name

            clean_html = build_clean_article_html(
                title=title,
                body_html=body_html,
                source_url=article.url
            )

            export_page = await context.new_page()
            try:
                await export_page.set_content(
                    clean_html,
                    wait_until="load"
                )
                await export_page.wait_for_timeout(300)

                await export_page_to_pdf(export_page, pdf_path)
            finally:
                await export_page.close()

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
            await source_page.close()

    async def run(self, browser: Browser, output_dir: Path) -> list[ExportResult]:
        output_dir.mkdir(parents=True, exist_ok=True)

        context = await browser.new_context(
            viewport={"width": 1600, "height": 1200}
        )

        start_page = await context.new_page()
        await self.open_start_page(start_page)

        input("Nar sidan ar helt laddad, tryck Enter for att fortsatta...")

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