# Glossary Compliance Checker

A Python tool that verifies translations against an approved glossary. It scans bilingual documents (Excel, SDLXLIFF) and flags segments where glossary terms are missing.

## Features

- **Glossary-driven checking** — Load an English→Spanish glossary from Excel
- **Multi-format support** — Scans Excel (`.xlsx`) and SDLXLIFF (`.sdlxliff`) translation files
- **Smart matching** — Whole-word matching + fuzzy matching (via `rapidfuzz`) catches typos and accent variations
- **Graphical interface** — Built with Tkinter, dark-themed, no web server needed
- **Export reports** — Results to Excel reports with summary statistics
- **Extensible** — Clean parser interface makes adding new file formats easy

## Quick Start

```bash
pip install -r requirements.txt
python run_gui.py
```

Or use the GUI module directly:

```bash
python -m glossary_checker.gui
```

## Usage

1. **Select Glossary** — Browse for an Excel file with English terms in column A and Spanish equivalents in column B
2. **Select Translation File** — Choose a translation file (Excel or SDLXLIFF) to check
3. **Run Check** — Click "Run Compliance Check" to scan all segments
4. **Review & Export** — View missing terms in the results panel, export to Excel

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
│   ├── core.py             # Glossary matching engine
│   ├── gui.py              # Tkinter GUI
│   ├── exporters.py        # Excel/CSV export
│   └── parsers/            # File format parsers
│       ├── excel_parser.py
│       └── sdlxliff_parser.py
├── tests/                  # pytest test suite
├── run_gui.py              # Entry point
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Running Tests

```bash
pip install pytest
pytest
```

## Tech Stack

- **Python 3.10+** — Core logic
- **pandas + openpyxl** — Excel I/O
- **rapidfuzz** — Fuzzy string matching
- **lxml** — XML/SDLXLIFF parsing
- **Tkinter** — Desktop GUI
- **pytest** — Test suite
