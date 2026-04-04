from dataclasses import dataclass

@dataclass
class ArticleLink:
    title: str
    url: str

@dataclass
class ExportResult:
    title: str
    url: str
    pdf_path: str
    success: bool
    error_message: str | None = None