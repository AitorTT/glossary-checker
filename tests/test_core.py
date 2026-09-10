import pytest
from pathlib import Path
import pandas as pd
from glossary_checker.core import GlossaryChecker


def test_word_boundary_pattern():
    pattern = GlossaryChecker._word_boundary_pattern("test")
    assert pattern == r'\btest\b'


def test_load_glossary(tmp_path):
    df = pd.DataFrame([["button", "botón"], ["start", "iniciar, comenzar"]])
    path = tmp_path / "glossary.xlsx"
    df.to_excel(path, index=False)

    checker = GlossaryChecker(path)
    assert "button" in checker.glossary
    assert checker.glossary["button"] == ["botón"]
    assert checker.glossary["start"] == ["iniciar", "comenzar"]


def test_check_segment_exact_match(tmp_path):
    df = pd.DataFrame([["button", "botón"]])
    path = tmp_path / "glossary.xlsx"
    df.to_excel(path, index=False)

    checker = GlossaryChecker(path)
    missing = checker.check_segment("Click the button", "Haz clic en el botón", 0)

    assert len(missing) == 0


def test_check_segment_missing(tmp_path):
    df = pd.DataFrame([["button", "botón"]])
    path = tmp_path / "glossary.xlsx"
    df.to_excel(path, index=False)

    checker = GlossaryChecker(path)
    missing = checker.check_segment("Click the button", "Haz clic", 0)

    assert len(missing) == 1
    assert missing[0]['english_term'] == "button"
    assert missing[0]['expected_spanish'] == ["botón"]


def test_fuzzy_match_typo(tmp_path):
    df = pd.DataFrame([["button", "botón"]])
    path = tmp_path / "glossary.xlsx"
    df.to_excel(path, index=False)

    checker = GlossaryChecker(path, fuzzy_threshold=80)
    missing = checker.check_segment("Click the button", "Haz clic en el boton", 0)

    assert len(missing) == 0


def test_case_insensitive_matching(tmp_path):
    df = pd.DataFrame([["Button", "Botón"]])
    path = tmp_path / "glossary.xlsx"
    df.to_excel(path, index=False)

    checker = GlossaryChecker(path)
    missing = checker.check_segment("Click the BUTTON", "Haz clic en el botón", 0)

    assert len(missing) == 0


def test_get_statistics(tmp_path):
    df = pd.DataFrame([["button", "botón"], ["start", "iniciar"]])
    path = tmp_path / "glossary.xlsx"
    df.to_excel(path, index=False)

    checker = GlossaryChecker(path)
    missing = checker.check_segment("Click the button to start", "Haz clic", 0)

    stats = checker.get_statistics(missing)
    assert stats['total_missing'] == 2
    assert stats['most_common_term'] is not None
