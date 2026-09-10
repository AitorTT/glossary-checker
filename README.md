# Glossary Compliance Checker

A Python tool that verifies translations against an approved glossary. It scans bilingual documents (Excel, SDLXLIFF, Trados packages, MemoQ, XLIFF, TMX, SDLTM) and flags segments where glossary terms are missing, mistranslated, or inconsistent — helping translators and reviewers maintain terminology consistency.

## Features

- **Glossary-driven checking** — Load an English→Spanish glossary from Excel
- **Multi-format support** — Scans Excel (`.xlsx`), SDLXLIFF (`.sdlxliff`), Trados packages (`.sdlppx`), MemoQ (`.mqxlz`), XLIFF (`.xlf`), TMX (`.tmx`), and SDLTM (`.sdltm`) translation files
- **File conversion** — Convert SDLXLIFF, Trados packages, or MemoQ exports to aligned Excel for easy review
- **Smart matching** — Whole-word matching + fuzzy matching (via `rapidfuzz`) catches typos and accent variations
- **Graphical interface** — Built with Tkinter, dark-themed, no web server needed
- **Web interface** — Flask-based web UI for browser-based usage
- **Export reports** — Results to Excel/CSV reports with summary statistics
- **Extensible** — Clean parser interface makes adding new file formats easy

## Quick Start

### Desktop GUI

```bash
pip install -e .
python run_gui.py
```

Or use the GUI module directly:

```bash
python -m glossary_checker.gui
```

### Web Interface

```bash
pip install -e ".[web]"
python run_web.py
```

Then open http://localhost:5000 in your browser.

For production deployment (e.g., Render, Railway):

```bash
pip install -e ".[web]"
gunicorn glossary_checker.web:app
```

## Usage

1. **Select Glossary** — Browse for an Excel file with English terms in column A and Spanish equivalents in column B
2. **Select Translation File** — Choose a translation file (Excel, SDLXLIFF, Trados package `.sdlppx`, MemoQ, XLIFF, TMX, or SDLTM) to check
3. **Run Check** — Click "Run Compliance Check" to scan all segments
4. **Review & Export** — View missing terms in the results panel, export to Excel or CSV

You can also convert bilingual files to aligned Excel without running a compliance check — useful for reviewing translations outside Trados or MemoQ.

### Glossary Format

Your glossary Excel should have two columns:

| English | Spanish |
|---------|---------|
| button | botón |
| start | iniciar, comenzar |
| save | guardar |

Multiple Spanish synonyms can be comma-separated.

## Project Structure

```
glossary_checker/
├── glossary_checker/       # Main package
│   ├── config.py            # Centralized configuration
│   ├── core.py              # Glossary matching engine
│   ├── gui.py               # Tkinter GUI
│   ├── web.py               # Flask web interface
│   ├── exporters.py         # Excel/CSV export + file conversions
│   ├── parsers/             # File format parsers
│   │   ├── excel_parser.py
│   │   ├── sdlxliff_parser.py
│   │   ├── sdlppx_parser.py
│   │   └── mqxliff_parser.py
│   ├── templates/           # Flask HTML templates
│   │   ├── layout.html
│   │   ├── index.html
│   │   └── results.html
│   └── static/              # CSS & assets
│       └── style.css
├── tests/                   # pytest test suite
├── run_gui.py               # Desktop entry point
├── run_web.py               # Web entry point
├── pyproject.toml
└── README.md
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## Tech Stack

- **Python 3.10+** — Core logic
- **pandas + openpyxl** — Excel I/O
- **rapidfuzz** — Fuzzy string matching
- **lxml** — XML/XLIFF parsing
- **Flask** — Web interface
- **Tkinter** — Desktop GUI
- **pytest** — Test suite
