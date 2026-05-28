"""Parser for standard XLIFF files (.xlf)."""
from pathlib import Path
from typing import List, Tuple
from lxml import etree
from .sdlxliff_parser import get_element_text


XLF_NS = 'urn:oasis:names:tc:xliff:document:1.2'


def parse_xlf(path: Path, preserve_tags: bool = False) -> List[Tuple[int, str, str]]:
    """
    Parse a standard .xlf file (XLIFF 1.2) and extract segments.

    Args:
        path: Path to .xlf file
        preserve_tags: If True, preserve inline XML tags as [tag]...[/tag]

    Returns:
        List of (segment_id, source_text, target_text) tuples
    """
    tree = etree.parse(str(path))
    root = tree.getroot()

    trans_units = root.xpath('//ns:trans-unit', namespaces={'ns': XLF_NS})
    if not trans_units:
        trans_units = root.xpath('//trans-unit')

    segments = []

    for idx, tu in enumerate(trans_units):
        try:
            source_elem = tu.find(f'{{{XLF_NS}}}source')
            target_elem = tu.find(f'{{{XLF_NS}}}target')

            if source_elem is None:
                source_elem = tu.find('source')
            if target_elem is None:
                target_elem = tu.find('target')

            source_text = get_element_text(source_elem, preserve_tags) if source_elem is not None else ""
            target_text = get_element_text(target_elem, preserve_tags) if target_elem is not None else ""

            if source_text:
                segments.append((idx, source_text, target_text))

        except Exception:
            continue

    return segments
