from fastapi.testclient import TestClient
from PIL import Image
import io
from main import app

client = TestClient(app)

def create_test_image():
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()
    assert response.json()["service"] == "Angel Archive Image Processing"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "image-processing"

def test_process_opacity():
    test_img = create_test_image()
    response = client.post(
        "/process/opacity?opacity=0.5",
        files={"file": ("test.png", test_img, "image/png")}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_process_opacity_invalid_range():
    test_img = create_test_image()
    response = client.post(
        "/process/opacity?opacity=1.5",
        files={"file": ("test.png", test_img, "image/png")}
    )
    assert response.status_code == 400
    assert "Opacity must be between 0 and 1" in response.json()["detail"]

def test_process_grayscale():
    test_img = create_test_image()
    response = client.post(
        "/process/grayscale",
        files={"file": ("test.png", test_img, "image/png")}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_process_circular():
    test_img = create_test_image()
    response = client.post(
        "/process/circular",
        files={"file": ("test.png", test_img, "image/png")}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_process_circular_custom_params():
    test_img = create_test_image()
    response = client.post(
        "/process/circular?crop_width=500&crop_height=1000&zoom_factor=0.7&y_shift=-100",
        files={"file": ("test.png", test_img, "image/png")}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_process_all_variants():
    test_img = create_test_image()
    response = client.post(
        "/process/all?opacity=0.5",
        files={"file": ("test.png", test_img, "image/png")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "variants" in data
    assert "opacity" in data["variants"]
    assert "grayscale" in data["variants"]
    assert "circular" in data["variants"]

def test_invalid_file():
    response = client.post(
        "/process/opacity",
        files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
    )
    assert response.status_code == 500
    assert "Image processing failed" in response.json()["detail"]

