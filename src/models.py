from dataclasses import dataclass  # Importerar dataclass-dekoratorn för att enkelt skapa dataklasser

@dataclass  # Dekorator som automatiskt genererar __init__, __repr__ och __eq__
class ArticleLink:  # Dataklass som representerar en artikellänk
    title: str  # Artikelns titel som textsträng
    url: str  # Artikelns URL som textsträng

@dataclass  # Dekorator som automatiskt genererar __init__, __repr__ och __eq__
class ExportResult:  # Dataklass som representerar resultatet av en PDF-export
    title: str  # Artikelns titel
    url: str  # Artikelns URL
    pdf_path: str  # Sökvägen till den skapade PDF-filen
    success: bool  # Sant om exporten lyckades, annars falskt
    error_message: str | None = None  # Eventuellt felmeddelande, None om exporten lyckades