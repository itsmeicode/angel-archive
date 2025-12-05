import pytest
from unittest.mock import MagicMock, patch


class TestUsersEndpoints:
    """Tests for user management endpoints"""

    @patch("app.routers.users.get_supabase")
    def test_get_user_profile(self, mock_get_supabase, client, sample_user):
        """Test get user profile"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = sample_user
        mock_get_supabase.return_value = mock_supabase

        response = client.get(f"/api/users/{sample_user['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    @patch("app.routers.users.get_supabase")
    def test_get_user_profile_not_found(self, mock_get_supabase, client):
        """Test get user profile - not found"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
        mock_get_supabase.return_value = mock_supabase

        response = client.get("/api/users/nonexistent")
        assert response.status_code == 404

    @patch("app.routers.users.get_supabase")
    def test_update_user_profile(self, mock_get_supabase, client, sample_user):
        """Test update user profile"""
        updated_user = {**sample_user, "username": "newusername"}
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [updated_user]
        mock_get_supabase.return_value = mock_supabase

        response = client.put(
            f"/api/users/{sample_user['id']}",
            json={"username": "newusername"}
        )
        assert response.status_code == 200

    @patch("app.routers.users.get_supabase")
    def test_update_user_profile_no_fields(self, mock_get_supabase, client, sample_user):
        """Test update user profile - no valid fields"""
        response = client.put(
            f"/api/users/{sample_user['id']}",
            json={}
        )
        assert response.status_code == 400
