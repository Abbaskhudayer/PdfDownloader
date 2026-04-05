import re  # Importerar modulen för reguljära uttryck
from urllib.parse import urlparse  # Importerar urlparse för att tolka URL-strängar

def clean_text(value: str) -> str:  # Funktion som rensar en textsträng från extra blanksteg
    return re.sub(r"\s+", " ", value).strip()  # Ersätter flera blanksteg med ett enda och tar bort inledande/avslutande blanksteg

def make_safe_filename(value: str, max_length: int = 120) -> str:  # Funktion som skapar ett säkert filnamn från en sträng
    value = clean_text(value)  # Rensar texten från extra blanksteg

    if not value:  # Kontrollerar om strängen är tom efter rensning
        return "untitled"  # Returnerar standardnamn om strängen var tom

    value = re.sub(r'[<>:"/\\|?*]', "_", value)  # Ersätter ogiltiga filnamnstecken med understreck
    value = value.strip(" .")  # Tar bort inledande och avslutande mellanslag och punkter

    if len(value) > max_length:  # Kontrollerar om filnamnet är för långt
        value = value[:max_length].rstrip()  # Kortar ner filnamnet till maxlängden

    return value or "untitled"  # Returnerar filnamnet, eller standardnamn om strängen blivit tom

def normalize_url(url: str) -> str:  # Funktion som normaliserar en URL
    parsed = urlparse(url)  # Tolkar URL-strängen till dess komponenter
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"  # Bygger ihop en normaliserad URL utan frågeparametrar