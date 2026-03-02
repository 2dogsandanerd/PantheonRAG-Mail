import pytest
import asyncio
from src.core.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError, CircuitState

@pytest.mark.asyncio
async def test_circuit_opens_after_threshold():
    """Test circuit opens after failure threshold"""
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

    async def failing_func():
        raise RuntimeError("Service down")

    # Trigger failures until circuit opens
    for i in range(3):
        with pytest.raises(RuntimeError):
            await breaker.call(failing_func)

    # Circuit should now be open
    assert breaker.state == CircuitState.OPEN

    # Next call should be rejected immediately
    with pytest.raises(CircuitBreakerOpenError):
        await breaker.call(failing_func)

@pytest.mark.asyncio
async def test_circuit_recovers_after_timeout():
    """Test circuit attempts recovery after timeout"""
    breaker = CircuitBreaker(
        failure_threshold=2,
        success_threshold=2,
        recovery_timeout=1  # 1 second for fast test
    )

    call_count = [0]

    async def flaky_func():
        call_count[0] += 1
        if call_count[0] <= 2:
            raise RuntimeError("Failing")
        return "success"

    # Open circuit
    for _ in range(2):
        with pytest.raises(RuntimeError):
            await breaker.call(flaky_func)

    assert breaker.state == CircuitState.OPEN

    # Wait for recovery timeout
    await asyncio.sleep(1.5)

    # Should attempt recovery (HALF_OPEN)
    result = await breaker.call(flaky_func)
    assert breaker.state == CircuitState.HALF_OPEN

    # One more success should close circuit
    result = await breaker.call(flaky_func)
    assert breaker.state == CircuitState.CLOSED

@pytest.mark.asyncio
async def test_retry_with_exponential_backoff():
    """Test retry policy with exponential backoff"""
    from src.core.retry_policy import RetryPolicy

    policy = RetryPolicy(max_retries=3, base_delay=0.1, exponential_base=2.0, jitter=False)

    attempt_times = []

    async def flaky_func():
        attempt_times.append(asyncio.get_event_loop().time())
        if len(attempt_times) < 3:
            raise RuntimeError("Transient failure")
        return "success"

    result = await policy.execute(flaky_func)

    assert result == "success"
    assert len(attempt_times) == 3

    # Check exponential delays: ~0.1s, ~0.2s
    assert attempt_times[1] - attempt_times[0] >= 0.1
    assert attempt_times[2] - attempt_times[1] >= 0.2

@pytest.mark.asyncio
async def test_concurrent_requests_thread_safety():
    """Test thread-safety with concurrent requests through circuit breaker"""
    breaker = CircuitBreaker()
    counter = [0]
    lock = asyncio.Lock()

    async def increment():
        async with lock:
            counter[0] += 1
        await asyncio.sleep(0.01)
        return counter[0]

    # 100 concurrent requests
    tasks = [breaker.call(increment) for _ in range(100)]
    results = await asyncio.gather(*tasks)

    assert counter[0] == 100
    assert len(set(results)) == 100  # All unique values
