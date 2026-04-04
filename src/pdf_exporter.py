from pathlib import Path
from playwright.async_api import Page

async def export_page_to_pdf(page: Page, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    await page.pdf(
        path=str(output_path),
        format="A4",
        print_background=True,
        prefer_css_page_size=True,
    )