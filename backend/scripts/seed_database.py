import os
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

SCRAPER_DIR = Path(__file__).parent.parent.parent / "scraper"
IMAGES_DIR = SCRAPER_DIR / "images"


def format_series_name(folder_name: str) -> str:
    """Convert folder name to display name (e.g., 'Fruit_2019_Series' -> 'Fruit 2019 Series')."""
    return folder_name.replace("_", " ")


def format_angel_name(filename: str) -> str:
    """Convert filename to angel name (e.g., 'Apple.png' -> 'Apple')."""
    name = Path(filename).stem
    name = re.sub(r"^\d+[-_]", "", name)
    name = name.replace("_", " ")
    return name


def get_or_create_series(name: str) -> int:
    """Get existing series ID or create new series."""
    result = supabase.table("series").select("id").eq("name", name).execute()
    if result.data:
        return result.data[0]["id"]
    
    result = supabase.table("series").insert({"name": name}).execute()
    if result.data:
        print(f"  Created series: {name}")
        return result.data[0]["id"]
    
    raise Exception(f"Failed to create series: {name}")


def angel_exists(name: str, series_id: int) -> bool:
    """Check if angel already exists in the database."""
    result = supabase.table("angels").select("id").eq("name", name).eq("series_id", series_id).execute()
    return len(result.data) > 0


def create_angel(name: str, series_id: int, series_folder: str, filename: str) -> bool:
    """Create an angel record in the database."""
    base_name = Path(filename).stem
    
    angel_data = {
        "name": name,
        "series_id": series_id,
        "image": f"images/{series_folder}/{filename}",
        "image_bw": f"images_bw/{series_folder}/{filename}",
        "image_opacity": f"images_opacity/{series_folder}/{filename}",
        "image_profile_pic": f"images_profile_pic/{series_folder}/{filename}",
    }
    
    try:
        result = supabase.table("angels").insert(angel_data).execute()
        if result.data:
            return True
    except Exception as e:
        print(f"    Error creating angel {name}: {e}")
    
    return False


def main():
    print("Seeding database with series and angels...")
    print(f"Images directory: {IMAGES_DIR}")
    print("-" * 50)
    
    if not IMAGES_DIR.exists():
        print(f"Error: Images directory not found: {IMAGES_DIR}")
        print("Run the scraper first: python scraper/scrape_images.py")
        sys.exit(1)
    
    series_count = 0
    angel_count = 0
    skipped_count = 0
    
    for series_folder in sorted(IMAGES_DIR.iterdir()):
        if not series_folder.is_dir():
            continue
        
        series_name = format_series_name(series_folder.name)
        print(f"\nProcessing: {series_name}")
        
        series_id = get_or_create_series(series_name)
        series_count += 1
        
        for image_file in sorted(series_folder.glob("*.png")):
            angel_name = format_angel_name(image_file.name)
            
            if angel_exists(angel_name, series_id):
                print(f"    Skipped (exists): {angel_name}")
                skipped_count += 1
                continue
            
            if create_angel(angel_name, series_id, series_folder.name, image_file.name):
                print(f"    Created: {angel_name}")
                angel_count += 1
    
    print("-" * 50)
    print(f"Done!")
    print(f"  Series: {series_count}")
    print(f"  Angels created: {angel_count}")
    print(f"  Angels skipped: {skipped_count}")


if __name__ == "__main__":
    main()

