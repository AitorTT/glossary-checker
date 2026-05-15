"""Parser for MemoQ bilingual exports (.mqxlz / .mqxliff)."""
import zipfile
from pathlib import Path
from typing import List, Tuple
from lxml import etree
from .sdlxliff_parser import get_element_text


def parse_mqxlz(path: Path) -> List[Tuple[int, str, str]]:
    """
    Parse a .mqxlz file (MemoQ export) and extract segments.
    
    The .mqxlz is a zip containing a document.mqxliff (XLIFF 1.2).
    
    Returns:
        List of (segment_id, source_text, target_text) tuples
    """
    with zipfile.ZipFile(path, 'r') as z:
        content = z.read('document.mqxliff')

    root = etree.fromstring(content)
    xliff_ns = 'urn:oasis:names:tc:xliff:document:1.2'

    trans_units = root.xpath('//ns:trans-unit', namespaces={'ns': xliff_ns})
    segments = []

    for idx, tu in enumerate(trans_units):
        try:
            source_elem = tu.find(f'{{{xliff_ns}}}source')
            target_elem = tu.find(f'{{{xliff_ns}}}target')

            source_text = get_element_text(source_elem) if source_elem is not None else ""
            target_text = get_element_text(target_elem) if target_elem is not None else ""

            if source_text:
                segments.append((idx, source_text, target_text))

        except Exception:
            continue

    return segments
