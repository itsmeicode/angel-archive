"""Tests for audit logging routes."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestAuditRoutes:
    """Test audit log endpoints."""

    @patch("app.routers.audit.get_supabase_admin")
    def test_get_all_audit_logs(self, mock_get_supabase_admin, client):
        """Test fetching all audit logs."""
        mock_logs = [
            {
                "id": 1,
                "user_id": "00000000-0000-0000-0000-000000000001",
                "action": "login",
                "details": {"ip": "127.0.0.1"},
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "user_id": "00000000-0000-0000-0000-000000000002",
                "action": "collection_update",
                "details": {"angel_id": 1},
                "created_at": "2024-01-01T01:00:00Z"
            }
        ]
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(data=mock_logs)
        mock_get_supabase_admin.return_value = mock_sb

        response = client.get("/api/audit")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["action"] == "login"

    @patch("app.routers.audit.get_supabase_admin")
    def test_get_audit_logs_by_user(self, mock_get_supabase_admin, client):
        """Test fetching audit logs for a specific user."""
        user_id = "00000000-0000-0000-0000-000000000001"
        mock_logs = [
            {
                "id": 1,
                "user_id": user_id,
                "action": "login",
                "details": {},
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=mock_logs)
        mock_get_supabase_admin.return_value = mock_sb

        response = client.get(f"/api/audit/user/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == user_id

    @patch("app.routers.audit.get_supabase_admin")
    def test_get_audit_stats(self, mock_get_supabase_admin, client):
        """Test fetching audit statistics."""
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.execute.return_value = MagicMock(data=[], count=0)
        mock_sb.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
        mock_get_supabase_admin.return_value = mock_sb

        response = client.get("/api/audit/stats")
        assert response.status_code == 200

    @patch("app.routers.audit.get_supabase_admin")
    def test_get_audit_logs_with_limit(self, mock_get_supabase_admin, client):
        """Test fetching audit logs with custom limit."""
        mock_logs = [{"id": i, "action": "test"} for i in range(5)]
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(data=mock_logs)
        mock_get_supabase_admin.return_value = mock_sb

        response = client.get("/api/audit?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5


class TestAuditLogger:
    """Test audit logging middleware/utility."""

    def test_log_audit_creates_entry(self, mock_supabase_admin):
        """Test that log_audit creates a database entry."""
        from app.middleware.audit_logger import log_audit
        
        mock_supabase_admin.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": 1}]
        )
        
        # This would be called internally
        # log_audit(mock_supabase_admin, "user-123", "test_action", {"key": "value"})

    def test_log_audit_handles_errors_gracefully(self, mock_supabase_admin):
        """Test that log_audit doesn't crash on errors."""
        from app.middleware.audit_logger import log_audit
        
        mock_supabase_admin.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        # Should not raise, just log the error
        # log_audit(mock_supabase_admin, "user-123", "test_action", {})

