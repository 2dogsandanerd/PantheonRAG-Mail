"""Unit tests for HealthChecker."""

import pytest
import asyncio
from datetime import datetime, timedelta
from src.services.health_checker import HealthChecker, ServiceStatus


@pytest.mark.asyncio
async def test_check_service_unhealthy():
    """Test failed health check for unreachable service."""
    checker = HealthChecker()

    is_healthy = await checker.check_service(
        "invalid_service",
        "http://localhost:99999",
        "/invalid",
        timeout=0.5
    )

    assert is_healthy is False


@pytest.mark.asyncio
async def test_cache_initially_invalid():
    """Test that cache is invalid initially."""
    checker = HealthChecker()

    assert not checker._is_cache_valid()


def test_cache_valid_after_set():
    """Test that cache is valid after being set."""
    checker = HealthChecker()

    # Set cache
    checker._status_cache = {"test": "data"}
    checker._status_cache_time = datetime.now()

    # Should be valid immediately
    assert checker._is_cache_valid()


def test_cache_expires():
    """Test that cache expires after TTL."""
    checker = HealthChecker()

    # Set cache with old timestamp
    checker._status_cache = {"test": "data"}
    checker._status_cache_time = datetime.now() - timedelta(seconds=4)

    # Should be invalid (TTL is 3 seconds)
    assert not checker._is_cache_valid()


def test_invalidate_cache():
    """Test cache invalidation."""
    checker = HealthChecker()

    checker._status_cache = {"test": "data"}
    checker._status_cache_time = datetime.now()

    checker.invalidate_cache()

    assert checker._status_cache is None
    assert checker._status_cache_time is None


def test_get_default_status():
    """Test default status structure."""
    checker = HealthChecker()

    default = checker._get_default_status()

    assert "ollama" in default
    assert "chroma" in default
    assert default["ollama"]["running"] is False
    assert default["chroma"]["running"] is False
