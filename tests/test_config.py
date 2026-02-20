"""Tests for scout_awards.config: constants, clean_award_name, font discovery."""

import os

from scout_awards.config import (
    BAR_HEIGHT,
    FONT_BOLD,
    HEIGHT,
    IMAGES_DIR,
    RANK_COLORS,
    RANK_DISPLAY,
    RANK_ORDER,
    SIDE_MARGIN,
    WIDTH,
    clean_award_name,
)


class TestLayoutConstants:
    def test_width(self):
        assert WIDTH == 1920

    def test_height(self):
        assert HEIGHT == 1080

    def test_bar_height(self):
        assert BAR_HEIGHT == 15

    def test_side_margin(self):
        assert SIDE_MARGIN == 80


class TestRankDefinitions:
    def test_rank_colors_keys(self):
        expected = {"lions", "tigers", "wolves", "bears", "webelos", "aol"}
        assert set(RANK_COLORS.keys()) == expected

    def test_rank_order_length(self):
        assert len(RANK_ORDER) == 6

    def test_rank_order_first(self):
        assert RANK_ORDER[0] == "lions"

    def test_rank_order_last(self):
        assert RANK_ORDER[-1] == "aol"

    def test_rank_display_lion(self):
        assert RANK_DISPLAY["lions"] == "Lion"

    def test_rank_display_aol(self):
        assert RANK_DISPLAY["aol"] == "Arrow of Light"

    def test_rank_display_all_present(self):
        for rank in RANK_ORDER:
            assert rank in RANK_DISPLAY


class TestCleanAwardName:
    def test_strips_adventure_suffix(self):
        assert clean_award_name("Race Time (Wolf) Adventure") == "Race Time (Wolf)"

    def test_strips_emblem_suffix(self):
        assert clean_award_name("Arrow of Light Rank Emblem") == "Arrow of Light Rank"

    def test_passthrough(self):
        assert clean_award_name("Recruiter Strip") == "Recruiter Strip"

    def test_both_suffixes(self):
        """Name ending in ' Adventure' then ' Emblem' — both are stripped."""
        assert clean_award_name("Foo Emblem Adventure") == "Foo"
        assert clean_award_name("Foo Adventure Emblem") == "Foo Adventure"


class TestFontsAndPaths:
    def test_fonts_resolved(self):
        # CI may have different fonts; just check FONT_BOLD is truthy
        assert FONT_BOLD

    def test_images_dir_exists(self):
        assert os.path.isdir(IMAGES_DIR)
