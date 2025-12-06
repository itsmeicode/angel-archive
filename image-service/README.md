# Angel Archive Image Processing Service

FastAPI microservice for image processing operations. Demonstrates polyglot architecture by providing Python-based image processing capabilities that integrate with the FastAPI backend.

## Features

- Opacity adjustment
- Grayscale conversion
- Circular crop with zoom
- Batch processing of all variants

## API Endpoints

### Health Check
```bash
GET /health
```

Returns service status for monitoring and health checks.

### Process Opacity
```bash
POST /process/opacity?opacity=0.5
Content-Type: multipart/form-data
```

Adjusts image opacity (0.0 to 1.0).

### Process Grayscale
```bash
POST /process/grayscale
Content-Type: multipart/form-data
```

Converts image to black and white.

### Process Circular
```bash
POST /process/circular?crop_width=1000&crop_height=2000&zoom_factor=0.5&y_shift=-200
Content-Type: multipart/form-data
```

Creates circular cropped variant with custom parameters.

### Process All Variants
```bash
POST /process/all?opacity=0.5
Content-Type: multipart/form-data
```

Generates metadata for all image variants (use individual endpoints to download).

### Batch Endpoints
```bash
POST /process/batch/grayscale
POST /process/batch/opacity
POST /process/batch/circular
POST /process/batch/all
```

Process multiple images at once, returns a ZIP file.

## Setup and Running

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)

### Installation
```bash
cd image-service
pip install -r requirements.txt
```

### Running the Service
```bash
python main.py
```

Service runs on `http://localhost:8001`

### Running Tests
```bash
pytest test_main.py -v
```

## Testing the Service

```bash
curl -X POST "http://localhost:8001/process/opacity?opacity=0.7" \
  -F "file=@test_image.png" \
  --output result.png

curl -X POST "http://localhost:8001/process/grayscale" \
  -F "file=@test_image.png" \
  --output grayscale.png

curl -X POST "http://localhost:8001/process/circular" \
  -F "file=@test_image.png" \
  --output circular.png
```

## Integration with FastAPI Backend

The FastAPI backend can call this service for image processing:

```python
import httpx

async def process_image(image_bytes: bytes, process_type: str = "opacity") -> bytes:
    async with httpx.AsyncClient() as client:
        files = {"file": ("image.png", image_bytes, "image/png")}
        response = await client.post(
            f"http://localhost:8001/process/{process_type}",
            files=files
        )
        return response.content
```

## Architecture Benefits

1. **Polyglot Systems**: Python for both API and image processing
2. **Independent Scaling**: Scale image service based on processing load
3. **Technology Fit**: Use Python's PIL library (best-in-class for image processing)
4. **Fault Isolation**: Image service failures don't crash main API
5. **Team Specialization**: Different teams can own different services

