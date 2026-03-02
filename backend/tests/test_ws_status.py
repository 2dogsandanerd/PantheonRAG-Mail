"""
WebSocket Status Endpoint Tests

Tests für backend/src/api/v1/services.py Endpoint /api/v1/services/ws/status

Szenarien:
1. Verbindungsaufbau: Client verbindet, initial_status empfangen
2. Keepalive: ping/pong bleibt offen
3. Event-Durchsatz: Status-Änderung → status_change Event
4. Disconnect & Cleanup: Subscriber entfernt, keine Leaks
5. Backpressure: > maxsize Events → Drop-Oldest ohne Crash
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime


# === FIXTURES ===

@pytest.fixture
def mock_service_manager():
    """Mock ServiceManager für Status-Abfragen."""
    manager = AsyncMock()
    manager.get_status = AsyncMock(return_value={
        "ollama": {"running": True, "host": "localhost", "port": 11434},
        "chroma": {"running": True, "host": "localhost", "port": 8000}
    })
    return manager


@pytest.fixture
def mock_config():
    """Mock Config für WS-Konfiguration."""
    config = Mock()
    config.max_queue_size = 16
    config.idle_timeout = 300
    config.max_subscribers = 10
    return config


@pytest.fixture
def mock_health_monitor(mock_config):
    """Mock HealthMonitor mit Subscriber-Verwaltung."""
    monitor = Mock()
    monitor.config = mock_config
    monitor._subscribers = []
    monitor.can_subscribe = Mock(return_value=True)
    monitor.subscribe = Mock(side_effect=lambda cb: monitor._subscribers.append(cb))
    monitor.unsubscribe = Mock(side_effect=lambda cb: monitor._subscribers.remove(cb) if cb in monitor._subscribers else None)
    monitor.get_subscriber_count = Mock(side_effect=lambda: len(monitor._subscribers))
    return monitor


@pytest.fixture
def mock_websocket():
    """Mock WebSocket Client."""
    ws = AsyncMock()
    ws.client = ("127.0.0.1", 12345)
    ws.accept = AsyncMock()
    ws.close = AsyncMock()
    ws.send_json = AsyncMock()
    ws.send_text = AsyncMock()
    ws.receive_text = AsyncMock()
    return ws


@pytest.fixture
def mock_config_service():
    """Mock ConfigService."""
    service = AsyncMock()
    service.load_configuration = Mock(return_value={
        "OLLAMA_HOST": "http://localhost:11434",
        "CHROMA_HOST": "localhost",
        "CHROMA_PORT": 8000
    })
    return service


# === TESTS ===

@pytest.mark.asyncio
async def test_ws_connection_accepted(mock_websocket, mock_health_monitor, mock_service_manager, mock_config_service, mock_config):
    """Test 1: Verbindungsaufbau – Client verbindet, initial_status empfangen."""
    
    from src.api.v1.services import websocket_status_stream
    
    # Setup: receive_text blockiert (idle)
    async def blocking_receive():
        await asyncio.sleep(10)
    
    mock_websocket.receive_text.side_effect = blocking_receive
    
    with patch('src.api.v1.services.get_health_monitor', return_value=mock_health_monitor):
        with patch('src.api.v1.services.service_manager', mock_service_manager):
            with patch('src.api.v1.services.config_service', mock_config_service):
                with patch('src.api.v1.services.get_websocket_config', return_value=mock_config):
                    try:
                        await asyncio.wait_for(
                            websocket_status_stream(mock_websocket),
                            timeout=0.5
                        )
                    except asyncio.TimeoutError:
                        pass
    
    # Assertions
    mock_websocket.accept.assert_called_once()
    mock_websocket.send_json.assert_called()
    
    # Prüfe initial_status
    initial_calls = [c for c in mock_websocket.send_json.call_args_list if "initial_status" in str(c)]
    assert len(initial_calls) > 0, "initial_status sollte gesendet werden"


@pytest.mark.asyncio
async def test_ws_ping_pong_keepalive(mock_websocket, mock_health_monitor, mock_service_manager, mock_config_service, mock_config):
    """Test 2: Keepalive – Client sendet ping, Server antwortet pong, Verbindung bleibt offen."""
    
    from src.api.v1.services import websocket_status_stream
    
    # Setup: Client sendet "ping", dann idle
    receive_calls = [
        "ping",  # Client sendet ping
        asyncio.sleep(10),  # Idle → timeout
    ]
    call_count = [0]
    
    async def mock_receive():
        val = receive_calls[call_count[0]]
        call_count[0] += 1
        if asyncio.iscoroutine(val):
            await val
        return val
    
    mock_websocket.receive_text.side_effect = mock_receive
    
    with patch('src.api.v1.services.get_health_monitor', return_value=mock_health_monitor):
        with patch('src.api.v1.services.service_manager', mock_service_manager):
            with patch('src.api.v1.services.config_service', mock_config_service):
                with patch('src.api.v1.services.get_websocket_config', return_value=mock_config):
                    try:
                        await asyncio.wait_for(
                            websocket_status_stream(mock_websocket),
                            timeout=0.5
                        )
                    except asyncio.TimeoutError:
                        pass
    
    # Assertions
    mock_websocket.send_text.assert_called()
    
    # Prüfe, dass pong gesendet wurde
    pong_calls = [call for call in mock_websocket.send_text.call_args_list if "pong" in str(call)]
    assert len(pong_calls) > 0, "Server sollte pong gesendet haben"
    
    # Prüfe, dass WS nicht geschlossen wurde nach ping
    mock_websocket.close.assert_not_called()


@pytest.mark.asyncio
async def test_ws_event_throughput(mock_websocket, mock_health_monitor, mock_service_manager, mock_config_service, mock_config):
    """Test 3: Event-Durchsatz – HealthMonitor Event → status_change empfangen."""
    
    from src.api.v1.services import websocket_status_stream
    
    # Setup: Simuliere HealthMonitor-Event während Verbindung
    event_queue = None
    
    def capture_subscribe(callback):
        nonlocal event_queue
        event_queue = callback
        mock_health_monitor._subscribers.append(callback)
    
    mock_health_monitor.subscribe = capture_subscribe
    
    # Simulate idle nach Event
    mock_websocket.receive_text.side_effect = asyncio.TimeoutError()
    
    async def run_endpoint():
        with patch('src.api.v1.services.get_health_monitor', return_value=mock_health_monitor):
            with patch('src.api.v1.services.service_manager', mock_service_manager):
                with patch('src.api.v1.services.config_service', mock_config_service):
                    with patch('src.api.v1.services.get_websocket_config', return_value=mock_config):
                        try:
                            await asyncio.wait_for(
                                websocket_status_stream(mock_websocket),
                                timeout=0.3
                            )
                        except asyncio.TimeoutError:
                            pass
    
    # Starte Endpoint in Task
    endpoint_task = asyncio.create_task(run_endpoint())
    await asyncio.sleep(0.05)  # Lass Subscribe registrieren
    
    # Emuliere Event vom HealthMonitor
    if event_queue:
        test_event = {
            "service": "ollama",
            "new_status": "stopped",
            "details": {"running": False}
        }
        # Callback wird aufgerufen (nimmt Event in Queue)
        event_queue(test_event)
        await asyncio.sleep(0.05)
    
    await asyncio.sleep(0.3)  # Warte auf Verarbeitung
    await asyncio.cancel_task(endpoint_task) if not endpoint_task.done() else None
    
    # Assertions
    status_change_calls = [
        call for call in mock_websocket.send_json.call_args_list
        if call[0][0].get("type") == "status_change"
    ]
    assert len(status_change_calls) > 0, "Server sollte status_change Event gesendet haben"


@pytest.mark.asyncio
async def test_ws_disconnect_cleanup(mock_websocket, mock_health_monitor, mock_service_manager, mock_config_service, mock_config):
    """Test 4: Disconnect & Cleanup – Subscriber entfernt, keine Leaks."""
    
    from src.api.v1.services import websocket_status_stream
    from fastapi import WebSocketDisconnect
    
    # Setup: Client trennt sich
    mock_websocket.receive_text.side_effect = WebSocketDisconnect(code=1000)
    
    with patch('src.api.v1.services.get_health_monitor', return_value=mock_health_monitor):
        with patch('src.api.v1.services.service_manager', mock_service_manager):
            with patch('src.api.v1.services.config_service', mock_config_service):
                with patch('src.api.v1.services.get_websocket_config', return_value=mock_config):
                    try:
                        await websocket_status_stream(mock_websocket)
                    except Exception:
                        pass  # Erwartet
    
    # Assertions
    # Subscriber sollte entfernt sein
    initial_count = len(mock_health_monitor._subscribers)
    # Nach Disconnect sollten 0 Subscriber sein
    assert mock_health_monitor.unsubscribe.called, "unsubscribe sollte aufgerufen worden sein"
    assert len(mock_health_monitor._subscribers) == 0, "Keine Subscriber sollten nach Disconnect übrig sein"


@pytest.mark.asyncio
async def test_ws_backpressure_drop_oldest(mock_websocket, mock_health_monitor, mock_service_manager, mock_config_service, mock_config):
    """Test 5: Backpressure – > maxsize Events → Drop-Oldest ohne Crash."""
    
    from src.api.v1.services import websocket_status_stream
    
    # Setup: Mock Queue mit Drop-Oldest
    queue_override = None
    dropped_count = [0]
    
    original_queue = __import__('asyncio').Queue
    
    class MockQueueWithLimit:
        def __init__(self, maxsize=16):
            self.queue = []
            self.maxsize = maxsize
        
        async def get(self):
            if self.queue:
                return self.queue.pop(0)
            await asyncio.sleep(10)  # Idle
        
        def put_nowait(self, item):
            if len(self.queue) >= self.maxsize:
                self.queue.pop(0)  # Drop oldest
                dropped_count[0] += 1
            self.queue.append(item)
    
    def mock_queue_factory(maxsize):
        return MockQueueWithLimit(maxsize)
    
    # Mock receive_text für idle
    mock_websocket.receive_text.side_effect = asyncio.TimeoutError()
    
    async def run_endpoint():
        with patch('src.api.v1.services.get_health_monitor', return_value=mock_health_monitor):
            with patch('src.api.v1.services.service_manager', mock_service_manager):
                with patch('src.api.v1.services.config_service', mock_config_service):
                    with patch('src.api.v1.services.get_websocket_config', return_value=mock_config):
                        with patch('asyncio.Queue', side_effect=mock_queue_factory):
                            try:
                                await asyncio.wait_for(
                                    websocket_status_stream(mock_websocket),
                                    timeout=0.3
                                )
                            except (asyncio.TimeoutError, Exception):
                                pass
    
    endpoint_task = asyncio.create_task(run_endpoint())
    await asyncio.sleep(0.05)
    
    # Simuliere > maxsize Events
    if mock_health_monitor._subscribers:
        callback = mock_health_monitor._subscribers[0]
        for i in range(25):  # > 16 (maxsize)
            event = {"service": "ollama", "new_status": "running", "details": {}}
            try:
                callback(event)
            except Exception:
                pass  # Drop-Oldest keine Exception
    
    await asyncio.sleep(0.3)
    if not endpoint_task.done():
        endpoint_task.cancel()
        try:
            await endpoint_task
        except asyncio.CancelledError:
            pass
    
    # Assertions
    # WS sollte nicht geclosed worden sein
    mock_websocket.close.assert_not_called()
    # Mindestens einige Events sollten verworfen worden sein
    assert dropped_count[0] > 0, "Unter Backpressure sollten Events verworfen werden"


# === PARAMETRISIERTE TESTS ===

@pytest.mark.parametrize("client_msg,expected_response", [
    ("ping", "pong"),
    ("PING", "pong"),  # Case-insensitive
])
@pytest.mark.asyncio
async def test_ws_ping_variations(client_msg, expected_response, mock_websocket, mock_health_monitor, mock_service_manager, mock_config_service, mock_config):
    """Test: ping-Variationen (Case-insensitive)."""
    
    from src.api.v1.services import websocket_status_stream
    
    mock_websocket.receive_text.side_effect = [client_msg, asyncio.sleep(10)]
    
    with patch('src.api.v1.services.get_health_monitor', return_value=mock_health_monitor):
        with patch('src.api.v1.services.service_manager', mock_service_manager):
            with patch('src.api.v1.services.config_service', mock_config_service):
                with patch('src.api.v1.services.get_websocket_config', return_value=mock_config):
                    try:
                        await asyncio.wait_for(
                            websocket_status_stream(mock_websocket),
                            timeout=0.5
                        )
                    except asyncio.TimeoutError:
                        pass
    
    # pong sollte gesendet werden
    pong_calls = [call for call in mock_websocket.send_text.call_args_list if "pong" in str(call)]
    assert len(pong_calls) > 0


# === INTEGRATION (LEICHT) ===

@pytest.mark.asyncio
async def test_ws_lifecycle_full(mock_websocket, mock_health_monitor, mock_service_manager, mock_config_service, mock_config):
    """Integration: Vollständiger Lifecycle – Connect → Ping → Event → Disconnect."""
    
    from src.api.v1.services import websocket_status_stream
    from fastapi import WebSocketDisconnect
    
    sequence = ["ping", asyncio.sleep(0.1), WebSocketDisconnect(code=1000)]
    call_count = [0]
    
    async def mock_receive():
        val = sequence[call_count[0]]
        call_count[0] += 1
        if asyncio.iscoroutine(val):
            await val
            return None  # Nach sleep kein return
        if isinstance(val, Exception):
            raise val
        return val
    
    mock_websocket.receive_text.side_effect = mock_receive
    
    with patch('src.api.v1.services.get_health_monitor', return_value=mock_health_monitor):
        with patch('src.api.v1.services.service_manager', mock_service_manager):
            with patch('src.api.v1.services.config_service', mock_config_service):
                with patch('src.api.v1.services.get_websocket_config', return_value=mock_config):
                    await websocket_status_stream(mock_websocket)
    
    # Assertions
    mock_websocket.accept.assert_called_once()
    pong_sent = any("pong" in str(call) for call in mock_websocket.send_text.call_args_list)
    assert pong_sent, "pong sollte gesendet worden sein"
    mock_websocket.close.assert_not_called()  # Nur Client trennt sich
