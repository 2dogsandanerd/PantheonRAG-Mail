/**
 * Custom hook for real-time service status via WebSocket
 *
 * Features:
 * - WebSocket connection to backend
 * - Auto-reconnect with exponential backoff
 * - State management with useReducer
 * - Manual refresh fallback
 */

import { useReducer, useRef, useEffect, useCallback } from 'react';
import { getServicesStatus } from '../api/client';

// Action types
const Actions = {
  SET_INITIAL_STATUS: 'SET_INITIAL_STATUS',
  UPDATE_SERVICE: 'UPDATE_SERVICE',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  WEBSOCKET_CONNECTING: 'WEBSOCKET_CONNECTING',
  WEBSOCKET_CONNECTED: 'WEBSOCKET_CONNECTED',
  WEBSOCKET_DISCONNECTED: 'WEBSOCKET_DISCONNECTED',
  WEBSOCKET_RECONNECTING: 'WEBSOCKET_RECONNECTING',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// Initial state
const initialState = {
  data: null,
  loading: true,
  error: null,
  connected: false,
  reconnecting: false,
  connectionStatus: 'connecting', // 'connecting' | 'connected' | 'disconnected' | 'reconnecting'
  reconnectAttempt: 0,
  lastUpdated: null
};

// Reducer function
function serviceStatusReducer(state, action) {
  switch (action.type) {
    case Actions.SET_INITIAL_STATUS:
      return {
        ...state,
        data: action.payload,
        loading: false,
        error: null,
        lastUpdated: new Date()
      };

    case Actions.UPDATE_SERVICE:
      if (!state.data) return state;

      return {
        ...state,
        data: {
          ...state.data,
          [action.payload.service]: {
            ...action.payload.details,
            running: action.payload.new_status === 'running'
          }
        },
        lastUpdated: new Date()
      };

    case Actions.SET_LOADING:
      return { ...state, loading: action.payload };

    case Actions.SET_ERROR:
      return { ...state, error: action.payload, loading: false };

    case Actions.CLEAR_ERROR:
      return { ...state, error: null };

    case Actions.WEBSOCKET_CONNECTING:
      return {
        ...state,
        connected: false,
        connectionStatus: 'connecting',
        reconnecting: false
      };

    case Actions.WEBSOCKET_CONNECTED:
      return {
        ...state,
        connected: true,
        connectionStatus: 'connected',
        reconnecting: false,
        reconnectAttempt: 0,
        error: null
      };

    case Actions.WEBSOCKET_DISCONNECTED:
      return {
        ...state,
        connected: false,
        connectionStatus: 'disconnected'
      };

    case Actions.WEBSOCKET_RECONNECTING:
      return {
        ...state,
        connected: false,
        connectionStatus: 'reconnecting',
        reconnecting: true,
        reconnectAttempt: action.payload || state.reconnectAttempt + 1
      };

    default:
      return state;
  }
}

/**
 * Hook for managing service status with WebSocket
 *
 * @param {Object} options - Configuration options
 * @param {string} options.wsUrl - WebSocket URL (default: auto-detect)
 * @param {number} options.reconnectDelay - Initial reconnect delay in ms (default: 1000)
 * @param {number} options.maxReconnectDelay - Max reconnect delay in ms (default: 30000)
 * @param {number} options.maxReconnectAttempts - Max reconnect attempts (default: 20)
 *
 * @returns {Object} Service status state and utilities
 */
export function useServiceStatus(options = {}) {
  const {
    wsUrl = null,
    reconnectDelay: initialReconnectDelay = 1000,
    maxReconnectDelay = 30000,
    maxReconnectAttempts = 20  // Increased from 10 to 20 for better resilience
  } = options;

  const [state, dispatch] = useReducer(serviceStatusReducer, initialState);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectDelayRef = useRef(initialReconnectDelay);
  const reconnectAttemptRef = useRef(0); // Use ref instead of state to avoid dependency loop
  const pingIntervalRef = useRef(null);

  // Get WebSocket URL
  const getWebSocketUrl = useCallback(() => {
    if (wsUrl) return wsUrl;

    // Use dynamic port from Electron if available
    if (window.electronAPI?.getWebSocketURL) {
      return window.electronAPI.getWebSocketURL();
    }

    // Fallback for non-Electron environments or if not initialized yet
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.hostname}:33800/api/v1/services/ws/status`;
  }, [wsUrl]);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    // Clean up previous connection before creating a new one
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Clear any pending reconnect
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Check max attempts
    if (reconnectAttemptRef.current >= maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnect attempts reached');
      dispatch({ type: Actions.SET_ERROR, payload: 'Failed to connect after multiple attempts' });
      return;
    }

    // Increment attempt counter
    reconnectAttemptRef.current += 1;

    dispatch({ type: Actions.WEBSOCKET_CONNECTING });

    const url = getWebSocketUrl();
    console.log('[WebSocket] Connecting to:', url);

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('[WebSocket] Connected');
        dispatch({ type: Actions.WEBSOCKET_CONNECTED });

        // Reset reconnect delay and attempt counter on successful connection
        reconnectDelayRef.current = initialReconnectDelay;
        reconnectAttemptRef.current = 0;

        // Start ping interval
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 15000);
      };

      ws.onmessage = (event) => {
        // Handle text messages (ping/pong) separately from JSON
        if (event.data === 'pong') {
          // Server keepalive response - ignore silently
          return;
        }

        try {
          const message = JSON.parse(event.data);

          if (message.type === 'initial_status') {
            console.log('[WebSocket] Initial status received:', message.data);
            dispatch({ type: Actions.SET_INITIAL_STATUS, payload: message.data });
          } else if (message.type === 'status_change') {
            console.log('[WebSocket] Status change:', message.data);
            dispatch({ type: Actions.UPDATE_SERVICE, payload: message.data });

            // Optional: Browser notification for stopped services
            if (Notification.permission === 'granted' && message.data.new_status === 'stopped') {
              new Notification('Service Status Changed', {
                body: `${message.data.service} is now ${message.data.new_status}`,
                icon: '/icon.png',
                tag: `service-${message.data.service}` // Prevent duplicate notifications
              });
            }
          }
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', err, 'Raw data:', event.data);
        }
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
      };

      ws.onclose = () => {
        console.log('[WebSocket] Disconnected');
        dispatch({ type: Actions.WEBSOCKET_DISCONNECTED });

        // Clean up ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        wsRef.current = null;

        // Exponential backoff reconnect
        const delay = Math.min(reconnectDelayRef.current, maxReconnectDelay);

        // Escalating reconnect logging (1st, 5th, 10th, 15th, 20th attempts)
        const shouldLog = reconnectAttemptRef.current === 1 ||
                         reconnectAttemptRef.current % 5 === 0;

        if (shouldLog) {
          console.log(
            `[WebSocket] Reconnecting (attempt ${reconnectAttemptRef.current}/${maxReconnectAttempts}) in ${delay}ms...`
          );
        }

        dispatch({ type: Actions.WEBSOCKET_RECONNECTING });

        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 2, maxReconnectDelay);
          connectWebSocket();
        }, delay);
      };

      wsRef.current = ws;

    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
      dispatch({ type: Actions.SET_ERROR, payload: error.message });
    }
  }, [getWebSocketUrl, initialReconnectDelay, maxReconnectDelay, maxReconnectAttempts]); // Removed state.reconnectAttempt to prevent dependency loop

  // Manual refresh (fallback when WebSocket is down)
  const refreshStatus = useCallback(async () => {
    dispatch({ type: Actions.SET_LOADING, payload: true });

    try {
      const status = await getServicesStatus();
      dispatch({ type: Actions.SET_INITIAL_STATUS, payload: status });
      dispatch({ type: Actions.CLEAR_ERROR });
      return { success: true };
    } catch (error) {
      console.error('[Manual Refresh] Failed:', error);
      dispatch({ type: Actions.SET_ERROR, payload: error.message });
      return { success: false, error: error.message };
    }
  }, []);

  // Initialize WebSocket connection (only once on mount)
  useEffect(() => {
    connectWebSocket();

    // Request notification permission
    if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
      Notification.requestPermission();
    }

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty deps: only run once on mount, reconnect logic handled by ws.onclose

  return {
    ...state,
    refreshStatus
  };
}
