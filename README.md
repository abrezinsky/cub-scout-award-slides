# Cub Scout Award Certificate Generator

Generate broadcast-quality 1920x1080 PNG award certificates for Cub Scout Blue and Gold ceremonies, pack meetings, or other recognition events.

Each scout gets a single slide showing their name, den, rank logo, and all earned awards with badge images downloaded automatically from the BSA CDN.

![Example output](example.png)

## Requirements

- Python 3.8+
- [Pillow](https://pillow.readthedocs.io/) (`pip install Pillow`)
- Impact font (falls back to DejaVu Sans Bold if unavailable)

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 generate_awards.py <purchase_order.csv>
python3 generate_awards.py <purchase_order.csv> -o <output_dir>
python3 generate_awards.py <purchase_order.csv> -p awards.pptx
```

Try with the included sample data:

```bash
python3 generate_awards.py sample.csv
```

Options:
- `-o` / `--output-dir` — directory to save PNGs (default: `output/`)
- `-p` / `--pptx` — also generate a PowerPoint file with all slides ordered by rank (Lion, Tiger, Wolf, Bear, Webelos, AOL) then last name

Output PNGs are saved to `output/` by default, with filenames like `wolves_Johnson_Sarah.png`.

## Input CSV

The input CSV is a **Scoutbook purchase order export** — it is not a custom format. To get one:

1. Log in to [Scoutbook](https://scoutbook.scouting.org/)
2. Navigate to your pack's purchase order
3. Export the order as CSV

The CSV has these columns:

| Column | Example | Description |
|--------|---------|-------------|
| First Name | Sarah | Scout's first name |
| Last Name | Johnson | Scout's last name |
| Den Type | wolves | Rank identifier (see below) |
| Den Number | 3 | Den number |
| Quantity | 1 | (unused) |
| SKU | 619941 | Award SKU for image lookup |
| Item Type | Adventure | Award category |
| Price | 2.19 | (unused) |
| Item Name | Cubs Who Care Adventure | Display name |
| Date Earned | 2025-12-01 | (unused) |

### Den Types

`lions`, `tigers`, `wolves`, `bears`, `webelos`, `aol`

### Item Types

- **Adventure** — adventure loop/pin awards (shown in the main grid)
- **Badges of Rank** — rank emblems like Arrow of Light (shown in featured section)
- **Misc Awards** — recruiter strip, etc. (shown in featured section)

## How It Works

1. Parses the CSV and groups awards by scout
2. Downloads badge images from the BSA CDN (cached in `images/`)
3. Generates a 1920x1080 PNG per scout with:
   - Scout name and den info in the header
   - Rank logo in the upper right
   - Featured section for rank badges and special awards
   - Adventure grid (1 or 2 columns based on count)

## Rank Logos

Place rank logo PNGs in `images/` with these names:

- `rank_lion.png`
- `rank_tiger.png`
- `rank_wolf.png`
- `rank_bear.png`
- `rank_webelos.png` (also used for Arrow of Light)

## Award Images

`award_images.json` maps SKUs to badge image URLs. Badge images are automatically downloaded and cached in `images/sku_<SKU>.png` on first run. If a SKU is missing from the JSON, a circular placeholder is generated.
