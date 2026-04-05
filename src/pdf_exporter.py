from html import escape
from pathlib import Path
from playwright.async_api import Page


async def export_page_to_pdf(page: Page, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    await page.pdf(
        path=str(output_path),
        format="A4",
        print_background=True,
        margin={
            "top": "15mm",
            "bottom": "15mm",
            "left": "12mm",
            "right": "12mm",
        },
    )


def build_clean_article_html(title: str, body_html: str, source_url: str) -> str:
    safe_title = escape(title)
    safe_source_url = escape(source_url, quote=True)

    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="utf-8" />
    <title>{safe_title}</title>
    <style>
        @page {{
            size: A4;
            margin: 15mm 12mm 15mm 12mm;
        }}

        html, body {{
            margin: 0;
            padding: 0;
            background: #ffffff;
            color: #111111;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12pt;
            line-height: 1.55;
        }}

        body {{
            padding: 0;
        }}

        .article-wrapper {{
            width: 100%;
        }}

        .article-title {{
            font-size: 22pt;
            font-weight: 700;
            line-height: 1.25;
            margin: 0 0 12mm 0;
        }}

        .source-url {{
            margin: 0 0 10mm 0;
            font-size: 9pt;
            color: #555;
            word-break: break-all;
        }}

        h1, h2, h3, h4, h5, h6 {{
            page-break-after: avoid;
            margin-top: 8mm;
            margin-bottom: 3mm;
            line-height: 1.3;
        }}

        p, ul, ol, blockquote {{
            margin-top: 0;
            margin-bottom: 4mm;
        }}

        ul, ol {{
            padding-left: 7mm;
        }}

        li {{
            margin-bottom: 1.5mm;
        }}

        a {{
            color: #0645ad;
            text-decoration: underline;
            word-break: break-word;
        }}

        img {{
            display: block;
            max-width: 100%;
            height: auto;
            margin: 4mm 0;
        }}

        pre, code {{
            font-family: Consolas, "Courier New", monospace;
            tab-size: 4;
        }}

        pre {{
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            word-break: normal;
            overflow: visible !important;
            max-height: none !important;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            padding: 14px 16px;
            background: #f7f7f7;
            margin: 5mm 0 6mm 0;
            page-break-inside: avoid;
            break-inside: avoid;
            font-size: 10.5pt;
            line-height: 1.6;
        }}

        pre code {{
            display: block;
            white-space: inherit;
            overflow-wrap: inherit;
            word-break: inherit;
        }}

        code {{
            white-space: pre-wrap;
            word-break: break-word;
            font-size: 0.95em;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 5mm;
            table-layout: auto;
        }}

        th, td {{
            border: 1px solid #cfcfcf;
            padding: 6px;
            vertical-align: top;
            text-align: left;
        }}

        blockquote {{
            border-left: 3px solid #d6d6d6;
            padding-left: 10px;
            color: #444;
        }}

        .article-body * {{
            max-height: none !important;
        }}

        .article-body [style*="overflow"] {{
            overflow: visible !important;
        }}

        .article-body [style*="height"] {{
            height: auto !important;
        }}

        .article-body [style*="max-height"] {{
            max-height: none !important;
        }}
    </style>
</head>
<body>
    <div class="article-wrapper">
        <h1 class="article-title">{safe_title}</h1>
        <div class="source-url">Källa: <a href="{safe_source_url}">{safe_source_url}</a></div>
        <div class="article-body">
            {body_html}
        </div>
    </div>
</body>
</html>
"""