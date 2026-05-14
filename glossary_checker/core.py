"""Core glossary checking logic."""
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from rapidfuzz import fuzz
from .parsers import get_parser_for_file


class GlossaryChecker:
    """Check if translations contain required glossary terms."""
    
    def __init__(self, glossary_path: Path, fuzzy_threshold: int = 85):
        """
        Initialize checker with glossary.
        
        Args:
            glossary_path: Excel file with EN (col0) and ES (col1) terms
            fuzzy_threshold: 0-100, minimum similarity for fuzzy matching
        """
        self.glossary = self._load_glossary(glossary_path)
        self.fuzzy_threshold = fuzzy_threshold
    
    def _load_glossary(self, path: Path) -> Dict[str, List[str]]:
        """Load glossary from Excel. Returns {english_term: [spanish_equivalents]}."""
        df = pd.read_excel(path)
        glossary = {}
        
        for _, row in df.iterrows():
            en_term = str(row.iloc[0]).strip().lower()
            es_terms_raw = str(row.iloc[1])
            
            # Handle comma-separated synonyms
            if ',' in es_terms_raw:
                es_terms = [t.strip().lower() for t in es_terms_raw.split(',')]
            else:
                es_terms = [es_terms_raw.strip().lower()]
            
            glossary[en_term] = es_terms
        
        return glossary
    
    @staticmethod
    def _word_boundary_pattern(word: str) -> str:
        """Create regex pattern for whole-word matching."""
        return rf'\b{re.escape(word)}\b'
    
    def check_segment(self, en_text: str, es_text: str, segment_id: int) -> List[dict]:
        """
        Check a single translation segment.
        
        Returns list of missing terms with context.
        """
        en_text_lower = en_text.lower()
        es_text_lower = es_text.lower()
        missing = []
        
        for en_term, es_equivalents in self.glossary.items():
            # Check if English term appears (whole word only)
            pattern = self._word_boundary_pattern(en_term)
            if not re.search(pattern, en_text_lower):
                continue
            
            # Check if ANY Spanish equivalent appears
            found = False
            for es_term in es_equivalents:
                # Exact match with word boundaries
                es_pattern = self._word_boundary_pattern(es_term)
                if re.search(es_pattern, es_text_lower):
                    found = True
                    break
                
                # Fuzzy match for typos/variations (partial: term anywhere in text)
                if fuzz.partial_ratio(es_term, es_text_lower) >= self.fuzzy_threshold:
                    found = True
                    break
            
            if not found:
                missing.append({
                    'segment_id': segment_id,
                    'english_term': en_term,
                    'expected_spanish': es_equivalents,
                    'english_context': self._truncate(en_text, 80),
                    'spanish_context': self._truncate(es_text, 80),
                    'full_english': en_text,
                    'full_spanish': es_text
                })
        
        return missing
    
    def check_file(self, source_path: Path) -> List[dict]:
        """
        Check entire translation file.
        
        Args:
            source_path: Translation file (Excel, SDLXLIFF, etc.)
        """
        parser = get_parser_for_file(source_path)
        
        if parser is None:
            raise ValueError(f"Unsupported file format: {source_path.suffix}")
        
        segments = parser(source_path)
        all_missing = []
        
        for seg_id, en_text, es_text in segments:
            if not en_text or not es_text:
                continue
                
            missing = self.check_segment(en_text, es_text, seg_id)
            all_missing.extend(missing)
        
        return all_missing
    
    @staticmethod
    def _truncate(text: str, max_len: int) -> str:
        """Truncate text and add ellipsis if needed."""
        if len(text) <= max_len:
            return text
        return text[:max_len] + '...'
    
    def get_statistics(self, missing: List[dict]) -> dict:
        """Generate statistics from results."""
        if not missing:
            return {
                'total_missing': 0,
                'unique_terms': [],
                'most_common_term': None,
                'segments_affected': []
            }
        
        from collections import Counter
        term_counts = Counter(item['english_term'] for item in missing)
        segments = sorted(set(item['segment_id'] for item in missing))
        
        return {
            'total_missing': len(missing),
            'unique_terms': list(term_counts.keys()),
            'most_common_term': term_counts.most_common(1)[0] if term_counts else None,
            'segments_affected': segments,
            'term_frequencies': dict(term_counts)
        }
