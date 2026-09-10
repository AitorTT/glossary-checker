"""Export results to various formats."""
from pathlib import Path
from typing import List
import pandas as pd
from .parsers import parse_sdlxliff, parse_sdlppx, parse_mqxlz, parse_tmx, parse_sdltm, parse_xlf


def export_to_excel(missing_terms: List[dict], output_path: Path) -> Path:
    """
    Export missing terms to Excel report.
    
    Args:
        missing_terms: List of missing term dicts from GlossaryChecker
        output_path: Where to save the Excel file
    
    Returns:
        The output path (for chaining)
    """
    if not missing_terms:
        # Create empty report
        df = pd.DataFrame(columns=[
            'segment_id', 'english_term', 'expected_spanish',
            'english_context', 'spanish_context', 'full_english', 'full_spanish'
        ])
    else:
        df = pd.DataFrame(missing_terms)
        # Convert list columns to strings for Excel
        df['expected_spanish'] = df['expected_spanish'].apply(lambda x: ', '.join(x))
    
    # Reorder columns for readability
    column_order = [
        'segment_id', 'english_term', 'expected_spanish',
        'english_context', 'spanish_context'
    ]
    df = df[column_order]
    
    # Add summary sheet
    output_path = Path(output_path)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Missing Terms', index=False)
        
        # Summary sheet
        summary_data = {
            'Metric': ['Total Missing Terms', 'Segments Affected', 'Unique Terms'],
            'Value': [
                len(missing_terms),
                len(set(t['segment_id'] for t in missing_terms)) if missing_terms else 0,
                len(set(t['english_term'] for t in missing_terms)) if missing_terms else 0
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    
    return output_path


def export_to_csv(missing_terms: List[dict], output_path: Path) -> Path:
    """Export to CSV for spreadsheet apps."""
    if not missing_terms:
        df = pd.DataFrame(columns=['segment_id', 'english_term', 'expected_spanish', 'english_context', 'spanish_context'])
    else:
        df = pd.DataFrame(missing_terms)
        df['expected_spanish'] = df['expected_spanish'].apply(lambda x: ', '.join(x))
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    return output_path


def export_summary_text(missing_terms: List[dict]) -> str:
    """Generate human-readable summary text."""
    if not missing_terms:
        return "✓ No missing glossary terms found! Perfect compliance."
    
    unique_terms = set(t['english_term'] for t in missing_terms)
    segments = sorted(set(t['segment_id'] for t in missing_terms))
    
    lines = [
        f"❌ Found {len(missing_terms)} missing glossary terms",
        f"   Affects {len(segments)} segments",
        f"   {len(unique_terms)} unique terms missing",
        "",
        "Most frequently missing terms:"
    ]
    
    from collections import Counter
    term_counts = Counter(t['english_term'] for t in missing_terms)
    for term, count in term_counts.most_common(5):
        lines.append(f"   • '{term}' missing {count} times")
    
    return '\n'.join(lines)


def convert_sdlxliff_to_xlsx(sdlxliff_path: Path, output_path: Path = None) -> Path:
    """
    Convert SDLXLIFF file to aligned Excel file.
    
    Args:
        sdlxliff_path: Path to .sdlxliff file
        output_path: Optional output path (defaults to same name with .xlsx)
    
    Returns:
        Path to the created Excel file
    """
    if output_path is None:
        output_path = sdlxliff_path.with_suffix('.xlsx')
    
    segments = parse_sdlxliff(sdlxliff_path, preserve_tags=True)
    
    df = pd.DataFrame(segments, columns=['segment_id', 'source', 'target'])
    df.to_excel(output_path, index=False, sheet_name='Translation')
    
    return output_path


def convert_mqxlz_to_xlsx(mqxlz_path: Path, output_path: Path = None) -> Path:
    """
    Convert MemoQ .mqxlz file to aligned Excel file.
    
    Args:
        mqxlz_path: Path to .mqxlz file
        output_path: Optional output path (defaults to same name with .xlsx)
    
    Returns:
        Path to the created Excel file
    """
    if output_path is None:
        output_path = mqxlz_path.with_suffix('.xlsx')
    
    segments = parse_mqxlz(mqxlz_path, preserve_tags=True)
    
    df = pd.DataFrame(segments, columns=['segment_id', 'source', 'target'])
    df.to_excel(output_path, index=False, sheet_name='Translation')
    
    return output_path


def convert_sdlppx_to_xlsx(sdlppx_path: Path, output_path: Path = None) -> Path:
    """
    Convert a Trados Studio package (.sdlppx) to an aligned Excel file.

    Args:
        sdlppx_path: Path to .sdlppx file
        output_path: Optional output path (defaults to same name with .xlsx)

    Returns:
        Path to the created Excel file
    """
    if output_path is None:
        output_path = sdlppx_path.with_suffix('.xlsx')

    segments = parse_sdlppx(sdlppx_path, preserve_tags=True)

    df = pd.DataFrame(segments, columns=['segment_id', 'source', 'target'])
    df.to_excel(output_path, index=False, sheet_name='Translation')

    return output_path


def convert_tmx_to_xlsx(tmx_path: Path, output_path: Path = None) -> Path:
    """
    Convert TMX file to aligned Excel file.

    Args:
        tmx_path: Path to .tmx file
        output_path: Optional output path (defaults to same name with .xlsx)

    Returns:
        Path to the created Excel file
    """
    if output_path is None:
        output_path = tmx_path.with_suffix('.xlsx')

    segments = parse_tmx(tmx_path)

    df = pd.DataFrame(segments, columns=['segment_id', 'source', 'target'])
    df.to_excel(output_path, index=False, sheet_name='Translation')

    return output_path


def convert_sdltm_to_xlsx(sdltm_path: Path, output_path: Path = None) -> Path:
    """
    Convert SDLTM file to aligned Excel file.

    Args:
        sdltm_path: Path to .sdltm file
        output_path: Optional output path (defaults to same name with .xlsx)

    Returns:
        Path to the created Excel file
    """
    if output_path is None:
        output_path = sdltm_path.with_suffix('.xlsx')

    segments = parse_sdltm(sdltm_path)

    df = pd.DataFrame(segments, columns=['segment_id', 'source', 'target'])
    df.to_excel(output_path, index=False, sheet_name='Translation')

    return output_path


def convert_xlf_to_xlsx(xlf_path: Path, output_path: Path = None) -> Path:
    """
    Convert XLIFF .xlf file to aligned Excel file.

    Args:
        xlf_path: Path to .xlf file
        output_path: Optional output path (defaults to same name with .xlsx)

    Returns:
        Path to the created Excel file
    """
    if output_path is None:
        output_path = xlf_path.with_suffix('.xlsx')

    segments = parse_xlf(xlf_path, preserve_tags=True)

    df = pd.DataFrame(segments, columns=['segment_id', 'source', 'target'])
    df.to_excel(output_path, index=False, sheet_name='Translation')

    return output_path
