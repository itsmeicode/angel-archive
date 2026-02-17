"""
Sonny Angel Gallery Discovery Tool

Discovers all series and gallery IDs from the official Sonny Angel website.
Outputs a gallery_config.json file for use with scrape_images.py.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import sys

PRODUCT_TYPE_URLS = {
    "regular": ("Mini Figure (Regular)", "https://www.sonnyangel.com/en/products/")
    # "gift": ("Mini Figure (Gift)", "https://www.sonnyangel.com/en/products/mini-figure-gift/"),
    # "hippers": ("Mini Figure (Hippers)", "https://www.sonnyangel.com/en/products/mini-figure-hippers/"),
    # "limited": ("Mini Figure (Limited)", "https://www.sonnyangel.com/en/products/mini-figure-limited/"),
    # "artist": ("Artist Collection", "https://www.sonnyangel.com/en/products/artist-collection/"),
    # "master": ("Master Collection", "https://www.sonnyangel.com/en/master-collection/"),
    # "others": ("Others", "https://www.sonnyangel.com/en/products/others/"),
}


def discover_galleries_from_page(url: str) -> list[dict]:
    """Fetch a product page and extract all gallery configurations."""
    print(f"Fetching: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    series_titles = soup.find_all("h2", class_="tabtitle")
    discovered_galleries = []

    for title_tag in series_titles:
        series_name = title_tag.get_text(strip=True)
        tabcontent = title_tag.find_next_sibling("div", class_="tabcontent")

        if not tabcontent:
            print(f"  Warning: No tabcontent found for series '{series_name}'")
            continue

        gallery = tabcontent.find("div", class_="foogallery")

        if not gallery:
            print(f"  Warning: No gallery found for series '{series_name}'")
            continue

        gallery_id = gallery.get("id")

        if not gallery_id:
            print(f"  Warning: Gallery has no ID for series '{series_name}'")
            continue

        discovered_galleries.append({
            "series_name": series_name,
            "url": url,
            "gallery_id": gallery_id
        })

        print(f"  Found: {series_name} (ID: {gallery_id})")

    return discovered_galleries


def discover_all_galleries(selected_types: list[str] = None) -> dict:
    """Discover galleries from all or selected product types."""
    print("Starting gallery discovery...\n")

    if selected_types:
        types_to_scrape = {k: v for k, v in PRODUCT_TYPE_URLS.items() if k in selected_types}
        if not types_to_scrape:
            print("Error: No valid product types selected!")
            print(f"Available types: {', '.join(PRODUCT_TYPE_URLS.keys())}")
            return {}
    else:
        types_to_scrape = PRODUCT_TYPE_URLS

    print(f"Selected product types: {', '.join(types_to_scrape.keys())}\n")

    config = {}
    total_series = 0

    for key, (product_type, url) in types_to_scrape.items():
        print(f"\n{'='*60}")
        print(f"Product Type: {product_type}")
        print(f"{'='*60}")

        galleries = discover_galleries_from_page(url)
        config[product_type] = galleries
        total_series += len(galleries)

        print(f"\nFound {len(galleries)} series in {product_type}\n")
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Discovery Complete!")
    print(f"Total Product Types: {len(config)}")
    print(f"Total Series: {total_series}")
    print(f"{'='*60}\n")

    return config


def save_config(config: dict, output_file: str = "gallery_config.json"):
    """Save gallery configuration to JSON file."""
    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Config written to: {output_file}")


def print_summary(config: dict):
    """Print a summary of discovered galleries."""
    print("\nSummary of Discovered Galleries:")
    print("=" * 60)

    for product_type, galleries in config.items():
        print(f"\n{product_type}: {len(galleries)} series")
        for gallery in galleries:
            print(f"  - {gallery['series_name']}")


def main():
    """Main entry point - discover all galleries and save config."""
    print("\n" + "=" * 60)
    print("Sonny Angel Gallery Discovery Tool")
    print("=" * 60 + "\n")

    if len(sys.argv) > 1:
        selected_types = sys.argv[1].split(",")
    else:
        selected_types = None

    config = discover_all_galleries(selected_types=selected_types)

    if not config:
        return

    save_config(config, output_file="gallery_config.json")
    print_summary(config)

    print("\nNext steps:")
    print("1. Review gallery_config.json")
    print("2. Run: python scrape_images.py")


if __name__ == "__main__":
    main()

