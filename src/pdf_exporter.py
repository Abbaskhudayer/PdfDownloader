from html import escape  # Importerar escape för att skydda specialtecken i HTML
from pathlib import Path  # Importerar Path för att hantera filsökvägar
from playwright.async_api import Page  # Importerar Page-klassen från Playwright


async def export_page_to_pdf(page: Page, output_path: Path) -> None:  # Asynkron funktion som exporterar en sida till PDF
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Skapar utdatakatalogen om den inte redan finns

    await page.pdf(  # Anropar Playwrights PDF-exportfunktion
        path=str(output_path),  # Sätter sökvägen för den sparade PDF-filen
        format="A4",  # Använder A4-format för sidan
        print_background=True,  # Inkluderar bakgrundsfärger och bilder i PDF:en
        margin={  # Definierar marginaler för PDF-sidan
            "top": "15mm",  # Övre marginal
            "bottom": "15mm",  # Nedre marginal
            "left": "12mm",  # Vänster marginal
            "right": "12mm",  # Höger marginal
        },
    )


def build_clean_article_html(title: str, body_html: str, source_url: str) -> str:  # Funktion som bygger ren HTML för PDF-export
    safe_title = escape(title)  # Escapar specialtecken i titeln för säker HTML-inbäddning
    safe_source_url = escape(source_url, quote=True)  # Escapar specialtecken i URL:en inklusive citattecken

    return f"""<!DOCTYPE html>  <!-- HTML5-dokumenttypsdeklaration -->
<html lang="sv">  <!-- Rotelementet med svenska som språkinställning -->
<head>  <!-- Sidhuvudet med metadata och stilar -->
    <meta charset="utf-8" />  <!-- Anger teckenkodning till UTF-8 -->
    <title>{safe_title}</title>  <!-- Sidans titel från artikelns rubrik -->
    <style>  <!-- Inbäddade CSS-stilar för PDF-layouten -->
        @page {{  /* Sidformatsinställningar för utskrift */
            size: A4;  /* A4-sidformat */
            margin: 15mm 12mm 15mm 12mm;  /* Marginaler: topp höger botten vänster */
        }}

        html, body {{  /* Grundläggande stilar för hela dokumentet */
            margin: 0;  /* Nollställer standardmarginaler */
            padding: 0;  /* Nollställer standardpadding */
            background: #ffffff;  /* Vit bakgrundsfärg */
            color: #111111;  /* Nästan svart textfärg */
            font-family: Arial, Helvetica, sans-serif;  /* Sans-serif typsnittsfamilj */
            font-size: 12pt;  /* Grundläggande teckenstorlek */
            line-height: 1.55;  /* Radavstånd för läsbarhet */
        }}

        body {{  /* Ytterligare stilar för body-elementet */
            padding: 0;  /* Nollställer padding på body */
        }}

        .article-wrapper {{  /* Wrapper-element för artikelinnehållet */
            width: 100%;  /* Full bredd */
        }}

        .article-title {{  /* Stil för artikelns huvudrubrik */
            font-size: 22pt;  /* Stor teckenstorlek för titeln */
            font-weight: 700;  /* Fet stil */
            line-height: 1.25;  /* Kompakt radavstånd för rubriken */
            margin: 0 0 12mm 0;  /* Undre marginal för avstånd till innehållet */
        }}

        .source-url {{  /* Stil för käll-URL:en under titeln */
            margin: 0 0 10mm 0;  /* Undre marginal */
            font-size: 9pt;  /* Liten teckenstorlek för URL:en */
            color: #555;  /* Grå textfärg */
            word-break: break-all;  /* Tillåter radbrytning mitt i URL:en */
        }}

        h1, h2, h3, h4, h5, h6 {{  /* Stilar för alla rubriknivåer */
            page-break-after: avoid;  /* Undviker sidbrytning direkt efter rubrik */
            margin-top: 8mm;  /* Övre marginal för rubriker */
            margin-bottom: 3mm;  /* Undre marginal för rubriker */
            line-height: 1.3;  /* Radavstånd för rubriker */
        }}

        p, ul, ol, blockquote {{  /* Stilar för stycken och listor */
            margin-top: 0;  /* Ingen övre marginal */
            margin-bottom: 4mm;  /* Undre marginal för avstånd mellan block */
        }}

        ul, ol {{  /* Stilar för ordnade och oordnade listor */
            padding-left: 7mm;  /* Indentering för listpunkter */
        }}

        li {{  /* Stil för enskilda listobjekt */
            margin-bottom: 1.5mm;  /* Litet avstånd mellan listobjekt */
        }}

        a {{  /* Stilar för hyperlänkar */
            color: #0645ad;  /* Blå länkfärg */
            text-decoration: underline;  /* Understrykning på länkar */
            word-break: break-word;  /* Tillåter radbrytning i långa URL:er */
        }}

        img {{  /* Stilar för bilder */
            display: block;  /* Visar bilden som ett blockelement */
            max-width: 100%;  /* Begränsar bilden till sidans bredd */
            height: auto;  /* Bevarar bildproportionerna */
            margin: 4mm 0;  /* Vertikalt avstånd runt bilder */
        }}

        pre, code {{  /* Stilar för kodblock och inline-kod */
            font-family: Consolas, "Courier New", monospace;  /* Monospace-typsnitt för kod */
            tab-size: 4;  /* Tabbstorlek på 4 tecken */
        }}

        pre {{  /* Stilar för förformaterade kodblock */
            white-space: pre-wrap;  /* Bevarar blanksteg men tillåter radbrytning */
            overflow-wrap: anywhere;  /* Tillåter radbrytning var som helst */
            word-break: normal;  /* Normal ordbrytning */
            overflow: visible !important;  /* Tvingar synligt innehåll utan scrollning */
            max-height: none !important;  /* Tar bort eventuell maxhöjdbegränsning */
            border: 1px solid #d0d0d0;  /* Tunn grå ram runt kodblocket */
            border-radius: 8px;  /* Rundade hörn */
            padding: 14px 16px;  /* Inre avstånd i kodblocket */
            background: #f7f7f7;  /* Ljusgrå bakgrund för kodblock */
            margin: 5mm 0 6mm 0;  /* Vertikalt avstånd runt kodblock */
            page-break-inside: avoid;  /* Undviker sidbrytning mitt i kodblock */
            break-inside: avoid;  /* Modern CSS för att undvika bryt inuti kodblock */
            font-size: 10.5pt;  /* Teckenstorlek för kod */
            line-height: 1.6;  /* Radavstånd för läsbarhet i kod */
        }}

        pre code {{  /* Stilar för code-element inuti pre-block */
            display: block;  /* Visar som blockelement */
            white-space: inherit;  /* Ärver white-space från pre */
            overflow-wrap: inherit;  /* Ärver overflow-wrap från pre */
            word-break: inherit;  /* Ärver word-break från pre */
        }}

        code {{  /* Stilar för inline-kod utanför pre-block */
            white-space: pre-wrap;  /* Bevarar blanksteg men tillåter radbrytning */
            word-break: break-word;  /* Bryter långa ord vid behov */
            font-size: 0.95em;  /* Något mindre teckenstorlek än omgivande text */
        }}

        table {{  /* Stilar för tabeller */
            border-collapse: collapse;  /* Slår ihop cellramar till en enda ram */
            width: 100%;  /* Full bredd */
            margin-bottom: 5mm;  /* Undre marginal */
            table-layout: auto;  /* Automatisk kolumnbredd baserat på innehåll */
        }}

        th, td {{  /* Stilar för tabellrubriker och celler */
            border: 1px solid #cfcfcf;  /* Tunn grå ram runt varje cell */
            padding: 6px;  /* Inre avstånd i cellerna */
            vertical-align: top;  /* Justerar innehåll till toppen av cellen */
            text-align: left;  /* Vänsterjusterar text */
        }}

        blockquote {{  /* Stilar för citat-block */
            border-left: 3px solid #d6d6d6;  /* Grå vänsterkant som markerar citatet */
            padding-left: 10px;  /* Indentering av citattext */
            color: #444;  /* Mörkgrå textfärg för citat */
        }}

        .article-body * {{  /* Nollställer maxhöjd för alla element i artikelkroppen */
            max-height: none !important;  /* Säkerställer att inget innehåll döljs */
        }}

        .article-body [style*="overflow"] {{  /* Åsidosätter overflow-stilar i artikelkroppen */
            overflow: visible !important;  /* Tvingar all overflow att synas */
        }}

        .article-body [style*="height"] {{  /* Åsidosätter höjdstilar i artikelkroppen */
            height: auto !important;  /* Sätter höjden till auto */
        }}

        .article-body [style*="max-height"] {{  /* Åsidosätter maxhöjdstilar i artikelkroppen */
            max-height: none !important;  /* Tar bort maxhöjdbegränsning */
        }}
    </style>  <!-- Slut på stilsektion -->
</head>  <!-- Slut på sidhuvudet -->
<body>  <!-- Sidans synliga innehåll -->
    <div class="article-wrapper">  <!-- Wrapper-container för hela artikeln -->
        <h1 class="article-title">{safe_title}</h1>  <!-- Artikelns titel -->
        <div class="source-url">Källa: <a href="{safe_source_url}">{safe_source_url}</a></div>  <!-- Länk till källsidan -->
        <div class="article-body">  <!-- Container för artikelns brödtext -->
            {body_html}  <!-- Det extraherade HTML-innehållet från artikeln -->
        </div>  <!-- Slut på article-body -->
    </div>  <!-- Slut på article-wrapper -->
</body>  <!-- Slut på body -->
</html>  <!-- Slut på HTML-dokumentet -->
"""