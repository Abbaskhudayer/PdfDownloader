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

            if "/article/" not in url:
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
            if await locator.count() > 0:
                text = clean_text(await locator.inner_text())
                if text:
                    return text
        return fallback

    async def find_article_html(self, page: Page) -> str | None:
        for selector in config.ARTICLE_CONTENT_SELECTORS:
            locator = page.locator(selector).first
            if await locator.count() > 0:
                html = await locator.inner_html()
                if html and html.strip():
                    return html
        return None

    async def expand_dynamic_content(self, page: Page) -> None:
        await page.evaluate(
            """
            () => {
                const all = document.querySelectorAll("*");

                for (const el of all) {
                    const style = window.getComputedStyle(el);

                    const isScrollable =
                        ["auto", "scroll", "hidden"].includes(style.overflow) ||
                        ["auto", "scroll", "hidden"].includes(style.overflowX) ||
                        ["auto", "scroll", "hidden"].includes(style.overflowY);

                    if (isScrollable) {
                        el.style.overflow = "visible";
                        el.style.overflowX = "visible";
                        el.style.overflowY = "visible";
                        el.style.maxHeight = "none";
                        el.style.height = "auto";
                    }
                }

                document.querySelectorAll("pre, code").forEach(el => {
                    el.style.whiteSpace = "pre-wrap";
                    el.style.wordBreak = "break-word";
                    el.style.overflow = "visible";
                    el.style.maxHeight = "none";
                    el.style.height = "auto";
                });

                document.querySelectorAll("img").forEach(img => {
                    img.loading = "eager";
                });
            }
            """
        )

    def build_clean_html(self, title: str, body_html: str, source_url: str) -> str:
        return f"""
<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{
      font-family: Arial, Helvetica, sans-serif;
      color: #222;
      margin: 0;
      padding: 32px;
      line-height: 1.6;
      font-size: 15px;
    }}

    h1, h2, h3, h4 {{
      line-height: 1.25;
      margin-top: 1.2em;
    }}

    img {{
      max-width: 100%;
      height: auto;
    }}

    a {{
      color: #0a58ca;
      text-decoration: underline;
      word-break: break-word;
    }}

    pre, code {{
      font-family: Consolas, "Courier New", monospace;
    }}

    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      overflow: visible !important;
      max-height: none !important;
      height: auto !important;
      border: 1px solid #ddd;
      background: #f7f7f7;
      padding: 12px;
      border-radius: 6px;
    }}

    code {{
      white-space: pre-wrap;
      word-break: break-word;
    }}

    table {{
      border-collapse: collapse;
      width: 100%;
      table-layout: auto;
    }}

    th, td {{
      border: 1px solid #ccc;
      padding: 8px;
      vertical-align: top;
      word-break: break-word;
    }}

    .meta {{
      margin-bottom: 24px;
      font-size: 13px;
      color: #666;
    }}

    .article-root * {{
      max-height: none !important;
    }}

    .article-root [style*="overflow"],
    .article-root [class*="scroll"],
    .article-root [class*="code"] {{
      overflow: visible !important;
      max-height: none !important;
      height: auto !important;
    }}

    @page {{
      size: A4;
      margin: 15mm 12mm 15mm 12mm;
    }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="meta">Källa: <a href="{source_url}">{source_url}</a></div>
  <div class="article-root">
    {body_html}
  </div>
</body>
</html>
"""

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

            await self.expand_dynamic_content(page)

            title = await self.get_best_title(page, article.title)
            article_html = await self.find_article_html(page)

            if not article_html:
                raise RuntimeError("Kunde inte hitta artikelinnehåll på sidan.")

            clean_html = self.build_clean_html(title, article_html, article.url)

            pdf_page = await context.new_page()
            await pdf_page.set_content(clean_html, wait_until="load")
            await pdf_page.wait_for_timeout(1000)

            safe_title = make_safe_filename(title)
            file_name = f"{index:03d}_{safe_title}.pdf"
            pdf_path = output_dir / file_name

            await export_page_to_pdf(pdf_page, pdf_path)

            await pdf_page.close()

            self.logger.info("Sparade ren PDF: %s", pdf_path)

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
            viewport={"width": 1600, "height": 1400}
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