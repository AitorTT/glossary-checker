"""Excel file parser for aligned source/target text."""
from pathlib import Path
from typing import List, Tuple
import pandas as pd


def parse_excel(path: Path) -> List[Tuple[int, str, str]]:
    """
    Parse Excel file with aligned source/target text.
    
    Returns:
        List of (segment_id, source_text, target_text) tuples
    """
    df = pd.read_excel(path)
    segments = []
    
    for idx, row in df.iterrows():
        source = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        target = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
        
        if source and target:
            segments.append((idx, source, target))
    
    return segments
