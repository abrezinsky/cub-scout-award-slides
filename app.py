"""Flask web app for generating Cub Scout award certificates."""

import io
import os
import tempfile
import zipfile

from flask import Flask, jsonify, render_template, request, send_file

from scout_awards import IMAGES_DIR, load_award_images, load_csv, sort_scouts
from scout_awards import download_images, generate_scout_image, generate_pptx

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

# Pre-load static SKU map once at import time
_AWARD_IMAGES_PATH = os.path.join(os.path.dirname(__file__), "award_images.json")
SKU_MAP = load_award_images(_AWARD_IMAGES_PATH)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/generate", methods=["POST"])
def generate():
    # --- Validate upload ---
    if "file" not in request.files:
        return jsonify(error="No file uploaded"), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify(error="No file selected"), 400
    if not file.filename.lower().endswith(".csv"):
        return jsonify(error="File must be a .csv"), 400

    # --- Read form options ---
    theme = request.form.get("theme", "dark")
    fmt = request.form.get("format", "pptx")
    light = theme == "light"

    # Derive download name from uploaded filename (strip .csv, add _pres)
    stem = os.path.splitext(file.filename)[0]
    ext = "pptx" if fmt == "pptx" else "zip"
    download_name = f"{stem}_pres.{ext}"

    # --- Save CSV to temp file (load_csv expects a path) ---
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_csv = tmp.name
            file.save(tmp)

        scouts = load_csv(tmp_csv)
        if not scouts:
            return jsonify(error="No scout data found in CSV"), 400

        sorted_scouts = sort_scouts(scouts)
        download_images(sorted_scouts, SKU_MAP, IMAGES_DIR)

        if fmt == "pptx":
            return _generate_pptx_response(sorted_scouts, light, download_name)
        else:
            return _generate_zip_response(sorted_scouts, light, download_name)

    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        try:
            os.unlink(tmp_csv)
        except OSError:
            pass


def _generate_pptx_response(sorted_scouts, light, download_name):
    """Generate PPTX and return as download."""
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp:
        tmp_pptx = tmp.name

    try:
        generate_pptx(tmp_pptx, sorted_scouts, IMAGES_DIR, light=light)
        buf = io.BytesIO()
        with open(tmp_pptx, "rb") as f:
            buf.write(f.read())
        buf.seek(0)
    finally:
        try:
            os.unlink(tmp_pptx)
        except OSError:
            pass

    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        as_attachment=True,
        download_name=download_name,
    )


def _generate_zip_response(sorted_scouts, light, download_name):
    """Generate ZIP of PNGs and return as download."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for scout in sorted_scouts:
            img = generate_scout_image(scout, IMAGES_DIR, light=light)
            png_buf = io.BytesIO()
            img.save(png_buf, format="PNG")
            den = scout["den_type"]
            filename = f"{den}_{scout['last']}_{scout['first']}.png"
            zf.writestr(filename, png_buf.getvalue())
    buf.seek(0)

    return send_file(
        buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name=download_name,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
