"""Tests for data export routes."""
import pytest
from unittest.mock import MagicMock, patch


class TestExportRoutes:
    """Test data export endpoints."""

    @patch("app.routers.export.get_supabase")
    def test_export_user_data_json(self, mock_get_supabase, client, sample_user, sample_collection):
        """Test exporting user data as JSON."""
        user_id = sample_user["id"]
        mock_sb = MagicMock()
        # Export only queries user_collections (with angels join), no user profile query
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{**sample_collection, "angels": {"name": "Test Angel", "series_id": 1}}]
        )
        mock_get_supabase.return_value = mock_sb

        response = client.get(f"/api/export/users/{user_id}?format=json")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    @patch("app.routers.export.get_supabase")
    def test_export_user_data_csv(self, mock_get_supabase, client, sample_user, sample_collection):
        """Test exporting user data as CSV."""
        user_id = sample_user["id"]
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{**sample_collection, "angels": {"name": "Test Angel", "series_id": 1}}]
        )
        mock_get_supabase.return_value = mock_sb

        response = client.get(f"/api/export/users/{user_id}?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")

    def test_export_user_data_invalid_format(self, client, sample_user):
        """Test export with invalid format returns validation error (422)."""
        user_id = sample_user["id"]
        response = client.get(f"/api/export/users/{user_id}?format=xml")
        assert response.status_code == 422

    def test_export_status_can_export(self, client, mock_supabase_admin, sample_user):
        """Test export status when user can export."""
        user_id = sample_user["id"]
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )
        response = client.get(f"/api/export/users/{user_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["canExport"] is True

    def test_export_status_rate_limited(self, client, mock_supabase_admin, sample_user):
        """Test export status when user is rate limited."""
        user_id = sample_user["id"]
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{"id": 1, "user_id": user_id, "action": "export", "created_at": "2024-01-01T00:00:00Z"}]
        )
        response = client.get(f"/api/export/users/{user_id}/status")
        assert response.status_code == 200

    @patch("app.routers.export.get_supabase")
    def test_export_user_not_found(self, mock_get_supabase, client):
        """Test export for user with no collections returns empty export."""
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        mock_get_supabase.return_value = mock_sb
        response = client.get("/api/export/users/00000000-0000-0000-0000-000000000099?format=json")
        assert response.status_code == 200
        data = response.json()
        assert data["collection"] == []
        assert data["summary"]["total_cards"] == 0

    @patch("app.routers.export.get_supabase")
    def test_export_includes_collection_summary(self, mock_get_supabase, client, sample_user, sample_collection):
        """Test that export includes collection statistics."""
        user_id = sample_user["id"]
        collections = [
            {**sample_collection, "angels": {"name": "A", "series_id": 1}, "is_favorite": True},
            {**sample_collection, "id": 2, "angels": {"name": "B", "series_id": 1}, "in_search_of": True},
            {**sample_collection, "id": 3, "angels": {"name": "C", "series_id": 1}, "willing_to_trade": True},
        ]
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=collections)
        mock_get_supabase.return_value = mock_sb
        response = client.get(f"/api/export/users/{user_id}?format=json")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "collection" in data

