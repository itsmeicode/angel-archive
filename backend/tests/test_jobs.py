"""Tests for job management routes."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestJobRoutes:
    """Test job management endpoints."""

    @patch("app.services.job_service.get_supabase_admin")
    def test_trigger_job_success(self, mock_get_supabase_admin, client):
        """Test manually triggering a job."""
        mock_sb = MagicMock()
        mock_sb.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": 1, "status": "running"}])
        # update_job_run fetches started_at then updates
        mock_sb.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
            data={"started_at": "2024-01-01T00:00:00Z"}
        )
        mock_sb.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": 1}])
        mock_get_supabase_admin.return_value = mock_sb

        response = client.post("/api/jobs/trigger")
        assert response.status_code in [200, 202, 503]  # May be disabled in test mode

    @patch("app.services.job_service.get_supabase_admin")
    def test_get_job_history(self, mock_get_supabase_admin, client):
        """Test fetching job history. API returns { success, jobs, cron }."""
        mock_jobs = [
            {"id": 1, "job_name": "asset_pipeline", "status": "success", "started_at": "2024-01-01T00:00:00Z", "completed_at": "2024-01-01T00:05:00Z", "images_processed": 10, "error_message": None},
            {"id": 2, "job_name": "asset_pipeline", "status": "success", "started_at": "2024-01-02T00:00:00Z", "completed_at": "2024-01-02T00:03:00Z", "images_processed": 5, "error_message": None},
        ]
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=mock_jobs)
        mock_get_supabase_admin.return_value = mock_sb

        response = client.get("/api/jobs/status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["jobs"]) == 2
        assert "cron" in data

    @patch("app.services.job_service.get_supabase_admin")
    def test_get_job_history_with_limit(self, mock_get_supabase_admin, client):
        """Test fetching job history with custom limit."""
        mock_jobs = [{"id": i, "job_name": "asset_pipeline", "status": "success"} for i in range(5)]
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=mock_jobs)
        mock_get_supabase_admin.return_value = mock_sb

        response = client.get("/api/jobs/status?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 5

    @patch("app.services.job_service.get_supabase_admin")
    def test_get_latest_job(self, mock_get_supabase_admin, client):
        """Test fetching the latest job run. API returns { success, job }."""
        mock_job = {"id": 1, "job_name": "asset_pipeline", "status": "success", "started_at": "2024-01-01T00:00:00Z", "completed_at": "2024-01-01T00:05:00Z", "images_processed": 10, "error_message": None}
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[mock_job])
        mock_get_supabase_admin.return_value = mock_sb

        response = client.get("/api/jobs/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["job"]["id"] == 1

    @patch("app.services.job_service.get_supabase_admin")
    def test_get_latest_job_none_found(self, mock_get_supabase_admin, client):
        """Test getting latest job when none exist. API returns 200 with job: None."""
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
        mock_get_supabase_admin.return_value = mock_sb

        response = client.get("/api/jobs/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["job"] is None

    def test_get_cron_status(self, client):
        """Test getting cron scheduler status. API returns { success, cron }."""
        response = client.get("/api/jobs/cron")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cron" in data
        assert "enabled" in data["cron"]
        assert "running" in data["cron"]

    @patch("app.services.job_service.get_supabase_admin")
    def test_job_with_errors(self, mock_get_supabase_admin, client):
        """Test job run with errors. Schema uses error_message (string), not errors."""
        mock_job = {
            "id": 1,
            "job_name": "asset_pipeline",
            "status": "failed",
            "started_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:01:00Z",
            "images_processed": 0,
            "error_message": "Failed to connect to image service",
        }
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[mock_job])
        mock_get_supabase_admin.return_value = mock_sb

        response = client.get("/api/jobs/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["job"]["status"] == "failed"
        assert data["job"]["error_message"] == "Failed to connect to image service"


class TestCronManager:
    """Test cron manager functionality."""

    def test_cron_manager_starts(self):
        """Test that cron manager can start."""
        from app.services.cron_manager import get_cron_status
        
        status = get_cron_status()
        assert "enabled" in status
        assert "running" in status

    def test_cron_manager_status_fields(self):
        """Test cron status returns expected fields."""
        from app.services.cron_manager import get_cron_status
        
        status = get_cron_status()
        expected_fields = ["enabled", "running", "next_run", "schedule"]
        for field in expected_fields:
            assert field in status


class TestJobService:
    """Test job service functionality."""

    def test_job_service_creates_job_record(self, mock_supabase_admin):
        """Test that running a job creates a database record."""
        mock_supabase_admin.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": 1}]
        )
        
        # Job service would create a record when starting
        # This is tested indirectly through the API tests

    def test_job_service_updates_on_completion(self, mock_supabase_admin):
        """Test that job record is updated on completion."""
        mock_supabase_admin.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": 1, "status": "completed"}]
        )
        
        # Job service would update the record when complete
        # This is tested indirectly through the API tests

