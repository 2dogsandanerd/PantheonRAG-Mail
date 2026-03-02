/**
 * Preload Script
 *
 * Exposes safe Electron APIs to the renderer process via contextBridge.
 *
 * This runs in a privileged context with access to Node.js APIs, but
 * exposes only specific, safe methods to the web page via contextBridge.
 *
 * Security: contextIsolation must be enabled in webPreferences.
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose Electron APIs to window.electronAPI
contextBridge.exposeInMainWorld('electronAPI', {
  /**
   * Get backend URL
   *
   * In development: http://localhost:<dynamic_port>
   * In production: Could be configurable or different port
   *
   * @returns {string} Backend base URL
   */
  getBackendURL: () => {
    // Port is set by main process via executeJavaScript in window.__BACKEND_PORT__
    const port = window.__BACKEND_PORT__ || 33800;
    return `http://localhost:${port}`;
  },

  /**
   * Get WebSocket URL for service status endpoint
   *
   * Uses the same dynamic port as REST API
   *
   * @returns {string} WebSocket URL (ws://localhost:<dynamic_port>/api/v1/services/ws/status)
   */
  getWebSocketURL: () => {
    // Port is set by main process via executeJavaScript in window.__BACKEND_PORT__
    const port = window.__BACKEND_PORT__ || 33800;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//localhost:${port}/api/v1/services/ws/status`;
  },

  /**
   * Get current platform
   *
   * @returns {string} Platform: 'win32'|'darwin'|'linux'
   */
  getPlatform: () => {
    return process.platform;
  },

  /**
   * Get app version
   *
   * @returns {string} App version from package.json
   */
  getVersion: () => {
    return process.env.npm_package_version || '1.0.0';
  },

  /**
   * Check if running in development mode
   *
   * @returns {boolean} True if development
   */
  isDevelopment: () => {
    return process.env.NODE_ENV === 'development';
  },

  /**
   * Open a native folder selection dialog.
   * @returns {Promise<string|null>} The selected folder path or null if canceled.
   */
  selectFolder: () => ipcRenderer.invoke('dialog:openFolder'),

  // Future: Add more IPC methods as needed
  // openFileDialog: () => ipcRenderer.invoke('dialog:openFile'),
  // saveFileDialog: (content) => ipcRenderer.invoke('dialog:saveFile', content),
  // openExternal: (url) => ipcRenderer.invoke('shell:openExternal', url),
});

console.log('[Preload] Electron APIs exposed to renderer');
