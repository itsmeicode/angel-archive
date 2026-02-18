import pytest
from unittest.mock import MagicMock, patch


class TestAuthEndpoints:
    """Tests for authentication endpoints"""

    def test_auth_root(self, client):
        """Test auth root endpoint"""
        response = client.get("/auth")
        assert response.status_code == 200
        assert response.json()["message"] == "Auth routes are working"

    @patch("app.routers.auth.get_supabase_admin")
    def test_check_username_exists(self, mock_get_supabase_admin, client):
        """Test username availability check - exists"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"username": "testuser"}]
        mock_get_supabase_admin.return_value = mock_supabase

        response = client.get("/auth/check/username/testuser")
        assert response.status_code == 200
        assert response.json()["exists"] == True

    @patch("app.routers.auth.get_supabase_admin")
    def test_check_username_not_exists(self, mock_get_supabase_admin, client):
        """Test username availability check - not exists"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_get_supabase_admin.return_value = mock_supabase

        response = client.get("/auth/check/username/newuser")
        assert response.status_code == 200
        assert response.json()["exists"] == False

    @patch("app.routers.auth.get_supabase_admin")
    def test_check_email_exists(self, mock_get_supabase_admin, client):
        """Test email availability check - exists"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"email": "test@example.com"}]
        mock_get_supabase_admin.return_value = mock_supabase

        response = client.get("/auth/check/email/test@example.com")
        assert response.status_code == 200
        assert response.json()["exists"] == True

    @patch("app.routers.auth.get_supabase_admin")
    def test_check_email_not_exists(self, mock_get_supabase_admin, client):
        """Test email availability check - not exists"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_get_supabase_admin.return_value = mock_supabase

        response = client.get("/auth/check/email/new@example.com")
        assert response.status_code == 200
        assert response.json()["exists"] == False

    @patch("app.routers.auth.get_supabase_admin")
    def test_create_user_success(self, mock_get_supabase_admin, client, sample_user):
        """Test user creation"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [sample_user]
        mock_get_supabase_admin.return_value = mock_supabase

        response = client.post("/auth/users", json={
            "id": sample_user["id"],
            "email": sample_user["email"],
            "username": sample_user["username"],
        })
        assert response.status_code == 201

    @patch("app.routers.auth.get_supabase_admin")
    def test_get_user_by_username_found(self, mock_get_supabase_admin, client):
        """Test lookup user by username - found"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"email": "test@example.com"}]
        mock_get_supabase_admin.return_value = mock_supabase

        response = client.get("/auth/users/by-username/testuser")
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    @patch("app.routers.auth.get_supabase_admin")
    def test_get_user_by_username_not_found(self, mock_get_supabase_admin, client):
        """Test lookup user by username - not found"""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_get_supabase_admin.return_value = mock_supabase

        response = client.get("/auth/users/by-username/nonexistent")
        assert response.status_code == 404
