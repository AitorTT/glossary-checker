"""Parser for TMX (Translation Memory eXchange) files."""
from pathlib import Path
from typing import List, Tuple
from lxml import etree


def parse_tmx(path: Path, preserve_tags: bool = False) -> List[Tuple[int, str, str]]:
    """
    Parse a .tmx file and extract translation units as aligned segments.

    TMX files contain <tu> elements, each with <tuv> children keyed by
    xml:lang. The parser groups TUVs by the first two distinct languages
    found (typically source and target).

    Args:
        path: Path to .tmx file
        preserve_tags: If True, preserve inline XML tags as [tag]...[/tag]

    Returns:
        List of (segment_id, source_text, target_text) tuples
    """
    tree = etree.parse(str(path))
    root = tree.getroot()

    translation_units = root.xpath('//tu')

    if not translation_units:
        translation_units = root.findall('.//tu')

    segments = []
    seg_counter = 0

    for tu in translation_units:
        try:
            tuvs = tu.xpath('.//tuv')
            if not tuvs:
                tuvs = tu.findall('.//tuv')

            if len(tuvs) < 2:
                continue

            langs_seen = []
            lang_texts = {}

            for tuv in tuvs:
                lang = tuv.get('{http://www.w3.org/XML/1998/namespace}lang')
                if lang is None:
                    lang = tuv.get('xml:lang')
                if lang is None:
                    lang = tuv.get('lang')

                seg_elem = tuv.find('seg')
                if seg_elem is None:
                    continue

                text = _get_seg_text(seg_elem, preserve_tags)
                if not text:
                    continue

                lang_key = lang.lower().split('-')[0] if lang else ''

                if lang_key not in lang_texts:
                    lang_texts[lang_key] = text
                    langs_seen.append(lang_key)

            if len(langs_seen) >= 2:
                source_text = lang_texts[langs_seen[0]]
                target_text = lang_texts[langs_seen[1]]
                if source_text:
                    segments.append((seg_counter, source_text, target_text))
                    seg_counter += 1

        except Exception:
            continue

    return segments


def _get_seg_text(element, preserve_tags: bool = False) -> str:
    """Extract text from a <seg> element."""
    if element is None:
        return ""

    if preserve_tags:
        text_parts = [element.text or ""]
        for child in element:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            text_parts.append(f'[{tag}]')
            if child.text:
                text_parts.append(child.text)
            text_parts.append(f'[/{tag}]')
            if child.tail:
                text_parts.append(child.tail)
        text = ''.join(text_parts).strip()
    else:
        text = ''.join(element.itertext()).strip()

    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')

    return text
