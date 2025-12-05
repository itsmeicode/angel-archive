# Angel Archive Scraper

Scripts for downloading and processing Sonny Angel images from the official website.

## Setup

```bash
cd scraper
pip install -r requirements.txt
```

## Usage

### Step 1: Discover Galleries

Discover all available series from the Sonny Angel website:

```bash
python discover_galleries.py
```

This creates `gallery_config.json` with all series information.

### Step 2: Download Images

Download all angel images based on the config:

```bash
python scrape_images.py
```

Images are saved to `images/{series_name}_Series/`.

### Step 3: Process Images

Create image variants (grayscale, opacity, circular crop):

```bash
python process_images.py
```

Creates:
- `images_bw/` - Black & white versions
- `images_opacity/` - 50% opacity versions  
- `images_profile_pic/` - Circular cropped for avatars

## Output Structure

```
scraper/
  images/
    Animal_1_Series/
      Cockerel.png
      Dalmatian.png
      ...
  images_bw/
    Animal_1_Series/
      Cockerel.png
      ...
  images_opacity/
    ...
  images_profile_pic/
    ...
```

## Notes

- Images are gitignored (large files)
- Upload processed images to Supabase Storage
- Respectful rate limiting (0.5-1s between requests)

