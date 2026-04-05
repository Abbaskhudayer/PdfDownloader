import logging  # Importerar standardbibliotekets loggningsmodul
from pathlib import Path  # Importerar Path för att hantera filsökvägar

def setup_logger(log_dir: Path) -> logging.Logger:  # Funktion som skapar och konfigurerar en loggare
    log_dir.mkdir(parents=True, exist_ok=True)  # Skapar loggkatalogen om den inte finns
    log_file = log_dir / "run.log"  # Definierar sökvägen till loggfilen

    logger = logging.getLogger("nodehill_pdf")  # Hämtar eller skapar en loggare med ett unikt namn
    logger.setLevel(logging.INFO)  # Sätter lägsta loggnivå till INFO
    logger.handlers.clear()  # Tar bort eventuella tidigare handlers för att undvika dubbletter

    file_handler = logging.FileHandler(log_file, encoding="utf-8")  # Skapar en handler som skriver loggar till fil
    console_handler = logging.StreamHandler()  # Skapar en handler som skriver loggar till konsolen

    formatter = logging.Formatter(  # Skapar ett format för loggmeddelandena
        "%(asctime)s [%(levelname)s] %(message)s"  # Format: tidsstämpel, loggnivå och meddelande
    )

    file_handler.setFormatter(formatter)  # Kopplar formatteraren till filhanteraren
    console_handler.setFormatter(formatter)  # Kopplar formatteraren till konsolhanteraren

    logger.addHandler(file_handler)  # Lägger till filhanteraren i loggaren
    logger.addHandler(console_handler)  # Lägger till konsolhanteraren i loggaren

    return logger  # Returnerar den konfigurerade loggaren