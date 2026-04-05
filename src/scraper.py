from pathlib import Path  # Importerar Path för att hantera filsökvägar
from typing import List  # Importerar List för typannotering

from playwright.async_api import Browser, BrowserContext, Page  # Importerar Playwright-klasser för webbläsarautomation

from models import ArticleLink, ExportResult  # Importerar datamodeller för artikellänkar och exportresultat
from pdf_exporter import export_page_to_pdf, build_clean_article_html  # Importerar funktioner för PDF-export
from utils import clean_text, make_safe_filename, normalize_url  # Importerar hjälpfunktioner för text och URL
import config  # Importerar konfigurationsinställningar


class NodeHillScraper:  # Definierar skrarparklass för NodeHill-webbplatsen
    def __init__(self, logger):  # Konstruktor som tar emot en loggare som parameter
        self.logger = logger  # Sparar loggaren som instansvariabel
        self.seen_urls: set[str] = set()  # Skapar en mängd för att hålla reda på besökta URL:er

    async def open_start_page(self, page: Page) -> None:  # Asynkron metod för att öppna startsidan
        self.logger.info("Öppnar startsidan: %s", config.BASE_URL)  # Loggar att startsidan öppnas

        await page.goto(  # Navigerar till bas-URL:en
            config.BASE_URL,  # URL från konfigurationsfilen
            wait_until="networkidle",  # Väntar tills nätverkstrafiken är stilla
            timeout=config.NAVIGATION_TIMEOUT_MS,  # Använder konfigurerad timeout
        )

        await page.wait_for_timeout(config.WAIT_AFTER_LOAD_MS)  # Väntar extra tid efter laddning

    async def collect_article_links(self, page: Page) -> List[ArticleLink]:  # Asynkron metod för att samla in artikellänkar
        self.logger.info("Samlar artikellänkar...")  # Loggar att insamlingen börjar

        raw_links = await page.eval_on_selector_all(  # Kör JavaScript för att hämta alla artikellänkar
            config.ARTICLE_CARD_SELECTOR,  # CSS-selektor för artikelkort
            """
            elements => elements.map(el => ({
                title: (el.textContent || '').trim(),
                url: el.href || ''
            }))
            """
        )

        articles: list[ArticleLink] = []  # Skapar en tom lista för artiklarna

        for item in raw_links:  # Itererar över varje rålänk
            title = clean_text(item.get("title", ""))  # Rensar titeltexten från extra blanksteg
            url = item.get("url", "").strip()  # Hämtar och trimmar URL:en

            if not title or not url:  # Hoppar över poster utan titel eller URL
                continue  # Fortsätter till nästa iteration

            if "sys9-newton.lms.nodehill.se" not in url:  # Kontrollerar att URL:en tillhör rätt domän
                continue  # Hoppar över om domänen inte stämmer

            normalized = normalize_url(url)  # Normaliserar URL:en för enhetlighet

            # Ta bara riktiga artikelsidor
            if "/article/" not in normalized:  # Kontrollerar att sidan är en artikelsida
                continue  # Hoppar över om det inte är en artikelsida

            if normalized in self.seen_urls:  # Kontrollerar om URL:en redan besökts
                continue  # Hoppar över dubbletter

            self.seen_urls.add(normalized)  # Lägger till URL:en i mängden av besökta URL:er
            articles.append(ArticleLink(title=title, url=normalized))  # Lägger till artikeln i listan

        self.logger.info("Antal hittade unika artikellänkar: %s", len(articles))  # Loggar antalet hittade artiklar
        return articles  # Returnerar listan med artiklar

    async def get_best_title(self, page: Page, fallback: str) -> str:  # Asynkron metod för att hämta bästa möjliga titel
        locator = page.locator(config.ARTICLE_TITLE_SELECTOR).first  # Skapar en locator för titelelementet
        if await locator.count() > 0:  # Kontrollerar att titelelementet finns på sidan
            text = clean_text(await locator.inner_text())  # Hämtar och rensar titeltexten
            if text:  # Kontrollerar att texten inte är tom
                return text  # Returnerar den hittade titeln

        return fallback  # Returnerar reservtiteln om ingen titel hittades

    async def extract_article_body_html(self, page: Page) -> str:  # Asynkron metod för att extrahera artikelns HTML-innehåll
        body_locator = page.locator(config.ARTICLE_BODY_SELECTOR).first  # Skapar en locator för artikelns innehåll
        if await body_locator.count() == 0:  # Kontrollerar att innehållselementet finns
            raise ValueError(  # Kastar ett fel om elementet saknas
                f"Kunde inte hitta artikelinnehåll med selector: {config.ARTICLE_BODY_SELECTOR}"  # Felmeddelande med selektor
            )

        body_html = await page.eval_on_selector(  # Kör JavaScript för att extrahera och rensa artikelns HTML
            config.ARTICLE_BODY_SELECTOR,  # CSS-selektor för artikelns innehållsblock
            """
            (element) => {
                const clone = element.cloneNode(true); // Klonar elementet för att inte ändra originalet

                const selectorsToRemove = [ // Definierar selektorer för element som ska tas bort
                    ".prev-next-links",
                    ".favorites-button",
                    "button",
                    "[role='button']",
                    ".copy-button",
                    ".copy-btn",
                    ".clipboard-button",
                    ".code-copy",
                    ".toolbar",
                    ".code-toolbar",
                    ".v-btn",
                    ".material-icons",
                    ".line-numbers-rows",
                    ".line-numbers",
                    ".line-number",
                    "[class*='line-number']",
                    "[class*='linenumber']",
                    "[data-line-number]",
                    "[aria-label='Copy code']"
                ];

                for (const selector of selectorsToRemove) { // Itererar över selektorerna och tar bort matchande element
                    clone.querySelectorAll(selector).forEach(node => node.remove()); // Tar bort varje matchande nod
                }

                // Ta bort element som bara visar copy-ikon/text
                clone.querySelectorAll("*").forEach(node => { // Itererar över alla element i klonen
                    const text = (node.textContent || "").trim(); // Hämtar och trimmar elementets textinnehåll
                    const childCount = node.children ? node.children.length : 0; // Räknar antalet barnelement

                    if (
                        childCount === 0 && // Kontrollerar att elementet saknar barn
                        (
                            text === "content_copy" || // Kontrollerar om texten är en copy-ikon
                            text === "copy" || // Kontrollerar om texten är "copy"
                            text === "Copy" // Kontrollerar om texten är "Copy"
                        )
                    ) {
                        node.remove(); // Tar bort copy-ikonelement
                    }
                });

                function normalizeLineEndings(value) { // Funktion som normaliserar radbrytningar till Unix-stil
                    return (value || "").replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n"); // Ersätter Windows- och Mac-radbrytningar
                }

                function trimOuterBlankLines(value) { // Funktion som tar bort tomma rader i början och slutet
                    return value.replace(/^\\n+|\\n+$/g, ""); // Tar bort inledande och avslutande tomma rader
                }

                function stripSharedIndentation(value) { // Funktion som tar bort gemensam indentering från alla rader
                    const lines = value.split("\\n"); // Delar upp texten i enskilda rader
                    const nonEmptyLines = lines.filter(line => line.trim().length > 0); // Filtrerar bort tomma rader

                    if (nonEmptyLines.length === 0) { // Kontrollerar om det finns några icke-tomma rader
                        return value; // Returnerar originalet om alla rader är tomma
                    }

                    const indents = nonEmptyLines.map(line => { // Beräknar indenteringslängden för varje rad
                        const match = line.match(/^\\s*/); // Matchar inledande blanksteg
                        return match ? match[0].length : 0; // Returnerar antal inledande blanksteg
                    });

                    const minIndent = Math.min(...indents); // Hittar den minsta indenteringen bland alla rader

                    if (minIndent <= 0) { // Kontrollerar om det finns någon gemensam indentering
                        return value; // Returnerar originalet om ingen gemensam indentering finns
                    }

                    return lines // Bearbetar raderna för att ta bort gemensam indentering
                        .map(line => {
                            if (line.trim().length === 0) { // Kontrollerar om raden är tom
                                return ""; // Returnerar tom sträng för tomma rader
                            }

                            return line.slice(minIndent); // Tar bort den gemensamma indenteringen
                        })
                        .join("\\n"); // Sätter ihop raderna igen med radbrytningar
                }

                function everyNonEmptyLineStartsWithNumber(value) { // Kontrollerar om varje icke-tom rad börjar med ett nummer
                    const lines = value.split("\\n").filter(line => line.trim().length > 0); // Filtrerar tomma rader

                    if (lines.length === 0) { // Kontrollerar om det finns några rader
                        return false; // Returnerar falskt om inga rader finns
                    }

                    return lines.every(line => /^\\s*\\d+/.test(line)); // Testar om varje rad börjar med ett nummer
                }

                function stripLeadingLineNumbers(value) { // Funktion som tar bort inledande radnummer
                    return value
                        .split("\\n") // Delar upp texten i rader
                        .map(line => line.replace(/^(\\s*)\\d+/, "$1")) // Tar bort radnumret men behåller indenteringen
                        .join("\\n"); // Sätter ihop raderna igen
                }

                function cleanCodeText(value) { // Funktion som utför fullständig rensning av kodtext
                    let text = normalizeLineEndings(value); // Normaliserar radbrytningar
                    text = trimOuterBlankLines(text); // Tar bort yttre tomma rader

                    if (everyNonEmptyLineStartsWithNumber(text)) { // Kontrollerar om rader börjar med radnummer
                        text = stripLeadingLineNumbers(text); // Tar bort radnumren
                    }

                    text = trimOuterBlankLines(text); // Tar bort yttre tomma rader igen
                    text = stripSharedIndentation(text); // Tar bort gemensam indentering

                    return text; // Returnerar den rensade kodtexten
                }

                // Gör om kodblock till ren textbaserad HTML så copy/paste blir bättre
                clone.querySelectorAll("pre").forEach(pre => { // Itererar över alla pre-element
                    const text = cleanCodeText(pre.innerText || pre.textContent || ""); // Rensar kodtexten

                    const newPre = document.createElement("pre"); // Skapar ett nytt pre-element
                    const newCode = document.createElement("code"); // Skapar ett nytt code-element
                    newCode.textContent = text; // Sätter den rensade texten i code-elementet

                    newPre.appendChild(newCode); // Lägger till code-elementet i pre-elementet
                    pre.replaceWith(newPre); // Ersätter det gamla pre-elementet med det nya
                });

                // Inline code utan pre runt sig
                clone.querySelectorAll("code").forEach(code => { // Itererar över alla code-element
                    if (code.closest("pre")) { // Kontrollerar om code-elementet är inuti ett pre-element
                        return; // Hoppar över element som redan hanteras av pre-blocket
                    }

                    code.textContent = normalizeLineEndings(code.innerText || code.textContent || ""); // Normaliserar radbrytningar i inline-kod
                });

                // Gör länkar absoluta
                clone.querySelectorAll("a[href]").forEach(a => { // Itererar över alla ankarlänkar
                    try {
                        a.href = new URL(a.getAttribute("href"), document.baseURI).href; // Gör relativa URL:er absoluta
                    } catch (_) {} // Ignorerar fel vid ogiltig URL
                });

                // Gör bildkällor absoluta
                clone.querySelectorAll("img[src]").forEach(img => { // Itererar över alla bilder
                    try {
                        img.src = new URL(img.getAttribute("src"), document.baseURI).href; // Gör relativa bildkällor absoluta
                    } catch (_) {} // Ignorerar fel vid ogiltig URL
                });

                // Ta bort tomma ankare
                clone.querySelectorAll("a[name]").forEach(a => { // Itererar över ankare med name-attribut
                    const hasVisibleContent = (a.textContent || "").trim().length > 0; // Kontrollerar om ankaret har synligt innehåll
                    const hasHref = a.hasAttribute("href"); // Kontrollerar om ankaret har en href

                    if (!hasVisibleContent && !hasHref) { // Tar bara bort ankaret om det saknar innehåll och href
                        a.remove(); // Tar bort det tomma ankaret
                    }
                });

                // Försök veckla ut scrollbara block
                clone.querySelectorAll("*").forEach(node => { // Itererar över alla element
                    const style = node.getAttribute("style") || ""; // Hämtar elementets stilattribut

                    if (style.includes("overflow")) { // Kontrollerar om overflow-stil finns
                        node.style.overflow = "visible"; // Gör overflow synligt
                    }

                    if (style.includes("height")) { // Kontrollerar om höjd-stil finns
                        node.style.height = "auto"; // Sätter höjden till auto
                    }

                    if (style.includes("max-height")) { // Kontrollerar om max-höjd-stil finns
                        node.style.maxHeight = "none"; // Tar bort max-höjdbegränsningen
                    }
                });

                clone.querySelectorAll("pre, code").forEach(node => { // Itererar över alla pre- och code-element
                    node.style.overflow = "visible"; // Gör overflow synligt
                    node.style.maxHeight = "none"; // Tar bort max-höjdbegränsningen
                    node.style.height = "auto"; // Sätter höjden till auto
                });

                return clone.innerHTML; // Returnerar det rensade HTML-innehållet
            }
            """
        )

        if not body_html or not str(body_html).strip():  # Kontrollerar att HTML-innehållet inte är tomt
            raise ValueError("Artikelinnehållet blev tomt efter extrahering.")  # Kastar fel om innehållet är tomt

        return str(body_html)  # Returnerar HTML-innehållet som sträng

    async def export_article(  # Asynkron metod för att exportera en artikel till PDF
        self,
        context: BrowserContext,  # Webbläsarkontexten att använda
        article: ArticleLink,  # Artikeln som ska exporteras
        index: int,  # Artikelns ordningsnummer
        output_dir: Path  # Katalogen där PDF:en ska sparas
    ) -> ExportResult:  # Returnerar ett exportresultat
        source_page = await context.new_page()  # Skapar en ny sida för att läsa artikeln

        try:  # Försöker exportera artikeln
            self.logger.info("Öppnar artikel %s: %s", index, article.url)  # Loggar att artikeln öppnas

            await source_page.goto(  # Navigerar till artikelns URL
                article.url,  # Artikelns URL
                wait_until="networkidle",  # Väntar tills nätverkstrafiken är stilla
                timeout=config.NAVIGATION_TIMEOUT_MS,  # Använder konfigurerad timeout
            )

            await source_page.wait_for_timeout(config.WAIT_AFTER_LOAD_MS)  # Väntar extra tid efter laddning

            title = await self.get_best_title(source_page, article.title)  # Hämtar bästa möjliga titel för artikeln
            body_html = await self.extract_article_body_html(source_page)  # Extraherar artikelns HTML-innehåll

            safe_title = make_safe_filename(title)  # Skapar ett säkert filnamn från titeln
            file_name = f"{index:03d}_{safe_title}.pdf"  # Bygger upp filnamnet med nollpaddat index och titel
            pdf_path = output_dir / file_name  # Skapar den fullständiga sökvägen för PDF-filen

            clean_html = build_clean_article_html(  # Bygger ren HTML för PDF-exporten
                title=title,  # Artikelns titel
                body_html=body_html,  # Artikelns HTML-innehåll
                source_url=article.url  # Artikelns käll-URL
            )

            export_page = await context.new_page()  # Skapar en ny sida för PDF-export
            try:  # Försöker exportera till PDF
                await export_page.set_content(  # Sätter HTML-innehållet på exportsidan
                    clean_html,  # Den rensade HTML:en
                    wait_until="load"  # Väntar tills sidan är laddad
                )
                await export_page.wait_for_timeout(300)  # Väntar 300ms för att låta sidan rendera klart

                await export_page_to_pdf(export_page, pdf_path)  # Exporterar sidan till en PDF-fil
            finally:  # Körs alltid oavsett om exporten lyckades
                await export_page.close()  # Stänger exportsidan

            self.logger.info("Sparade PDF: %s", pdf_path)  # Loggar att PDF:en sparades

            return ExportResult(  # Returnerar ett lyckat exportresultat
                title=title,  # Artikelns titel
                url=article.url,  # Artikelns URL
                pdf_path=str(pdf_path),  # Sökvägen till den skapade PDF-filen
                success=True  # Anger att exporten lyckades
            )

        except Exception as ex:  # Fångar eventuella fel under exporten
            self.logger.exception("Fel vid export av artikel: %s", article.url)  # Loggar felet med spårningsinformation

            return ExportResult(  # Returnerar ett misslyckat exportresultat
                title=article.title,  # Använder originaltiteln som reserv
                url=article.url,  # Artikelns URL
                pdf_path="",  # Tom sökväg eftersom exporten misslyckades
                success=False,  # Anger att exporten misslyckades
                error_message=str(ex)  # Sparar felmeddelandet som sträng
            )

        finally:  # Körs alltid efter try/except
            await source_page.close()  # Stänger källsidan

    async def run(self, browser: Browser, output_dir: Path) -> list[ExportResult]:  # Asynkron huvudmetod som kör hela skrapningen
        output_dir.mkdir(parents=True, exist_ok=True)  # Skapar utdatakatalogen om den inte finns

        context = await browser.new_context(  # Skapar en ny webbläsarkontext
            viewport={"width": 1600, "height": 1200}  # Sätter fönsterstorlek för rendering
        )

        start_page = await context.new_page()  # Skapar startsidan
        await self.open_start_page(start_page)  # Öppnar och laddar startsidan

        input("När sidan är helt laddad, tryck Enter för att fortsätta...")  # Väntar på att användaren trycker Enter

        articles = await self.collect_article_links(start_page)  # Samlar in alla artikellänkar från startsidan

        results: list[ExportResult] = []  # Skapar en tom lista för exportresultaten

        for index, article in enumerate(articles, start=1):  # Itererar över alla artiklar med startindex 1
            result = await self.export_article(  # Exporterar artikeln till PDF
                context=context,  # Webbläsarkontexten
                article=article,  # Den aktuella artikeln
                index=index,  # Artikelns ordningsnummer
                output_dir=output_dir  # Katalogen för PDF-filer
            )
            results.append(result)  # Lägger till resultatet i listan

        await start_page.close()  # Stänger startsidan
        await context.close()  # Stänger webbläsarkontexten

        return results  # Returnerar listan med alla exportresultat