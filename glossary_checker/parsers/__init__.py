"""File parsers for different translation file formats."""
from pathlib import Path
from typing import List, Tuple
from .excel_parser import parse_excel
from .sdlxliff_parser import parse_sdlxliff
from .mqxliff_parser import parse_mqxlz


def get_parser_for_file(path: Path):
    """
    Get appropriate parser function for file extension.
    
    Returns:
        Parser function or None if unsupported
    """
    ext = path.suffix.lower()
    
    parsers = {
        '.xlsx': parse_excel,
        '.xls': parse_excel,
        '.sdlxliff': parse_sdlxliff,
        '.mqxlz': parse_mqxlz,
    }
    
    return parsers.get(ext)
