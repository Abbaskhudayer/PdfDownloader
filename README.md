# PDF Downloader / PDF-nedladdare

## English/Swedish

### Overview

This project is a Python-based PDF downloader and scraper built with Playwright.

It opens a website, collects relevant internal pages, extracts the main content, builds a cleaner printable HTML version, and exports each page as a PDF.

The goal is to create readable PDFs that are easier to save, review, and copy text from than a raw browser print.

### Features

- Opens pages with Playwright
- Collects internal links
- Visits each page automatically
- Extracts the main content area
- Cleans up exported content for better readability
- Exports one PDF per page
- Creates logs during execution
- Handles errors per page so the full run does not stop immediately

### Project structure

```text
PdfDownloader/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── logger_setup.py
│   ├── main.py
│   ├── models.py
│   ├── pdf_exporter.py
│   ├── scraper.py
│   └── utils.py
├── output/
├── logs/
├── requirements.txt
├── .gitignore
└── README.md
```

### Requirements

Before running the project, install:

- Python 3.11 or later
- Visual Studio Code
- VS Code Python extension
- Playwright for Python

Recommended:

- Pylance extension in VS Code

### Getting started in VS Code

#### 1. Open the project

Open the project folder in Visual Studio Code.

#### 2. Create a virtual environment

Open the terminal in VS Code and run:

```bash
python -m venv .venv
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

If you use Command Prompt instead:

```cmd
.venv\Scripts\activate
```

#### 3. Install dependencies

Run:

```bash
pip install -r requirements.txt
```

Then install Playwright browsers:

```bash
playwright install
```

### How to run the project

From the project root, run:

```bash
python src/main.py
```

If your system uses `py` instead of `python`, run:

```bash
py src/main.py
```

### Output

Generated PDF files are saved in:

```text
output/
```

Logs are saved in:

```text
logs/run.log
```

### Configuration

Main settings are stored in:

```text
src/config.py
```

This is where you typically adjust things such as:

- base URL
- selectors
- timeouts
- PDF settings
- content extraction behavior

### Notes

This project is designed as a reusable PDF scraping/export tool.

It can be adapted for other websites, but some pages may require updates to:

- selectors
- link filtering
- content extraction rules
- login handling
- waiting logic

### Troubleshooting

#### Python is not recognized

Make sure Python is installed and available in PATH.

Check with:

```bash
python --version
```

or:

```bash
py --version
```

#### Playwright does not start

Make sure you have installed dependencies and browsers:

```bash
pip install -r requirements.txt
playwright install
```

#### PowerShell blocks activation

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

---

## Svenska

### Översikt

Detta projekt är en PDF-nedladdare och scraper byggd i Python med Playwright.

Programmet öppnar en webbplats, samlar relevanta interna sidor, extraherar huvudinnehållet, bygger en renare utskriftsvänlig HTML-version och exporterar varje sida som PDF.

Målet är att skapa lättlästa PDF-filer som är enklare att spara, läsa och kopiera text från än en vanlig browser-utskrift.

### Funktioner

- Öppnar sidor med Playwright
- Samlar interna länkar
- Besöker varje sida automatiskt
- Extraherar sidans huvudinnehåll
- Städar upp innehållet för bättre läsbarhet
- Exporterar en PDF per sida
- Skapar loggar under körning
- Hanterar fel per sida så att hela körningen inte avbryts direkt

### Projektstruktur

```text
PdfDownloader/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── logger_setup.py
│   ├── main.py
│   ├── models.py
│   ├── pdf_exporter.py
│   ├── scraper.py
│   └── utils.py
├── output/
├── logs/
├── requirements.txt
├── .gitignore
└── README.md
```

### Krav

Innan projektet körs behöver följande vara installerat:

- Python 3.11 eller senare
- Visual Studio Code
- Python-tillägget i VS Code
- Playwright för Python

Rekommenderas även:

- Pylance i VS Code

### Kom igång i VS Code

#### 1. Öppna projektet

Öppna projektmappen i Visual Studio Code.

#### 2. Skapa en virtuell miljö

Öppna terminalen i VS Code och kör:

```bash
python -m venv .venv
```

I Windows PowerShell aktiverar du den med:

```powershell
.venv\Scripts\Activate.ps1
```

Om PowerShell blockerar aktiveringen, kör:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Om du använder Command Prompt i stället:

```cmd
.venv\Scripts\activate
```

#### 3. Installera beroenden

Kör:

```bash
pip install -r requirements.txt
```

Installera sedan Playwrights browsers:

```bash
playwright install
```

### Så kör du projektet

Från projektroten, kör:

```bash
python src/main.py
```

Om din dator använder `py` i stället för `python`, kör:

```bash
py src/main.py
```

### Output

Skapade PDF-filer sparas i:

```text
output/
```

Loggar sparas i:

```text
logs/run.log
```

### Konfiguration

De viktigaste inställningarna finns i:

```text
src/config.py
```

Där justerar man normalt sådant som:

- start-URL
- selectors
- timeouts
- PDF-inställningar
- regler för innehållsextrahering

### Kommentar

Projektet är byggt som ett återanvändbart verktyg för PDF-export och scraping.

Det går att anpassa till andra webbplatser, men vissa sidor kan kräva ändringar i:

- selectors
- filtrering av länkar
- regler för innehållsextrahering
- inloggningsflöde
- väntelogik

### Felsökning

#### Python känns inte igen

Kontrollera att Python är installerat och finns i PATH.

Testa med:

```bash
python --version
```

eller:

```bash
py --version
```

#### Playwright startar inte

Kontrollera att du har installerat både beroenden och browsers:

```bash
pip install -r requirements.txt
playwright install
```

#### PowerShell blockerar aktivering

Kör:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

och försök sedan aktivera miljön igen.
