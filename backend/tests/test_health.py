import pytest


class TestHealthEndpoints:
    """Tests for health monitoring endpoints"""

    def test_health_check(self, client):
        """Test liveness endpoint returns ok status"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "uptime" in data

    def test_readiness_check(self, client):
        """Test readiness endpoint returns service status"""
        response = client.get("/health/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "services" in data
        assert "memory" in data["services"]

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint returns prometheus-style metrics"""
        response = client.get("/health/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "uptime" in data
        assert "metrics" in data
        assert "system" in data
        
        metrics = data["metrics"]
        assert "http_requests_total" in metrics
        assert "http_errors_total" in metrics
        assert "error_rate" in metrics

    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to the API"
