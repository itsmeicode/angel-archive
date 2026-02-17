from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw
import io
from typing import Optional, List
import uvicorn
import zipfile
import tempfile
import os

app = FastAPI(
    title="Angel Archive Image Processing Service",
    description="Microservice for image processing operations (opacity, grayscale, circular crop)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Angel Archive Image Processing",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "opacity": "POST /process/opacity",
            "grayscale": "POST /process/grayscale",
            "circular": "POST /process/circular",
            "all": "POST /process/all",
            "batch_all": "POST /process/batch/all",
            "batch_grayscale": "POST /process/batch/grayscale",
            "batch_opacity": "POST /process/batch/opacity",
            "batch_circular": "POST /process/batch/circular"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "image-processing",
        "version": "1.0.0"
    }

def reduce_opacity(img: Image.Image, opacity: float) -> Image.Image:
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda p: int(p * opacity))
    return Image.merge("RGBA", (r, g, b, a))

def convert_to_grayscale(img: Image.Image) -> Image.Image:
    return img.convert("L").convert("RGBA")

def convert_to_circular(
    img: Image.Image,
    crop_width: int = 1000,
    crop_height: int = 1000,
    zoom_factor: float = 0.5,
    y_shift: int = -300,
) -> Image.Image:
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

@app.post("/process/opacity")
async def process_opacity(
    file: UploadFile = File(...),
    opacity: float = 0.5
):
    if opacity < 0 or opacity > 1:
        raise HTTPException(status_code=400, detail="Opacity must be between 0 and 1")

    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))

        processed_img = reduce_opacity(img, opacity)

        img_byte_arr = io.BytesIO()
        processed_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return StreamingResponse(
            img_byte_arr,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=opacity_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@app.post("/process/grayscale")
async def process_grayscale(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))

        processed_img = convert_to_grayscale(img)

        img_byte_arr = io.BytesIO()
        processed_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return StreamingResponse(
            img_byte_arr,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=bw_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@app.post("/process/circular")
async def process_circular(
    file: UploadFile = File(...),
    crop_width: int = 1000,
    crop_height: int = 2000,
    zoom_factor: float = 0.5,
    y_shift: int = -200
):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))

        processed_img = convert_to_circular(img, crop_width, crop_height, zoom_factor, y_shift)

        img_byte_arr = io.BytesIO()
        processed_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return StreamingResponse(
            img_byte_arr,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=circular_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@app.post("/process/all")
async def process_all_variants(
    file: UploadFile = File(...),
    opacity: float = 0.5
):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))

        opacity_img = reduce_opacity(img.copy(), opacity)
        grayscale_img = convert_to_grayscale(img.copy())
        circular_img = convert_to_circular(img.copy())

        variants = {}

        for variant_name, variant_img in [
            ("opacity", opacity_img),
            ("grayscale", grayscale_img),
            ("circular", circular_img)
        ]:
            img_byte_arr = io.BytesIO()
            variant_img.save(img_byte_arr, format='PNG')
            variants[variant_name] = {
                "size": img_byte_arr.tell(),
                "format": "PNG"
            }

        return {
            "message": "All variants processed successfully",
            "variants": variants,
            "note": "Use individual endpoints to download specific variants"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@app.post("/process/batch/grayscale")
async def batch_process_grayscale(files: List[UploadFile] = File(...)):
    try:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                contents = await file.read()
                img = Image.open(io.BytesIO(contents))

                processed_img = convert_to_grayscale(img)

                img_byte_arr = io.BytesIO()
                processed_img.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)

                zip_file.writestr(f"bw_{file.filename}", img_byte_arr.getvalue())

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=batch_grayscale.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.post("/process/batch/opacity")
async def batch_process_opacity(
    files: List[UploadFile] = File(...),
    opacity: float = 0.5
):
    if opacity < 0 or opacity > 1:
        raise HTTPException(status_code=400, detail="Opacity must be between 0 and 1")

    try:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                contents = await file.read()
                img = Image.open(io.BytesIO(contents))

                processed_img = reduce_opacity(img, opacity)

                img_byte_arr = io.BytesIO()
                processed_img.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)

                zip_file.writestr(f"opacity_{file.filename}", img_byte_arr.getvalue())

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=batch_opacity.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.post("/process/batch/circular")
async def batch_process_circular(
    files: List[UploadFile] = File(...),
    crop_width: int = 1000,
    crop_height: int = 2000,
    zoom_factor: float = 0.5,
    y_shift: int = -200
):
    try:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                contents = await file.read()
                img = Image.open(io.BytesIO(contents))

                processed_img = convert_to_circular(img, crop_width, crop_height, zoom_factor, y_shift)

                img_byte_arr = io.BytesIO()
                processed_img.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)

                zip_file.writestr(f"circular_{file.filename}", img_byte_arr.getvalue())

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=batch_circular.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.post("/process/batch/all")
async def batch_process_all_variants(
    files: List[UploadFile] = File(...),
    opacity: float = 0.5
):
    if opacity < 0 or opacity > 1:
        raise HTTPException(status_code=400, detail="Opacity must be between 0 and 1")

    try:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                contents = await file.read()
                img = Image.open(io.BytesIO(contents))

                opacity_img = reduce_opacity(img.copy(), opacity)
                grayscale_img = convert_to_grayscale(img.copy())
                circular_img = convert_to_circular(img.copy())

                for variant_name, variant_img in [
                    ("opacity", opacity_img),
                    ("grayscale", grayscale_img),
                    ("circular", circular_img)
                ]:
                    img_byte_arr = io.BytesIO()
                    variant_img.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)

                    zip_file.writestr(f"{variant_name}_{file.filename}", img_byte_arr.getvalue())

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=batch_all_variants.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

