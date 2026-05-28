"""Flask web interface for Glossary Checker."""
import os
import uuid
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, send_file, flash, redirect, url_for

from .core import GlossaryChecker
from .exporters import export_to_excel, export_to_csv, convert_sdlxliff_to_xlsx, convert_mqxlz_to_xlsx, convert_tmx_to_xlsx, convert_sdltm_to_xlsx, convert_xlf_to_xlsx

CONVERTERS = {
    ".sdlxliff": convert_sdlxliff_to_xlsx,
    ".mqxlz": convert_mqxlz_to_xlsx,
    ".xlf": convert_xlf_to_xlsx,
    ".tmx": convert_tmx_to_xlsx,
    ".sdltm": convert_sdltm_to_xlsx,
}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", uuid.uuid4().hex)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

ALLOWED_GLOSSARY_EXT = {".xlsx", ".xls"}
ALLOWED_TRANSLATION_EXT = {".xlsx", ".xls", ".sdlxliff", ".mqxlz", ".xlf", ".tmx", ".sdltm"}

_results_cache: dict[str, list[dict]] = {}


def _ext_ok(filename: str, allowed: set) -> bool:
    return Path(filename).suffix.lower() in allowed


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert_file", methods=["POST"])
def convert_file():
    uploaded = request.files.get("file")

    if not uploaded:
        flash("Please select a file to convert.", "error")
        return redirect(url_for("index"))

    ext = Path(uploaded.filename).suffix.lower()
    converter = CONVERTERS.get(ext)

    if not converter:
        flash(f"Unsupported file format: {ext}", "error")
        return redirect(url_for("index"))

    tmpdir = Path(tempfile.mkdtemp(prefix="convert_"))

    try:
        input_path = tmpdir / uploaded.filename
        uploaded.save(input_path)

        output_path = converter(input_path)
        out_name = Path(uploaded.filename).stem + "_aligned.xlsx"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=out_name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        flash(f"Conversion error: {e}", "error")
        return redirect(url_for("index"))
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


@app.route("/check", methods=["POST"])
def check():
    glossary_file = request.files.get("glossary")
    translation_file = request.files.get("translation")

    if not glossary_file or not translation_file:
        flash("Please select both a glossary and a translation file.", "error")
        return redirect(url_for("index"))

    if not _ext_ok(glossary_file.filename, ALLOWED_GLOSSARY_EXT):
        flash("Glossary must be an Excel file (.xlsx or .xls).", "error")
        return redirect(url_for("index"))

    if not _ext_ok(translation_file.filename, ALLOWED_TRANSLATION_EXT):
        flash("Translation file must be Excel, SDLXLIFF, XLIFF, TMX, or SDLTM.", "error")
        return redirect(url_for("index"))

    tmpdir = Path(tempfile.mkdtemp(prefix="glossary_"))

    try:
        glossary_path = tmpdir / glossary_file.filename
        glossary_file.save(glossary_path)

        translation_path = tmpdir / translation_file.filename
        translation_file.save(translation_path)

        checker = GlossaryChecker(glossary_path)
        results = checker.check_file(translation_path)

        result_id = uuid.uuid4().hex
        _results_cache[result_id] = results

        stats = checker.get_statistics(results)

        return render_template("results.html",
                               result_id=result_id,
                               results=results,
                               stats=stats,
                               glossary_name=glossary_file.filename,
                               translation_name=translation_file.filename)

    except Exception as e:
        flash(f"Conversion error: {e}", "error")
        return redirect(url_for("index"))
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


@app.route("/convert_xlf", methods=["POST"])
def convert_xlf():
    xlf_file = request.files.get("xlf")

    if not xlf_file:
        flash("Please select an XLIFF (.xlf) file.", "error")
        return redirect(url_for("index"))

    if Path(xlf_file.filename).suffix.lower() != ".xlf":
        flash("File must be an XLIFF (.xlf).", "error")
        return redirect(url_for("index"))

    tmpdir = Path(tempfile.mkdtemp(prefix="convert_"))

    try:
        input_path = tmpdir / xlf_file.filename
        xlf_file.save(input_path)

        output_path = convert_xlf_to_xlsx(input_path)
        out_name = Path(xlf_file.filename).stem + "_aligned.xlsx"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=out_name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        flash(f"Conversion error: {e}", "error")
        return redirect(url_for("index"))
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


@app.route("/export/<result_id>/<fmt>")
def export(result_id: str, fmt: str):
    results = _results_cache.get(result_id)
    if results is None:
        flash("Results not found (expired or invalid link).", "error")
        return redirect(url_for("index"))

    tmp = Path(tempfile.mkdtemp(prefix="glossary_export_"))

    try:
        if fmt == "xlsx":
            out = tmp / "glossary_report.xlsx"
            export_to_excel(results, out)
            mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif fmt == "csv":
            out = tmp / "glossary_report.csv"
            export_to_csv(results, out)
            mimetype = "text/csv"
        else:
            flash("Unsupported format.", "error")
            return redirect(url_for("index"))

        return send_file(out, as_attachment=True, download_name=out.name, mimetype=mimetype)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


@app.route("/convert", methods=["POST"])
def convert():
    sdlxliff_file = request.files.get("sdlxliff")

    if not sdlxliff_file:
        flash("Please select an SDLXLIFF file.", "error")
        return redirect(url_for("index"))

    if Path(sdlxliff_file.filename).suffix.lower() != ".sdlxliff":
        flash("File must be an SDLXLIFF (.sdlxliff).", "error")
        return redirect(url_for("index"))

    tmpdir = Path(tempfile.mkdtemp(prefix="convert_"))

    try:
        input_path = tmpdir / sdlxliff_file.filename
        sdlxliff_file.save(input_path)

        output_path = convert_sdlxliff_to_xlsx(input_path)
        out_name = Path(sdlxliff_file.filename).stem + "_aligned.xlsx"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=out_name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        flash(f"Conversion error: {e}", "error")
        return redirect(url_for("index"))
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


@app.route("/convert_mqxlz", methods=["POST"])
def convert_mqxlz():
    mqxlz_file = request.files.get("mqxlz")

    if not mqxlz_file:
        flash("Please select a MemoQ (.mqxlz) file.", "error")
        return redirect(url_for("index"))

    if Path(mqxlz_file.filename).suffix.lower() != ".mqxlz":
        flash("File must be a MemoQ export (.mqxlz).", "error")
        return redirect(url_for("index"))

    tmpdir = Path(tempfile.mkdtemp(prefix="convert_"))

    try:
        input_path = tmpdir / mqxlz_file.filename
        mqxlz_file.save(input_path)

        output_path = convert_mqxlz_to_xlsx(input_path)
        out_name = Path(mqxlz_file.filename).stem + "_aligned.xlsx"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=out_name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        flash(f"Conversion error: {e}", "error")
        return redirect(url_for("index"))
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


@app.route("/convert_tmx", methods=["POST"])
def convert_tmx():
    tmx_file = request.files.get("tmx")

    if not tmx_file:
        flash("Please select a TMX (.tmx) file.", "error")
        return redirect(url_for("index"))

    if Path(tmx_file.filename).suffix.lower() != ".tmx":
        flash("File must be a TMX export (.tmx).", "error")
        return redirect(url_for("index"))

    tmpdir = Path(tempfile.mkdtemp(prefix="convert_"))

    try:
        input_path = tmpdir / tmx_file.filename
        tmx_file.save(input_path)

        output_path = convert_tmx_to_xlsx(input_path)
        out_name = Path(tmx_file.filename).stem + "_aligned.xlsx"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=out_name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        flash(f"Conversion error: {e}", "error")
        return redirect(url_for("index"))
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


@app.route("/convert_sdltm", methods=["POST"])
def convert_sdltm():
    sdltm_file = request.files.get("sdltm")

    if not sdltm_file:
        flash("Please select an SDLTM (.sdltm) file.", "error")
        return redirect(url_for("index"))

    if Path(sdltm_file.filename).suffix.lower() != ".sdltm":
        flash("File must be an SDL Trados TM (.sdltm).", "error")
        return redirect(url_for("index"))

    tmpdir = Path(tempfile.mkdtemp(prefix="convert_"))

    try:
        input_path = tmpdir / sdltm_file.filename
        sdltm_file.save(input_path)

        output_path = convert_sdltm_to_xlsx(input_path)
        out_name = Path(sdltm_file.filename).stem + "_aligned.xlsx"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=out_name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        flash(f"Conversion error: {e}", "error")
        return redirect(url_for("index"))
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)
