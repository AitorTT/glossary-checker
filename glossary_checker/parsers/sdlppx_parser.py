"""Parser for Trados Studio project packages (.sdlppx)."""
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple
from lxml import etree
from .sdlxliff_parser import parse_sdlxliff_bytes


def parse_sdlppx(path: Path, preserve_tags: bool = False) -> List[Tuple[int, str, str]]:
    """
    Parse a Trados Studio project package (.sdlppx).

    A .sdlppx is a zip archive that bundles one or more bilingual
    .sdlxliff files, usually one per project language folder. Each package
    also contains a source-language reference copy whose targets are empty;
    those are skipped so only real translations are returned.

    Args:
        path: Path to .sdlppx file
        preserve_tags: If True, preserve inline XML tags as [tag]...[/tag]

    Returns:
        List of (segment_id, source_text, target_text) tuples, with segment
        ids numbered continuously across all bundled files.
    """
    with zipfile.ZipFile(path, 'r') as z:
        names = [n for n in z.namelist() if n.lower().endswith('.sdlxliff')]

        if not names:
            raise ValueError(f"No .sdlxliff files found inside package: {path.name}")

        entries = []
        for name in names:
            content = z.read(name)
            entries.append((name, content, _header_target_language(content)))

    candidates = _select_bilingual_entries(entries)

    segments = []
    seg_counter = 0
    for _name, content in candidates:
        file_segments = parse_sdlxliff_bytes(content, preserve_tags)
        if not any(target for _sid, _src, target in file_segments):
            continue
        for _sid, source, target in file_segments:
            segments.append((seg_counter, source, target))
            seg_counter += 1

    return segments


def _header_target_language(content: bytes) -> Optional[str]:
    """Read the target-language attribute from an SDLXLIFF header."""
    try:
        root = etree.fromstring(content)
    except Exception:
        return None

    for element in root.iter():
        lang = element.get('target-language')
        if lang:
            return lang
    return None


def _select_bilingual_entries(entries):
    """Prefer files stored under their own target-language folder.

    Trados packages keep an empty reference copy in the source-language
    folder and the real bilingual file in the target-language folder. When
    that layout is detected, only the target-language files are returned.
    Otherwise all entries are returned and empty-target files are filtered
    out later.
    """
    preferred = [
        (name, content)
        for name, content, target_lang in entries
        if target_lang and _top_folder(name) == target_lang
    ]
    if preferred:
        return preferred
    return [(name, content) for name, content, _ in entries]


def _top_folder(name: str) -> str:
    """Return the first path component of a zip entry (or empty string)."""
    parts = Path(name).parts
    return parts[0] if len(parts) > 1 else ''
