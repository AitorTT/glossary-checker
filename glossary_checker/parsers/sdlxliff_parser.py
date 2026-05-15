"""SDLXLIFF file parser for Trados Studio translation files."""
from pathlib import Path
from typing import List, Tuple
from lxml import etree


def parse_sdlxliff(path: Path) -> List[Tuple[int, str, str]]:
    """
    Parse SDLXLIFF file (Trados Studio format).
    
    Extracts source text from <seg-source> and target text from <target>.
    Handles multiple <mrk> segments within a single <trans-unit>.
    
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
                    source_text = get_element_text(source_by_mid[mid])
                    target_text = get_element_text(target_by_mid.get(mid))
                    if source_text:
                        segments.append((seg_counter, source_text, target_text))
                        seg_counter += 1
            elif source_fallback and target_fallback:
                source_text = get_element_text(source_fallback[0]) if source_fallback else ""
                target_text = get_element_text(target_fallback[0]) if target_fallback else ""
                if source_text:
                    segments.append((seg_counter, source_text, target_text))
                    seg_counter += 1
                    
        except Exception:
            continue
    
    return segments


def get_element_text(element) -> str:
    """Extract clean text from an XML element."""
    if element is None:
        return ""
    
    # Get the text content
    text_parts = []
    
    # Get element's own text
    if element.text:
        text_parts.append(element.text)
    
    # Process child elements (like g, ph, etc.)
    for child in element:
        # Recursively get child text if it has content
        if child.text:
            text_parts.append(child.text)
        if child.tail:
            text_parts.append(child.tail)
    
    # Join and clean
    text = ' '.join(text_parts).strip()
    
    # Remove XML entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    
    return text
