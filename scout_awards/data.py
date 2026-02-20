"""Data loading: CSV parsing, award image catalog, image downloading."""

import csv
import json
import os
import textwrap
import urllib.request

from PIL import Image, ImageDraw, ImageFont

from .config import FONT_BOLD, RANK_ORDER


def load_award_images(path):
    """Load award_images.json and build SKU -> {name, imageUrl400} dict."""
    with open(path) as f:
        data = json.load(f)
    sku_map = {}
    for item in data["items"]:
        sku_map[item["sku"]] = item
    return sku_map


def load_csv(path):
    """Parse CSV, return list of scout dicts.

    Each dict has keys: first, last, den_type, den_number, awards.
    """
    scouts = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["First Name"].strip(), row["Last Name"].strip())
            if key not in scouts:
                scouts[key] = {
                    "first": key[0],
                    "last": key[1],
                    "den_type": row["Den Type"].strip(),
                    "den_number": row["Den Number"].strip(),
                    "awards": [],
                }
            scouts[key]["awards"].append({
                "sku": row["SKU"].strip(),
                "item_name": row["Item Name"].strip(),
                "item_type": row["Item Type"].strip(),
            })
    return list(scouts.values())


def sort_scouts(scouts):
    """Sort scouts by rank order, then last name, then first name."""
    rank_index = {r: i for i, r in enumerate(RANK_ORDER)}
    return sorted(
        scouts,
        key=lambda s: (rank_index.get(s["den_type"], 99), s["last"].lower(), s["first"].lower()),
    )


def download_images(scouts, sku_map, images_dir):
    """Download badge images for all unique SKUs, caching in images_dir.

    Returns a dict of {sku: {"path": str, "status": "cached"|"downloaded"|"placeholder"|"failed"}}.
    """
    os.makedirs(images_dir, exist_ok=True)
    all_skus = set()
    for scout in scouts:
        for award in scout["awards"]:
            all_skus.add(award["sku"])

    results = {}
    for sku in sorted(all_skus):
        dest = os.path.join(images_dir, f"sku_{sku}.png")
        if os.path.exists(dest):
            results[sku] = {"path": dest, "status": "cached"}
            continue

        source = sku_map.get(sku)
        if source:
            name = source.get("name", f"SKU {sku}")
            url = source.get("imageUrl400", "")
            try:
                urllib.request.urlretrieve(url, dest)
                results[sku] = {"path": dest, "status": "downloaded"}
            except Exception:
                _generate_placeholder(dest, name, sku)
                results[sku] = {"path": dest, "status": "failed"}
        else:
            _generate_placeholder(dest, f"SKU {sku}", sku)
            results[sku] = {"path": dest, "status": "placeholder"}

    return results


def _generate_placeholder(path, name, sku):
    """Generate a simple circular placeholder badge."""
    size = 400
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw circle
    margin = 20
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=(0, 63, 135),
        outline=(255, 199, 44),
        width=4,
    )
    # Draw text
    font = ImageFont.truetype(FONT_BOLD, 32)
    lines = name.split("\n") if "\n" in name else textwrap.wrap(name, width=14)
    y = size // 2 - len(lines) * 20
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((size - tw) // 2, y), line, fill="white", font=font)
        y += 40
    img.save(path)
