"""Tests for data export routes."""
import pytest
from unittest.mock import MagicMock, patch


class TestExportRoutes:
    """Test data export endpoints."""

    def test_export_user_data_json(self, client, mock_supabase_admin, sample_user, sample_collection):
        """Test exporting user data as JSON."""
        user_id = sample_user["id"]
        
        # Mock user profile
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data=sample_user
        )
        
        # Mock collections
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[sample_collection]
        )
        
        response = client.get(f"/api/export/users/{user_id}?format=json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_export_user_data_csv(self, client, mock_supabase_admin, sample_user, sample_collection):
        """Test exporting user data as CSV."""
        user_id = sample_user["id"]
        
        # Mock user profile
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data=sample_user
        )
        
        # Mock collections
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[sample_collection]
        )
        
        response = client.get(f"/api/export/users/{user_id}?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_export_user_data_invalid_format(self, client, mock_supabase_admin, sample_user):
        """Test export with invalid format returns error."""
        user_id = sample_user["id"]
        
        response = client.get(f"/api/export/users/{user_id}?format=xml")
        assert response.status_code == 400

    def test_export_status_can_export(self, client, mock_supabase_admin, sample_user):
        """Test export status when user can export."""
        user_id = sample_user["id"]
        
        # Mock no recent exports
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )
        
        response = client.get(f"/api/export/users/{user_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["canExport"] == True

    def test_export_status_rate_limited(self, client, mock_supabase_admin, sample_user):
        """Test export status when user is rate limited."""
        user_id = sample_user["id"]
        
        # Mock recent export within rate limit window
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[{
                "id": 1,
                "user_id": user_id,
                "action": "export",
                "created_at": "2024-01-01T00:00:00Z"  # Recent timestamp
            }]
        )
        
        response = client.get(f"/api/export/users/{user_id}/status")
        assert response.status_code == 200

    def test_export_user_not_found(self, client, mock_supabase_admin):
        """Test export for non-existent user."""
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data=None
        )
        
        response = client.get("/api/export/users/non-existent-id?format=json")
        assert response.status_code == 404

    def test_export_includes_collection_summary(self, client, mock_supabase_admin, sample_user, sample_collection):
        """Test that export includes collection statistics."""
        user_id = sample_user["id"]
        
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data=sample_user
        )
        
        collections = [
            {**sample_collection, "is_favorite": True},
            {**sample_collection, "id": 2, "in_search_of": True},
            {**sample_collection, "id": 3, "willing_to_trade": True}
        ]
        
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=collections
        )
        
        response = client.get(f"/api/export/users/{user_id}?format=json")
        assert response.status_code == 200

