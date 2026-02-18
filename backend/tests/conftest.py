import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    with patch("app.config.supabase.get_supabase") as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_supabase_admin():
    """Mock Supabase admin client"""
    with patch("app.config.supabase.get_supabase_admin") as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_user():
    """Sample user data (id is a valid UUID for Supabase/PostgREST)"""
    return {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "test@example.com",
        "username": "testuser",
        "profile_pic": None,
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_angel():
    """Sample angel data"""
    return {
        "id": 1,
        "name": "Test Angel",
        "series_id": 1,
        "image": "test/image.png",
        "image_bw": "test/image_bw.png",
        "image_opacity": "test/image_opacity.png",
        "image_profile_pic": "test/image_profile.png",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_collection():
    """Sample collection data"""
    return {
        "id": 1,
        "user_id": "00000000-0000-0000-0000-000000000001",
        "angel_id": 1,
        "count": 2,
        "trade_count": 0,
        "is_favorite": True,
        "in_search_of": False,
        "willing_to_trade": False,
        "updated_at": "2024-01-01T00:00:00Z",
    }
