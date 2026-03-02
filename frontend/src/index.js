const { app, BrowserWindow, protocol, ipcMain, dialog, net } = require('electron');
const path = require('node:path');
const { spawn } = require('child_process');
const fs = require('fs');

// Disable GPU acceleration to prevent crashes in Linux environments without GPU
app.disableHardwareAcceleration();

// Register custom protocol for production builds
if (process.env.NODE_ENV === 'production') {
  protocol.registerSchemesAsPrivileged([
    {
      scheme: 'app',
      privileges: {
        standard: true,
        secure: true,
        supportFetchAPI: true,
        corsEnabled: true
      }
    }
  ]);
}

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

let backendProcess = null;
let backendPort = null;
let celeryProcess = null;

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m',
  white: '\x1b[37m',
  gray: '\x1b[90m'
};

/**
 * Starts the Python FastAPI backend process
 */
async function startBackend() {
  const projectRoot = path.join(__dirname, '../../..');
  const backendPath = path.join(projectRoot, 'backend');
  const logsPath = path.join(projectRoot, 'logs');

  if (!fs.existsSync(logsPath)) {
    fs.mkdirSync(logsPath, { recursive: true });
  }

  const backendLogStream = fs.createWriteStream(path.join(logsPath, 'backend.log'), { flags: 'a' });
  const backendErrorStream = fs.createWriteStream(path.join(logsPath, 'backend.error.log'), { flags: 'a' });

  const BACKEND_PORT = 33800;

  try {
    const response = await fetch(`http://localhost:${BACKEND_PORT}/api/health`);
    if (response.ok) {
      console.log(`${colors.bright}${colors.green}[Main]${colors.reset} ${colors.green}Backend already running on port ${BACKEND_PORT} (Docker?). Skipping spawn.${colors.reset}`);
      return BACKEND_PORT;
    }
  } catch (e) {
    console.log(`${colors.blue}[Main]${colors.reset} Backend not detected on port ${BACKEND_PORT}. Spawning local process...`);
  }

  console.log(`${colors.bright}${colors.cyan}==================================${colors.reset}`);
  console.log(`${colors.bright}${colors.blue}[Main]${colors.reset} Starting Python backend...`);
  console.log(`${colors.blue}[Main]${colors.reset} Backend directory: ${colors.dim}${backendPath}${colors.reset}`);
  console.log(`${colors.bright}${colors.green}[Main]${colors.reset} Backend port: ${colors.bright}${BACKEND_PORT}${colors.reset}`);
  console.log(`${colors.bright}${colors.cyan}==================================${colors.reset}`);

  const isWindows = process.platform === 'win32';
  const venvPython = isWindows
    ? path.join(projectRoot, 'venv', 'Scripts', 'python.exe')
    : path.join(projectRoot, 'venv', 'bin', 'python3');

  console.log(`${colors.blue}[Main]${colors.reset} Using Python from: ${colors.dim}${venvPython}${colors.reset}`);

  backendProcess = spawn(venvPython, [
    '-m', 'uvicorn',
    'src.main:app',
    '--host', '127.0.0.1',
    '--port', BACKEND_PORT.toString(),
    '--log-level', 'info'
  ], {
    cwd: backendPath,
    stdio: 'pipe',
    env: { ...process.env }
  });

  function formatBackendLog(message, stream) {
    const lowerMsg = message.toLowerCase();
    if (lowerMsg.includes('error') || lowerMsg.includes('exception') || lowerMsg.includes('traceback') || lowerMsg.includes('failed')) {
      console.error(`${colors.bright}${colors.red}[Backend ERROR]${colors.reset} ${colors.red}${message}${colors.reset}`);
    } else if (lowerMsg.includes('warning') || lowerMsg.includes('warn')) {
      console.warn(`${colors.bright}${colors.yellow}[Backend WARN]${colors.reset} ${colors.yellow}${message}${colors.reset}`);
    } else if (lowerMsg.includes('startup complete') || lowerMsg.includes('started server') || lowerMsg.includes('application startup') || lowerMsg.includes('✅')) {
      console.log(`${colors.bright}${colors.green}[Backend OK]${colors.reset} ${colors.green}${message}${colors.reset}`);
    } else if (lowerMsg.includes('debug') || lowerMsg.includes('loaded config')) {
      console.log(`${colors.dim}${colors.gray}[Backend DEBUG]${colors.reset} ${colors.gray}${message}${colors.reset}`);
    } else if (lowerMsg.includes('info') || stream === 'stderr') {
      console.log(`${colors.cyan}[Backend INFO]${colors.reset} ${message}`);
    } else {
      console.log(`${colors.white}[Backend]${colors.reset} ${message}`);
    }
  }

  backendProcess.stdout.on('data', (data) => {
    const messages = data.toString().trim().split('\n');
    const timestamp = new Date().toISOString();
    messages.forEach(msg => {
      if (msg.trim()) {
        formatBackendLog(msg, 'stdout');
        backendLogStream.write(`[${timestamp}] ${msg}\n`);
      }
    });
  });

  backendProcess.stderr.on('data', (data) => {
    const messages = data.toString().trim().split('\n');
    const timestamp = new Date().toISOString();
    messages.forEach(msg => {
      if (msg.trim()) {
        formatBackendLog(msg, 'stderr');
        backendErrorStream.write(`[${timestamp}] ${msg}\n`);
      }
    });
  });

  backendProcess.on('close', (code) => {
    if (code === 0) {
      console.log(`${colors.green}[Backend]${colors.reset} Process exited cleanly (code ${code})`);
    } else {
      console.error(`${colors.bright}${colors.red}[Backend ERROR]${colors.reset} ${colors.red}Process exited with code ${code}${colors.reset}`);
    }
    backendProcess = null;
  });

  backendProcess.on('error', (error) => {
    console.error(`${colors.bright}${colors.red}[Backend ERROR]${colors.reset} ${colors.red}Failed to start: ${error.message}${colors.reset}`);
    backendProcess = null;
  });

  return BACKEND_PORT;
}

/**
 * Starts the Celery Worker process
 */
async function startCeleryWorker() {
  const projectRoot = path.join(__dirname, '../../..');
  const backendPath = path.join(projectRoot, 'backend');
  const logsPath = path.join(projectRoot, 'logs');

  const celeryLogStream = fs.createWriteStream(path.join(logsPath, 'celery.log'), { flags: 'a' });
  const celeryErrorStream = fs.createWriteStream(path.join(logsPath, 'celery.error.log'), { flags: 'a' });

  console.log(`${colors.bright}${colors.cyan}==================================${colors.reset}`);
  console.log(`${colors.bright}${colors.magenta}[Main]${colors.reset} Starting Celery Worker...`);
  console.log(`${colors.bright}${colors.cyan}==================================${colors.reset}`);

  const isWindows = process.platform === 'win32';
  const venvBin = isWindows
    ? path.join(projectRoot, 'venv', 'Scripts')
    : path.join(projectRoot, 'venv', 'bin');

  const celeryExecutable = path.join(venvBin, 'celery');

  console.log(`${colors.magenta}[Main]${colors.reset} Using Celery from: ${colors.dim}${celeryExecutable}${colors.reset}`);

  celeryProcess = spawn(celeryExecutable, [
    '-A', 'src.workers.celery_app',
    'worker',
    '--loglevel=info',
    '--concurrency=1'
  ], {
    cwd: backendPath,
    stdio: 'pipe',
    env: { ...process.env }
  });

  function formatCeleryLog(message, stream) {
    const lowerMsg = message.toLowerCase();
    if (lowerMsg.includes('error')) {
      console.error(`${colors.bright}${colors.red}[Celery ERROR]${colors.reset} ${colors.red}${message}${colors.reset}`);
    } else if (lowerMsg.includes('ready') || lowerMsg.includes('connected')) {
      console.log(`${colors.bright}${colors.green}[Celery OK]${colors.reset} ${colors.green}${message}${colors.reset}`);
    } else {
      console.log(`${colors.magenta}[Celery]${colors.reset} ${message}`);
    }
  }

  celeryProcess.stdout.on('data', (data) => {
    const messages = data.toString().trim().split('\n');
    const timestamp = new Date().toISOString();
    messages.forEach(msg => {
      if (msg.trim()) {
        formatCeleryLog(msg, 'stdout');
        celeryLogStream.write(`[${timestamp}] ${msg}\n`);
      }
    });
  });

  celeryProcess.stderr.on('data', (data) => {
    const messages = data.toString().trim().split('\n');
    const timestamp = new Date().toISOString();
    messages.forEach(msg => {
      if (msg.trim()) {
        formatCeleryLog(msg, 'stderr');
        celeryErrorStream.write(`[${timestamp}] ${msg}\n`);
      }
    });
  });

  celeryProcess.on('close', (code) => {
    console.log(`${colors.magenta}[Celery]${colors.reset} Process exited with code ${code}`);
    celeryProcess = null;
  });
}

async function waitForBackend(url, timeout = 30000) {
  const healthEndpoint = `${url}/api/health`;
  const startTime = Date.now();
  const pollInterval = 500;

  console.log(`${colors.blue}[Main]${colors.reset} Waiting for backend to be ready...`);
  console.log(`${colors.dim}${colors.gray}[Main]${colors.reset} ${colors.dim}Health endpoint: ${healthEndpoint}${colors.reset}`);

  while (Date.now() - startTime < timeout) {
    try {
      const response = await fetch(healthEndpoint);
      if (response.ok) {
        const data = await response.json();
        console.log(`${colors.bright}${colors.green}[Main]${colors.reset} ${colors.green}✅ Backend is ready!${colors.reset}`);
        return true;
      }
      console.log(`${colors.yellow}[Main]${colors.reset} Backend responded with status ${response.status}, retrying...`);
    } catch (error) {
      const elapsed = Date.now() - startTime;
      if (elapsed % 2500 < pollInterval) {
        console.log(`${colors.dim}${colors.gray}[Main]${colors.reset} ${colors.dim}Backend not ready yet (${Math.round(elapsed / 1000)}s elapsed)...${colors.reset}`);
      }
    }
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }
  const elapsedSeconds = Math.round((Date.now() - startTime) / 1000);
  throw new Error(`Backend failed to start within ${elapsedSeconds}s timeout`);
}

function createLoadingWindow() {
  const loadingWindow = new BrowserWindow({
    width: 400,
    height: 300,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });
  loadingWindow.loadFile(path.join(__dirname, '../../src/loading.html'));
  return loadingWindow;
}

const quitCelery = async () => {
  if (!celeryProcess || celeryProcess.killed) return;
  console.log(`${colors.yellow}[Main]${colors.reset} Stopping Celery Worker...`);
  celeryProcess.kill('SIGTERM');
  setTimeout(() => {
    if (celeryProcess && !celeryProcess.killed) {
      celeryProcess.kill('SIGKILL');
    }
  }, 2000);
};

const quitBackend = async () => {
  await quitCelery();

  if (!backendProcess || backendProcess.killed) {
    console.log(`${colors.blue}[Main]${colors.reset} Backend process is already stopped.`);
    return;
  }

  console.log(`${colors.yellow}[Main]${colors.reset} Initiating backend shutdown...`);

  try {
    const axios = require('axios');
    axios.post(`http://localhost:${backendPort}/api/shutdown`, {}, { timeout: 1000 }).catch(() => { });
  } catch (error) { }

  await new Promise(resolve => setTimeout(resolve, 200));

  console.log(`${colors.yellow}[Main]${colors.reset} Sending SIGTERM to backend process (PID: ${backendProcess.pid})...`);
  const termSuccess = backendProcess.kill('SIGTERM');
  if (!termSuccess) {
    console.error(`${colors.red}[Main ERROR]${colors.reset} ${colors.red}Failed to send SIGTERM.${colors.reset}`);
  }

  const killTimeout = setTimeout(() => {
    if (!backendProcess.killed) {
      console.log(`${colors.bright}${colors.red}[Main]${colors.reset} ${colors.red}Backend process did not exit gracefully. Forcing shutdown with SIGKILL...${colors.reset}`);
      backendProcess.kill('SIGKILL');
    }
  }, 3000);

  backendProcess.on('exit', () => {
    console.log(`${colors.green}[Main]${colors.reset} ✅ Backend process has exited.`);
    clearTimeout(killTimeout);
  });
};

const createWindow = (backendPort) => {
  const mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: MAIN_WINDOW_PRELOAD_WEBPACK_ENTRY,
      contextIsolation: true,
      nodeIntegration: false,
      webSecurity: !process.env.NODE_ENV || process.env.NODE_ENV === 'production',
    },
  });

  mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY);

  mainWindow.webContents.once('did-finish-load', () => {
    mainWindow.webContents.executeJavaScript(`
      window.__BACKEND_PORT__ = ${backendPort};
    `).then(() => {
      console.log(`${colors.green}[Main]${colors.reset} Backend port set in renderer: ${colors.bright}${backendPort}${colors.reset}`);
    });
  });

  if (process.env.NODE_ENV !== 'production') {
    mainWindow.webContents.openDevTools();
  }
};

app.whenReady().then(async () => {
  if (process.env.NODE_ENV === 'production') {
    protocol.handle('app', (request) => {
      const filePath = request.url.slice('app://'.length);
      return net.fetch(`file://${path.join(__dirname, filePath)}`);
    });
  }

  const loadingWindow = createLoadingWindow();

  try {
    backendPort = await startBackend();
    await waitForBackend(`http://localhost:${backendPort}`, 30000);

    // Start Celery Worker
    startCeleryWorker();

    loadingWindow.close();
    createWindow(backendPort);

  } catch (error) {
    loadingWindow.close();
    console.error(`${colors.bright}${colors.red}[Main ERROR]${colors.reset} ${colors.red}Failed to start backend: ${error.message}${colors.reset}`);

    const { dialog } = require('electron');
    await dialog.showMessageBox({
      type: 'error',
      title: 'Backend Startup Failed',
      message: 'Could not start the Python backend',
      detail: `Error: ${error.message}\n\nPlease check logs.`,
      buttons: ['OK']
    });
    app.quit();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow(backendPort);
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', async (event) => {
  event.preventDefault();
  console.log(`${colors.bright}${colors.yellow}[Main]${colors.reset} 'will-quit' event triggered. Starting cleanup...`);
  await quitBackend();
  console.log(`${colors.blue}[Main]${colors.reset} Cleanup complete. Exiting application.`);
  process.exit(0);
});

ipcMain.handle('dialog:openFolder', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openDirectory']
  });
  if (canceled) {
    return null;
  } else {
    return filePaths[0];
  }
});
