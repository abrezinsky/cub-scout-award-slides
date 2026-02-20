"""Pre-download all badge images from award_images.json.

Run during `docker build` so that download_images() is a no-op at runtime
for all known SKUs.
"""

import json
import os
import urllib.request

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")


def main():
    with open(os.path.join(os.path.dirname(__file__), "award_images.json")) as f:
        data = json.load(f)

    os.makedirs(IMAGES_DIR, exist_ok=True)
    total = len(data["items"])

    for i, item in enumerate(data["items"], 1):
        sku = item["sku"]
        url = item.get("imageUrl400", "")
        dest = os.path.join(IMAGES_DIR, f"sku_{sku}.png")

        if os.path.exists(dest):
            continue

        if not url:
            print(f"  [{i}/{total}] SKU {sku}: no URL, skipping")
            continue

        try:
            urllib.request.urlretrieve(url, dest)
            print(f"  [{i}/{total}] SKU {sku}: downloaded")
        except Exception as e:
            print(f"  [{i}/{total}] SKU {sku}: FAILED ({e})")


if __name__ == "__main__":
    main()
