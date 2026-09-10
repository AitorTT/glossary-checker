"""File parsers for different translation file formats."""
from pathlib import Path
from typing import List, Tuple
from .excel_parser import parse_excel
from .sdlxliff_parser import parse_sdlxliff
from .sdlppx_parser import parse_sdlppx
from .mqxliff_parser import parse_mqxlz
from .xlf_parser import parse_xlf
from .tmx_parser import parse_tmx
from .sdltm_parser import parse_sdltm


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
        '.sdlppx': parse_sdlppx,
        '.mqxlz': parse_mqxlz,
        '.xlf': parse_xlf,
        '.tmx': parse_tmx,
        '.sdltm': parse_sdltm,
    }
    
    return parsers.get(ext)
