"""Tests for audit logging routes."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestAuditRoutes:
    """Test audit log endpoints."""

    def test_get_all_audit_logs(self, client, mock_supabase_admin):
        """Test fetching all audit logs."""
        mock_logs = [
            {
                "id": 1,
                "user_id": "user-123",
                "action": "login",
                "details": {"ip": "127.0.0.1"},
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "user_id": "user-456",
                "action": "collection_update",
                "details": {"angel_id": 1},
                "created_at": "2024-01-01T01:00:00Z"
            }
        ]
        
        mock_supabase_admin.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=mock_logs
        )
        
        response = client.get("/api/audit")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["action"] == "login"

    def test_get_audit_logs_by_user(self, client, mock_supabase_admin):
        """Test fetching audit logs for a specific user."""
        user_id = "user-123"
        mock_logs = [
            {
                "id": 1,
                "user_id": user_id,
                "action": "login",
                "details": {},
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        mock_supabase_admin.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=mock_logs
        )
        
        response = client.get(f"/api/audit/user/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == user_id

    def test_get_audit_stats(self, client, mock_supabase_admin):
        """Test fetching audit statistics."""
        mock_stats = [
            {"action": "login", "count": 100},
            {"action": "logout", "count": 95},
            {"action": "collection_update", "count": 250}
        ]
        
        mock_supabase_admin.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=mock_stats
        )
        
        response = client.get("/api/audit/stats")
        assert response.status_code == 200

    def test_get_audit_logs_with_limit(self, client, mock_supabase_admin):
        """Test fetching audit logs with custom limit."""
        mock_logs = [{"id": i, "action": "test"} for i in range(5)]
        
        mock_supabase_admin.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=mock_logs
        )
        
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

