import pytest
from unittest.mock import MagicMock, patch


class TestAngelsEndpoints:
    """Tests for angels catalog endpoints"""

    @patch("app.routers.angels.get_supabase")
    def test_get_all_angels(self, mock_get_supabase, client, sample_angel):
        """Test get all angels"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [sample_angel]
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/angels")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Angel"
        assert "image_url" in data[0]

    @patch("app.routers.angels.get_supabase")
    def test_get_all_angels_empty(self, mock_get_supabase, client):
        """Test get all angels - empty list"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/angels")
        assert response.status_code == 200
        assert response.json() == []

    @patch("app.routers.angels.get_supabase")
    def test_get_angel_by_id(self, mock_get_supabase, client, sample_angel):
        """Test get single angel by ID"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = sample_angel
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/angels/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Angel"

    @patch("app.routers.angels.get_supabase")
    def test_get_angel_by_id_not_found(self, mock_get_supabase, client):
        """Test get angel by ID - not found"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/angels/999")
        assert response.status_code == 404

    @patch("app.routers.angels.get_supabase")
    def test_get_angels_by_series(self, mock_get_supabase, client, sample_angel):
        """Test get angels by series ID"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_angel]
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/angels/series/1")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1

    @patch("app.routers.angels.get_supabase")
    def test_get_profile_pictures(self, mock_get_supabase, client):
        """Test get profile pictures"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
            {"id": 1, "name": "Test Angel", "image_profile_pic": "test/profile.png"}
        ]
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/angels/profile-pictures")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert "image_url" in data[0]
