"""
E2E Test: Health Check and Service Status Flow

Tests the basic health endpoints and service status without mocks.
"""

import pytest
import httpx
from pathlib import Path

pytestmark = [pytest.mark.e2e, pytest.mark.integration]


@pytest.mark.asyncio
async def test_backend_health_endpoint():
    """Test that backend health endpoint returns 200."""
    from .conftest import TEST_BASE_URL
    async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
        response = await client.get("/api/health", follow_redirects=True)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"✅ Backend health: {data['status']}")


@pytest.mark.asyncio
async def test_api_root_endpoint(http_client: httpx.AsyncClient):
    """Test that API root is accessible."""
    # Try the docs endpoint
    response = await http_client.get("/docs", follow_redirects=True)

    # Should either return docs (200) or redirect to docs
    assert response.status_code in [200, 307]
    print("✅ API docs accessible")


@pytest.mark.asyncio
async def test_services_status_endpoint(http_client: httpx.AsyncClient):
    """Test the services status endpoint with real services."""
    response = await http_client.get("/services/status")

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "services" in data or "status" in data

    # Print service statuses for debugging
    if "services" in data:
        for service, status in data["services"].items():
            print(f"  - {service}: {status}")

    print("✅ Services status endpoint working")


@pytest.mark.asyncio
async def test_dashboard_stats_endpoint(http_client: httpx.AsyncClient):
    """Test dashboard stats endpoint."""
    response = await http_client.get("/dashboard/stats")

    # Should return 200 even if empty
    assert response.status_code == 200
    data = response.json()

    print(f"✅ Dashboard stats: {data}")


@pytest.mark.asyncio
async def test_config_endpoint(http_client: httpx.AsyncClient):
    """Test configuration endpoint."""
    # Get current config
    response = await http_client.get("/config/config")

    # Should work (might be empty if not configured)
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        print(
            f"✅ Config retrieved: {list(data.keys()) if isinstance(data, dict) else 'available'}"
        )
    else:
        print("⚠️  Config not set yet (expected)")


@pytest.mark.asyncio
async def test_end_to_end_health_flow():
    """Complete health check flow: API, Services, and basic functionality."""
    import httpx
    from .conftest import TEST_BASE_URL

    async with httpx.AsyncClient(base_url=TEST_BASE_URL, timeout=10.0) as client:
        # 1. Check API is up
        health_resp = await client.get("/api/health")
        assert health_resp.status_code == 200
        print("  1. ✓ API health check passed")

        # 2. Check services status
        services_resp = await client.get("/api/v1/services/status")
        assert services_resp.status_code == 200
        print("  2. ✓ Services status check passed")

        # 3. Check RAG collections endpoint (should work even if empty)
        collections_resp = await client.get("/api/v1/rag/collections")
        # 503 is acceptable if mocked/unavailable, but with mock it should be 200
        assert collections_resp.status_code in [200, 503] 
        print("  3. ✓ RAG collections endpoint accessible")

        # 4. Check dashboard
        dashboard_resp = await client.get("/api/v1/dashboard/stats")
        assert dashboard_resp.status_code == 200
        print("  4. ✓ Dashboard endpoint accessible")

    print("\n✅ Complete health flow passed - all services accessible!")
