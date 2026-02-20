#!/usr/bin/env python3
"""CLI for generating Cub Scout award certificate PNGs and PPTX presentations."""

import argparse
import os
import sys

from scout_awards import (
    IMAGES_DIR, PACKAGE_DIR,
    load_award_images, load_csv, download_images, sort_scouts,
    generate_scout_image, generate_pptx,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate 1920x1080 award certificate PNGs for Cub Scouts.",
        epilog="The input CSV is exported from a Scoutbook purchase order. "
               "Required columns: First Name, Last Name, Den Type, Den Number, "
               "SKU, Item Type, Item Name.",
    )
    parser.add_argument(
        "csv", metavar="purchase_order.csv",
        help="CSV file exported from a Scoutbook purchase order",
    )
    parser.add_argument(
        "-o", "--output-dir", default=os.path.join(SCRIPT_DIR, "output"),
        help="directory to save generated PNGs (default: output/)",
    )
    parser.add_argument(
        "-p", "--pptx", metavar="FILE",
        help="also generate a PowerPoint presentation with all slides",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    csv_path = args.csv
    if not os.path.isabs(csv_path):
        csv_path = os.path.join(os.getcwd(), csv_path)

    if not os.path.exists(csv_path):
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)

    output_dir = args.output_dir
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(os.getcwd(), output_dir)

    images_json_path = os.path.join(SCRIPT_DIR, "award_images.json")
    images_dir = IMAGES_DIR

    print("Loading award_images.json...")
    sku_map = load_award_images(images_json_path)
    print(f"  Loaded {len(sku_map)} award image entries")

    print(f"Loading CSV: {csv_path}")
    scouts = load_csv(csv_path)
    print(f"  Found {len(scouts)} scouts")

    print("Downloading/caching badge images...")
    results = download_images(scouts, sku_map, images_dir)
    for sku in sorted(results):
        info = results[sku]
        if info["status"] == "downloaded":
            source = sku_map.get(sku)
            name = source.get("name", f"SKU {sku}") if source else f"SKU {sku}"
            print(f"  Downloaded SKU {sku} ({name})")
        elif info["status"] == "placeholder":
            print(f"  No image source for SKU {sku}, generated placeholder")
        elif info["status"] == "failed":
            print(f"  Warning: Failed to download SKU {sku}, using placeholder")

    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating certificate images in {output_dir}/...")

    sorted_scouts = sort_scouts(scouts)

    for scout in sorted_scouts:
        img = generate_scout_image(scout, images_dir)
        filename = f"{scout['den_type']}_{scout['last']}_{scout['first']}.png"
        out_path = os.path.join(output_dir, filename)
        img.save(out_path)
        award_count = len(scout["awards"])
        print(f"  {filename} ({award_count} award{'s' if award_count != 1 else ''})")

    print(f"\nDone! Generated {len(sorted_scouts)} images in {output_dir}/")

    if args.pptx:
        pptx_path = args.pptx
        if not os.path.isabs(pptx_path):
            pptx_path = os.path.join(os.getcwd(), pptx_path)
        print(f"Generating PowerPoint: {pptx_path}...")
        generate_pptx(pptx_path, sorted_scouts, images_dir)
        print(f"  {len(sorted_scouts)} slides written.")


if __name__ == "__main__":
    main()
