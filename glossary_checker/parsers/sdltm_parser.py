"""Parser for SDL Trados Translation Memory files (.sdltm).

SDLTM files are SQLite databases. The schema varies between versions
but typically contains translation_units with source and target segments.
"""
import html
import sqlite3
from pathlib import Path
from typing import List, Tuple
from xml.etree import ElementTree


def parse_sdltm(path: Path) -> List[Tuple[int, str, str]]:
    """
    Parse a .sdltm file (SDL Trados Translation Memory database).

    Attempts to locate translation data across common SDLTM schema variants.

    Args:
        path: Path to .sdltm file

    Returns:
        List of (segment_id, source_text, target_text) tuples
    """
    conn = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row

    try:
        segments = _try_translation_units(conn)
        if segments:
            return segments

        segments = _try_entries(conn)
        if segments:
            return segments

        segments = _try_discover(conn)
        return segments

    finally:
        conn.close()


def _find_text_column(columns: List[str], keyword: str) -> str:
    """Find the best column for source or target text.
    
    Prefers columns containing 'segment' over other matches (e.g. 'hash').
    """
    cols_lower = {c.lower(): c for c in columns}
    kw = keyword.lower()

    exact = cols_lower.get(f'{kw}_segment')
    if exact:
        return exact

    segment_matches = [c for cl, c in cols_lower.items() if f'{kw}_segment' in cl]
    if segment_matches:
        return segment_matches[0]

    all_matches = [c for cl, c in cols_lower.items() if kw in cl]
    if all_matches:
        return all_matches[0]

    return None


def _extract_sdltm_text(raw: str) -> str:
    """Extract text from SDLTM XML segment format.
    
    The segment value in SDLTM looks like:
    <Segment><Elements><Text><Value>actual text</Value></Text></Elements>...</Segment>
    
    Returns the plain text if it's XML, or the raw string if not.
    """
    if not raw:
        return ""

    text = raw.strip()
    if not text.startswith('<Segment'):
        return text

    try:
        root = ElementTree.fromstring(text)
        value = root.find('.//Value')
        if value is not None and value.text:
            return html.unescape(value.text.strip())
    except ElementTree.ParseError:
        pass

    return text


def _try_translation_units(conn: sqlite3.Connection) -> List[Tuple[int, str, str]]:
    """Try the common translation_units table schema."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='translation_units'"
    )
    if not cursor.fetchone():
        return []

    columns = _get_columns(conn, 'translation_units')

    source_col = _find_text_column(columns, 'source')
    target_col = _find_text_column(columns, 'target')

    if not source_col or not target_col:
        return []

    segments = []
    rows = conn.execute(
        f'SELECT [{source_col}], [{target_col}] FROM translation_units'
    ).fetchall()
    for idx, row in enumerate(rows):
        src = _extract_sdltm_text(row[0] or '')
        tgt = _extract_sdltm_text(row[1] or '')
        if src:
            segments.append((idx, src, tgt))

    return segments


def _try_entries(conn: sqlite3.Connection) -> List[Tuple[int, str, str]]:
    """Try older SDLTM schema with an entries-like table."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='entries'"
    )
    if not cursor.fetchone():
        return []

    columns = _get_columns(conn, 'entries')

    source_col = _find_text_column(columns, 'source')
    target_col = _find_text_column(columns, 'target')

    if not source_col or not target_col:
        return []

    segments = []
    rows = conn.execute(
        f'SELECT [{source_col}], [{target_col}] FROM entries'
    ).fetchall()
    for idx, row in enumerate(rows):
        src = _extract_sdltm_text(row[0] or '')
        tgt = _extract_sdltm_text(row[1] or '')
        if src:
            segments.append((idx, src, tgt))

    return segments


def _try_discover(conn: sqlite3.Connection) -> List[Tuple[int, str, str]]:
    """Brute-force: scan all tables for columns containing source/target text."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        columns = _get_columns(conn, table)
        source_col = _find_text_column(columns, 'source')
        target_col = _find_text_column(columns, 'target')

        if not source_col or not target_col:
            continue

        try:
            rows = conn.execute(
                f'SELECT [{source_col}], [{target_col}] FROM [{table}]'
            ).fetchall()
            segments = []
            for idx, row in enumerate(rows):
                src = _extract_sdltm_text(row[0] or '')
                tgt = _extract_sdltm_text(row[1] or '')
                if src:
                    segments.append((idx, src, tgt))
            if segments:
                return segments
        except sqlite3.OperationalError:
            continue

    return []


def _get_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    """Get column names for a table."""
    cursor = conn.execute(f'PRAGMA table_info([{table}])')
    return [row['name'] for row in cursor.fetchall()]
