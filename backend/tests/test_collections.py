import pytest
from unittest.mock import MagicMock, patch


class TestCollectionsEndpoints:
    """Tests for user collections endpoints"""

    @patch("app.routers.users.get_supabase")
    def test_get_user_collections(self, mock_get_supabase, client, sample_user, sample_collection):
        """Test get user collections"""
        collection_with_angel = {
            **sample_collection,
            "angels": {
                "id": 1,
                "name": "Test Angel",
                "card_number": "001",
                "series_id": 1,
                "image": "test/image.png",
                "image_bw": None,
                "image_opacity": None,
                "image_profile_pic": None,
            }
        }
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [collection_with_angel]
        mock_get_supabase.return_value = mock_supabase

        response = client.get(f"/api/users/{sample_user['id']}/collections")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["count"] == 2
        assert data[0]["is_favorite"] == True

    @patch("app.routers.users.get_supabase")
    def test_get_user_collections_empty(self, mock_get_supabase, client, sample_user):
        """Test get user collections - empty"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        mock_get_supabase.return_value = mock_supabase

        response = client.get(f"/api/users/{sample_user['id']}/collections")
        assert response.status_code == 200
        assert response.json() == []

    @patch("app.routers.users.get_supabase")
    def test_upsert_collection(self, mock_get_supabase, client, sample_user, sample_collection):
        """Test add/update collection item"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [sample_collection]
        mock_get_supabase.return_value = mock_supabase

        response = client.post(
            f"/api/users/{sample_user['id']}/collections",
            json={
                "angel_id": 1,
                "count": 2,
                "is_favorite": True,
                "in_search_of": False,
                "willing_to_trade": False,
            }
        )
        assert response.status_code == 200

    @patch("app.routers.users.get_supabase")
    def test_delete_collection(self, mock_get_supabase, client, sample_user):
        """Test delete collection item"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.delete.return_value.match.return_value.execute.return_value.data = []
        mock_get_supabase.return_value = mock_supabase

        response = client.delete(f"/api/users/{sample_user['id']}/collections/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "deleted" in data["message"].lower()
