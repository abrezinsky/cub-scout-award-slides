"""Tests for the Flask web app (app.py)."""

import io
import zipfile

import pytest
from PIL import Image

from app import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _upload(client, csv_path, theme="dark", fmt="pptx"):
    """Helper: POST /generate with a CSV file and options."""
    with open(csv_path, "rb") as f:
        data = {
            "file": (f, "upload.csv"),
            "theme": theme,
            "format": fmt,
        }
        return client.post(
            "/generate",
            data=data,
            content_type="multipart/form-data",
        )


class TestIndex:
    def test_status(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_contains_title(self, client):
        resp = client.get("/")
        assert b"Cub Scout Award Presentation" in resp.data


class TestHealth:
    def test_status(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_json(self, client):
        resp = client.get("/health")
        assert resp.get_json() == {"status": "ok"}


class TestGenerateValidation:
    def test_no_file(self, client):
        resp = client.post("/generate", data={})
        assert resp.status_code == 400
        assert "No file uploaded" in resp.get_json()["error"]

    def test_empty_filename(self, client):
        data = {"file": (io.BytesIO(b""), "")}
        resp = client.post(
            "/generate", data=data, content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "No file selected" in resp.get_json()["error"]

    def test_non_csv(self, client):
        data = {"file": (io.BytesIO(b"hello"), "data.txt")}
        resp = client.post(
            "/generate", data=data, content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "csv" in resp.get_json()["error"].lower()

    def test_empty_csv(self, client, tmp_path):
        """A CSV with headers but no data rows should return 400."""
        p = tmp_path / "empty.csv"
        p.write_text(
            "First Name,Last Name,Den Type,Den Number,SKU,Item Type,Item Name\n"
        )
        resp = _upload(client, str(p))
        assert resp.status_code == 400
        assert "No scout data" in resp.get_json()["error"]


class TestGeneratePptx:
    def test_returns_pptx(self, client, sample_csv_path):
        resp = _upload(client, sample_csv_path, fmt="pptx")
        assert resp.status_code == 200
        assert "presentationml" in resp.content_type

    def test_pptx_is_valid(self, client, sample_csv_path):
        resp = _upload(client, sample_csv_path, fmt="pptx")
        from pptx import Presentation
        prs = Presentation(io.BytesIO(resp.data))
        assert len(prs.slides) > 0

    def test_pptx_light_theme(self, client, sample_csv_path):
        resp = _upload(client, sample_csv_path, theme="light", fmt="pptx")
        assert resp.status_code == 200


class TestGenerateZip:
    def test_returns_zip(self, client, sample_csv_path):
        resp = _upload(client, sample_csv_path, fmt="zip")
        assert resp.status_code == 200
        assert resp.content_type == "application/zip"

    def test_zip_contains_pngs(self, client, sample_csv_path):
        resp = _upload(client, sample_csv_path, fmt="zip")
        with zipfile.ZipFile(io.BytesIO(resp.data)) as zf:
            names = zf.namelist()
            assert len(names) > 0
            assert all(n.endswith(".png") for n in names)

    def test_zip_images_are_valid(self, client, sample_csv_path):
        resp = _upload(client, sample_csv_path, fmt="zip")
        with zipfile.ZipFile(io.BytesIO(resp.data)) as zf:
            for name in zf.namelist():
                img = Image.open(io.BytesIO(zf.read(name)))
                assert img.size == (1920, 1080)

    def test_zip_light_theme(self, client, sample_csv_path):
        resp = _upload(client, sample_csv_path, fmt="zip")
        assert resp.status_code == 200


class TestDefaultFormat:
    def test_defaults_to_pptx(self, client, sample_csv_path):
        """When format is omitted, should default to pptx."""
        with open(sample_csv_path, "rb") as f:
            data = {"file": (f, "upload.csv")}
            resp = client.post(
                "/generate", data=data, content_type="multipart/form-data",
            )
        assert resp.status_code == 200
        assert "presentationml" in resp.content_type
