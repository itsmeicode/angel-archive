"""
Image Processing Scripts

Creates image variants for each angel:
- Grayscale (black & white)
- Reduced opacity
- Circular crop (for profile pictures)
"""

import os
from PIL import Image, ImageDraw
from pathlib import Path


def reduce_opacity(img: Image.Image, opacity: float = 0.5) -> Image.Image:
    """Reduce image opacity."""
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda p: int(p * opacity))
    return Image.merge("RGBA", (r, g, b, a))


def convert_to_grayscale(img: Image.Image) -> Image.Image:
    """Convert image to grayscale while preserving alpha."""
    return img.convert("L").convert("RGBA")


def convert_to_circular(img: Image.Image, crop_width: int = 1000, crop_height: int = 1000, zoom_factor: float = 0.5, y_shift: int = -300) -> Image.Image:
    img = img.convert("RGBA")
    img_width, img_height = img.size

    x_center = img_width // 2
    y_center = img_height // 2 + y_shift

    left = x_center - crop_width // 2
    top = y_center - crop_height // 2
    right = x_center + crop_width // 2
    bottom = y_center + crop_height // 2

    top = max(0, top)
    bottom = min(img_height, bottom)

    cropped_img = img.crop((left, top, right, bottom))

    zoomed_width = int(crop_width * zoom_factor)
    zoomed_height = int(crop_height * zoom_factor)
    cropped_img = cropped_img.resize((zoomed_width, zoomed_height), Image.LANCZOS)

    mask = Image.new("L", (zoomed_width, zoomed_height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, zoomed_width, zoomed_height), fill=255)

    circular_img = Image.new("RGBA", (zoomed_width, zoomed_height), (0, 0, 0, 0))
    circular_img.paste(cropped_img, (0, 0), mask)

    circular_img = circular_img.resize((crop_width, crop_height), Image.LANCZOS)
    return circular_img


def process_all_images(input_dir: str = "images"):
    """Process all images and create variants."""
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"Error: {input_dir} directory not found!")
        print("Please run scrape_images.py first.")
        return

    output_dirs = {
        "bw": Path("images_bw"),
        "opacity": Path("images_opacity"),
        "profile_pic": Path("images_profile_pic"),
    }

    for dir_path in output_dirs.values():
        dir_path.mkdir(exist_ok=True)

    processed_count = 0

    for series_dir in input_path.iterdir():
        if not series_dir.is_dir():
            continue

        series_name = series_dir.name
        print(f"\nProcessing: {series_name}")

        for output_type, output_base in output_dirs.items():
            (output_base / series_name).mkdir(exist_ok=True)

        for image_file in series_dir.glob("*.png"):
            try:
                img = Image.open(image_file).convert("RGBA")
                filename = image_file.name

                bw_img = convert_to_grayscale(img.copy())
                bw_img.save(output_dirs["bw"] / series_name / filename, "PNG")

                opacity_img = reduce_opacity(img.copy(), 0.5)
                opacity_img.save(output_dirs["opacity"] / series_name / filename, "PNG")

                profile_img = convert_to_circular(img.copy())
                profile_img.save(
                    output_dirs["profile_pic"] / series_name / filename, "PNG"
                )

                print(f"  Processed: {filename}")
                processed_count += 1

            except Exception as e:
                print(f"  Error processing {image_file}: {e}")

    print(f"\n{'='*60}")
    print(f"Processing complete! Created variants for {processed_count} images.")
    print(f"{'='*60}")


if __name__ == "__main__":
    process_all_images()
