#!/usr/bin/env python3
"""
Upload images to Supabase Storage.

Run from the backend directory:
    python scripts/upload_images.py

Expects images in ../scraper/images/, ../scraper/images_bw/, etc.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "angels")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Paths relative to backend directory
SCRAPER_DIR = Path(__file__).parent.parent.parent / "scraper"
IMAGE_FOLDERS = ["images", "images_bw", "images_opacity", "images_profile_pic"]


def upload_file(local_path: Path, storage_path: str) -> bool:
    """Upload a single file to Supabase Storage."""
    try:
        with open(local_path, "rb") as f:
            file_data = f.read()
        
        # Normalize path separators for storage
        storage_path = storage_path.replace("\\", "/")
        
        result = supabase.storage.from_(BUCKET_NAME).upload(
            storage_path,
            file_data,
            file_options={"content-type": "image/png", "upsert": "true"}
        )
        
        print(f"✓ Uploaded: {storage_path}")
        return True
    except Exception as e:
        print(f"✗ Error uploading {storage_path}: {e}")
        return False


def upload_directory(local_dir: Path, storage_prefix: str = "") -> tuple[int, int]:
    """Recursively upload a directory to storage. Returns (success, failed) counts."""
    success = 0
    failed = 0
    
    if not local_dir.exists():
        print(f"Directory not found: {local_dir}")
        return 0, 0
    
    for item in local_dir.iterdir():
        if item.is_dir():
            s, f = upload_directory(item, f"{storage_prefix}/{item.name}" if storage_prefix else item.name)
            success += s
            failed += f
        elif item.is_file() and item.suffix.lower() == ".png":
            storage_path = f"{storage_prefix}/{item.name}" if storage_prefix else item.name
            if upload_file(item, storage_path):
                success += 1
            else:
                failed += 1
    
    return success, failed


def main():
    print(f"Uploading images to Supabase Storage bucket: {BUCKET_NAME}")
    print(f"Scraper directory: {SCRAPER_DIR}")
    print("-" * 50)
    
    total_success = 0
    total_failed = 0
    
    for folder in IMAGE_FOLDERS:
        folder_path = SCRAPER_DIR / folder
        if folder_path.exists():
            print(f"\nProcessing {folder}/...")
            success, failed = upload_directory(folder_path, folder)
            total_success += success
            total_failed += failed
        else:
            print(f"\nSkipping {folder}/ (not found)")
    
    print("-" * 50)
    print(f"Done! Uploaded: {total_success}, Failed: {total_failed}")


if __name__ == "__main__":
    main()

