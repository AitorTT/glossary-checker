"""SDLXLIFF file parser for Trados Studio translation files."""
from pathlib import Path
from typing import List, Tuple
from lxml import etree


def parse_sdlxliff(path: Path) -> List[Tuple[int, str, str]]:
    """
    Parse SDLXLIFF file (Trados Studio format).
    
    Extracts source text from <seg-source> and target text from <target>.
    Both are expected to contain <mrk> elements with segment text.
    
    Returns:
        List of (segment_id, source_text, target_text) tuples
    """
    tree = etree.parse(str(path))
    root = tree.getroot()
    
    # Find namespace
    ns_map = root.nsmap
    xliff_ns = ns_map.get(None) if None in ns_map else 'urn:oasis:names:tc:xliff:document:1.2'
    
    segments = []
    
    # Find all trans-unit elements
    trans_units = root.xpath('//ns:trans-unit', namespaces={'ns': xliff_ns})
    
    if not trans_units:
        # Fallback without namespace
        trans_units = root.xpath('//trans-unit')
        ns_aware = False
    else:
        ns_aware = True
    
    for idx, tu in enumerate(trans_units):
        try:
            # Extract source using filters
            if ns_aware:
                source_elements = tu.xpath('.//ns:seg-source//ns:mrk', namespaces={'ns': xliff_ns})
                target_elements = tu.xpath('.//ns:target//ns:mrk', namespaces={'ns': xliff_ns})
                
                # Fallback if filters don't match
                if not source_elements:
                    source_elements = tu.xpath('.//ns:source', namespaces={'ns': xliff_ns})
                if not target_elements:
                    target_elements = tu.xpath('.//ns:target', namespaces={'ns': xliff_ns})
            else:
                source_elements = tu.xpath('.//seg-source//mrk')
                target_elements = tu.xpath('.//target//mrk')
                
                if not source_elements:
                    source_elements = tu.xpath('.//source')
                if not target_elements:
                    target_elements = tu.xpath('.//target')
            
            # Extract text
            source_text = get_element_text(source_elements[0]) if source_elements else ""
            target_text = get_element_text(target_elements[0]) if target_elements else ""
            
            if source_text and target_text:
                segments.append((idx, source_text, target_text))
            
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
