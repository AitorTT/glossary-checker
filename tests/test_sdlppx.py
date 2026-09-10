import zipfile
from pathlib import Path

import pandas as pd
import pytest

from glossary_checker.core import GlossaryChecker
from glossary_checker.exporters import convert_sdlppx_to_xlsx
from glossary_checker.parsers import get_parser_for_file, parse_sdlppx
from glossary_checker.parsers.sdlppx_parser import parse_sdlppx as parse_sdlppx_direct

REFERENCE_SDLXLIFF = """<?xml version="1.0" encoding="utf-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="mail-admin" source-language="en-US" target-language="gl-ES">
    <body>
      <trans-unit id="1">
        <source>Hello world</source>
        <seg-source><mrk mtype="seg" mid="1">Hello world</mrk></seg-source>
        <target><mrk mtype="seg" mid="1" /></target>
      </trans-unit>
      <trans-unit id="2">
        <source>Save the file</source>
        <seg-source><mrk mtype="seg" mid="2">Save the file</mrk></seg-source>
        <target><mrk mtype="seg" mid="2" /></target>
      </trans-unit>
    </body>
  </file>
</xliff>
"""

TRANSLATED_SDLXLIFF = """<?xml version="1.0" encoding="utf-8"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="mail-admin" source-language="en-US" target-language="gl-ES">
    <body>
      <trans-unit id="1">
        <source>Hello world</source>
        <seg-source><mrk mtype="seg" mid="1">Hello world</mrk></seg-source>
        <target><mrk mtype="seg" mid="1">Ola mundo</mrk></target>
      </trans-unit>
      <trans-unit id="2">
        <source>Save the file</source>
        <seg-source><mrk mtype="seg" mid="2">Save the file</mrk></seg-source>
        <target><mrk mtype="seg" mid="2">Garda o ficheiro</mrk></target>
      </trans-unit>
    </body>
  </file>
</xliff>
"""


def _make_package(path: Path, entries: dict) -> Path:
    with zipfile.ZipFile(path, "w") as z:
        for name, content in entries.items():
            z.writestr(name, content)
    return path


@pytest.fixture
def sdlppx(tmp_path):
    return _make_package(
        tmp_path / "sample.sdlppx",
        {
            "project.sdlproj": "<project/>",
            "en-US/mail-admin_gl-ES.xliff.sdlxliff": REFERENCE_SDLXLIFF,
            "gl-ES/mail-admin_gl-ES.xliff.sdlxliff": TRANSLATED_SDLXLIFF,
        },
    )


def test_registry_returns_sdlppx_parser():
    assert get_parser_for_file(Path("x.sdlppx")) is parse_sdlppx_direct


def test_parse_sdlppx_uses_translated_file(sdlppx):
    segments = parse_sdlppx(sdlppx)

    assert len(segments) == 2
    assert segments[0][1] == "Hello world"
    assert segments[0][2] == "Ola mundo"
    assert segments[1][1] == "Save the file"
    assert segments[1][2] == "Garda o ficheiro"


def test_parse_sdlppx_missing_sdlxliff_raises(tmp_path):
    path = _make_package(tmp_path / "empty.sdlppx", {"project.sdlproj": "<project/>"})
    with pytest.raises(ValueError):
        parse_sdlppx(path)


def test_check_file_on_sdlppx(tmp_path, sdlppx):
    df = pd.DataFrame([["Hello", "Ola"], ["Save", "Garda"]])
    glossary = tmp_path / "glossary.xlsx"
    df.to_excel(glossary, index=False)

    checker = GlossaryChecker(glossary)
    missing = checker.check_file(sdlppx)

    assert missing == []


def test_check_file_on_sdlppx_reports_missing(tmp_path):
    path = _make_package(
        tmp_path / "missing.sdlppx",
        {"gl-ES/doc.sdlxliff": TRANSLATED_SDLXLIFF.replace("Ola mundo", "Boas")},
    )
    df = pd.DataFrame([["Hello", "Ola"]])
    glossary = tmp_path / "glossary.xlsx"
    df.to_excel(glossary, index=False)

    checker = GlossaryChecker(glossary, fuzzy_threshold=95)
    missing = checker.check_file(path)

    assert len(missing) == 1
    assert missing[0]["english_term"] == "hello"


def test_convert_sdlppx_to_xlsx(tmp_path, sdlppx):
    output = tmp_path / "out.xlsx"
    result = convert_sdlppx_to_xlsx(sdlppx, output)

    assert result == output
    assert output.exists()
    df = pd.read_excel(output)
    assert list(df.columns) == ["segment_id", "source", "target"]
    assert df.iloc[0]["target"] == "Ola mundo"
