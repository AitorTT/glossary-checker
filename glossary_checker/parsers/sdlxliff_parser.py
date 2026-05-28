"""SDLXLIFF file parser for Trados Studio translation files."""
import html
from pathlib import Path
from typing import List, Tuple
from lxml import etree


def parse_sdlxliff(path: Path, preserve_tags: bool = False) -> List[Tuple[int, str, str]]:
    """
    Parse SDLXLIFF file (Trados Studio format).
    
    Extracts source text from <seg-source> and target text from <target>.
    Handles multiple <mrk> segments within a single <trans-unit>.
    
    Args:
        path: Path to .sdlxliff file
        preserve_tags: If True, preserve inline XML tags as [tag]...[/tag]
    
    Returns:
        List of (segment_id, source_text, target_text) tuples
    """
    tree = etree.parse(str(path))
    root = tree.getroot()
    
    # Find namespace
    ns_map = root.nsmap
    xliff_ns = ns_map.get(None) if None in ns_map else 'urn:oasis:names:tc:xliff:document:1.2'
    
    segments = []
    seg_counter = 0
    
    # Find all trans-unit elements
    trans_units = root.xpath('//ns:trans-unit', namespaces={'ns': xliff_ns})
    
    if not trans_units:
        trans_units = root.xpath('//trans-unit')
        ns_aware = False
    else:
        ns_aware = True
    
    for tu in trans_units:
        try:
            if ns_aware:
                source_mrks = tu.xpath('.//ns:seg-source//ns:mrk', namespaces={'ns': xliff_ns})
                target_mrks = tu.xpath('.//ns:target//ns:mrk', namespaces={'ns': xliff_ns})
                source_fallback = tu.xpath('.//ns:source', namespaces={'ns': xliff_ns})
                target_fallback = tu.xpath('.//ns:target', namespaces={'ns': xliff_ns})
            else:
                source_mrks = tu.xpath('.//seg-source//mrk')
                target_mrks = tu.xpath('.//target//mrk')
                source_fallback = tu.xpath('.//source')
                target_fallback = tu.xpath('.//target')
            
            # If there are mrk elements, process each one
            if source_mrks and target_mrks:
                # Build mid-to-element maps for pairing
                source_by_mid = {m.get('mid'): m for m in source_mrks if m.get('mid')}
                target_by_mid = {m.get('mid'): m for m in target_mrks if m.get('mid')}
                
                for mid in source_by_mid:
                    source_text = get_element_text(source_by_mid[mid], preserve_tags)
                    target_text = get_element_text(target_by_mid.get(mid), preserve_tags)
                    if source_text:
                        segments.append((seg_counter, source_text, target_text))
                        seg_counter += 1
            elif source_fallback and target_fallback:
                source_text = get_element_text(source_fallback[0], preserve_tags) if source_fallback else ""
                target_text = get_element_text(target_fallback[0], preserve_tags) if target_fallback else ""
                if source_text:
                    segments.append((seg_counter, source_text, target_text))
                    seg_counter += 1
                    
        except Exception:
            continue
    
    return segments


def get_element_text(element, preserve_tags: bool = False) -> str:
    """Extract text from an XML element.
    
    Args:
        element: lxml element
        preserve_tags: If True, preserve inline XML tags as [tag]...[/tag]
    
    Returns:
        Clean text string
    """
    if element is None:
        return ""
    
    if preserve_tags:
        text = _serialize_tags(element)
    else:
        text_parts = []
        if element.text:
            text_parts.append(element.text)
        for child in element:
            if child.text:
                text_parts.append(child.text)
            if child.tail:
                text_parts.append(child.tail)
        text = ' '.join(text_parts).strip()
    
    text = html.unescape(text)
    
    return text


def _serialize_tags(element) -> str:
    """Serialize XML inline tags as [tag]...[/tag] recursively."""
    parts = []
    if element.text:
        parts.append(element.text)
    for child in element:
        tag = child.tag.split('}')[-1]
        attrs = ' '.join(f'{k}="{v}"' for k, v in child.attrib.items())
        if attrs:
            parts.append(f'[{tag} {attrs}]')
        else:
            parts.append(f'[{tag}]')
        parts.append(_serialize_tags(child))
        parts.append(f'[/{tag}]')
        if child.tail:
            parts.append(child.tail)
    return ''.join(parts)
