"""Tests for scout_awards.data: CSV loading, award images, sorting, downloading."""

import os

import pytest

from scout_awards.data import download_images, load_award_images, load_csv, sort_scouts


class TestLoadCsv:
    def test_returns_list(self, sample_csv_path):
        result = load_csv(sample_csv_path)
        assert isinstance(result, list)

    def test_scout_count(self, sample_csv_path):
        result = load_csv(sample_csv_path)
        assert len(result) == 8

    def test_scout_keys(self, sample_csv_path):
        result = load_csv(sample_csv_path)
        expected_keys = {"first", "last", "den_type", "den_number", "awards"}
        for scout in result:
            assert set(scout.keys()) == expected_keys

    def test_deduplication(self, mini_csv):
        result = load_csv(mini_csv)
        alice = [s for s in result if s["first"] == "Alice"]
        assert len(alice) == 1
        assert len(alice[0]["awards"]) == 2

    def test_strips_whitespace(self, mini_csv):
        result = load_csv(mini_csv)
        bob = [s for s in result if s["last"] == "Space"]
        assert len(bob) == 1
        assert bob[0]["first"] == "Bob"
        assert bob[0]["last"] == "Space"


class TestLoadAwardImages:
    def test_returns_dict(self, award_images_json_path):
        result = load_award_images(award_images_json_path)
        assert isinstance(result, dict)

    def test_spot_check_sku(self, award_images_json_path):
        result = load_award_images(award_images_json_path)
        assert "619914" in result
        assert result["619914"]["name"] == "Team Tiger"

    def test_value_structure(self, award_images_json_path):
        result = load_award_images(award_images_json_path)
        for sku, item in result.items():
            assert "sku" in item
            assert "name" in item
            assert "imageUrl400" in item

    def test_mini_json(self, mini_award_images_json):
        result = load_award_images(mini_award_images_json)
        assert len(result) == 2
        assert result["111"]["name"] == "Fake Award"


class TestSortScouts:
    def test_rank_order(self):
        scouts = [
            {"first": "A", "last": "A", "den_type": "wolves", "den_number": "1", "awards": []},
            {"first": "B", "last": "B", "den_type": "lions", "den_number": "1", "awards": []},
            {"first": "C", "last": "C", "den_type": "bears", "den_number": "1", "awards": []},
        ]
        sorted_s = sort_scouts(scouts)
        assert [s["den_type"] for s in sorted_s] == ["lions", "wolves", "bears"]

    def test_alpha_within_rank(self):
        scouts = [
            {"first": "Zoe", "last": "Adams", "den_type": "wolves", "den_number": "1", "awards": []},
            {"first": "Amy", "last": "Adams", "den_type": "wolves", "den_number": "1", "awards": []},
            {"first": "Amy", "last": "Baker", "den_type": "wolves", "den_number": "1", "awards": []},
        ]
        sorted_s = sort_scouts(scouts)
        assert [(s["first"], s["last"]) for s in sorted_s] == [
            ("Amy", "Adams"),
            ("Zoe", "Adams"),
            ("Amy", "Baker"),
        ]

    def test_full_sample_order(self, sample_csv_path):
        scouts = load_csv(sample_csv_path)
        sorted_s = sort_scouts(scouts)
        den_types = [s["den_type"] for s in sorted_s]
        # lions < tigers < wolves < bears < webelos < aol
        from scout_awards.config import RANK_ORDER
        rank_idx = {r: i for i, r in enumerate(RANK_ORDER)}
        indices = [rank_idx[d] for d in den_types]
        assert indices == sorted(indices)


class TestDownloadImages:
    def test_cached(self, tmp_images_dir):
        """When image already exists in dir, returns status 'cached' without network call."""
        # Pre-create the cached file
        cached_path = os.path.join(tmp_images_dir, "sku_999.png")
        with open(cached_path, "wb") as f:
            f.write(b"fake png data")

        scouts = [
            {"first": "X", "last": "Y", "den_type": "wolves", "den_number": "1",
             "awards": [{"sku": "999", "item_name": "Test", "item_type": "Adventure"}]},
        ]
        result = download_images(scouts, {}, tmp_images_dir)
        assert result["999"]["status"] == "cached"
        assert result["999"]["path"] == cached_path

    def test_placeholder(self, tmp_images_dir):
        """SKU not in sku_map generates placeholder PNG."""
        scouts = [
            {"first": "X", "last": "Y", "den_type": "wolves", "den_number": "1",
             "awards": [{"sku": "000", "item_name": "Missing", "item_type": "Adventure"}]},
        ]
        result = download_images(scouts, {}, tmp_images_dir)
        assert result["000"]["status"] == "placeholder"
        assert os.path.exists(result["000"]["path"])
        # Verify it's a valid image
        from PIL import Image
        img = Image.open(result["000"]["path"])
        assert img.size == (400, 400)
