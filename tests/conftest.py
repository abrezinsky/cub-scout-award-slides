"""Shared fixtures for scout_awards tests."""

import csv
import json
import os

import pytest

# tests/ directory
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(TESTS_DIR, os.pardir))


@pytest.fixture
def sample_csv_path():
    """Path to the real sample.csv in tests/."""
    return os.path.join(TESTS_DIR, "sample.csv")


@pytest.fixture
def award_images_json_path():
    """Path to the real award_images.json shipped with the project."""
    return os.path.join(PROJECT_ROOT, "award_images.json")


@pytest.fixture
def images_dir():
    """Path to the real images/ directory (read-only for rendering tests)."""
    return os.path.join(PROJECT_ROOT, "images")


@pytest.fixture
def tmp_images_dir(tmp_path):
    """A temporary directory for download tests that write files."""
    d = tmp_path / "images"
    d.mkdir()
    return str(d)


@pytest.fixture
def mini_csv(tmp_path):
    """Write a small 3-row CSV to tmp and return the path.

    Two rows share the same scout (Alice Test) to exercise deduplication.
    Third row has leading/trailing whitespace in names to test stripping.
    """
    p = tmp_path / "mini.csv"
    rows = [
        {
            "First Name": "Alice",
            "Last Name": "Test",
            "Den Type": "wolves",
            "Den Number": "1",
            "Quantity": "1",
            "SKU": "111",
            "Item Type": "Adventure",
            "Price": "2.19",
            "Item Name": "Fake Adventure",
            "Date Earned": "2025-01-01",
        },
        {
            "First Name": "Alice",
            "Last Name": "Test",
            "Den Type": "wolves",
            "Den Number": "1",
            "Quantity": "1",
            "SKU": "222",
            "Item Type": "Adventure",
            "Price": "2.19",
            "Item Name": "Another Adventure",
            "Date Earned": "2025-01-02",
        },
        {
            "First Name": "  Bob  ",
            "Last Name": "  Space  ",
            "Den Type": "tigers",
            "Den Number": "2",
            "Quantity": "1",
            "SKU": "333",
            "Item Type": "Misc Awards",
            "Price": "1.99",
            "Item Name": "Some Badge",
            "Date Earned": "2025-01-03",
        },
    ]
    with open(p, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return str(p)


@pytest.fixture
def mini_award_images_json(tmp_path):
    """Write a small JSON with 2 items and return the path."""
    p = tmp_path / "award_images.json"
    data = {
        "items": [
            {"sku": "111", "name": "Fake Award", "imageUrl400": "https://example.com/111.png"},
            {"sku": "222", "name": "Another Award", "imageUrl400": "https://example.com/222.png"},
        ]
    }
    with open(p, "w") as f:
        json.dump(data, f)
    return str(p)


@pytest.fixture
def sample_scout():
    """A single scout dict with a few awards, for renderer tests."""
    return {
        "first": "Test",
        "last": "Scout",
        "den_type": "wolves",
        "den_number": "3",
        "awards": [
            {"sku": "619941", "item_name": "Cubs Who Care Adventure", "item_type": "Adventure"},
            {"sku": "619949", "item_name": "Paws of Skill Adventure", "item_type": "Adventure"},
            {"sku": "660245", "item_name": "Race Time (Wolf) Adventure", "item_type": "Adventure"},
        ],
    }
