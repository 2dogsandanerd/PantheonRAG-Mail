# Authentication Guide — PantheonMail v5.0

Dieses Dokument beschreibt das JWT-Authentifizierungssystem von PantheonMail.

---

## 📋 Übersicht

PantheonMail v5.0 verwendet ein **vollständiges JWT-Authentifizierungssystem** mit:

- **Access Tokens** (kurze Lebensdauer, für API-Requests)
- **Refresh Tokens** (lange Lebensdauer, zum Erneuern von Access Tokens)
- **Auto-Refresh** bei 401-Fehlern
- **Development Mode** zum Deaktivieren der Auth für lokale Entwicklung

---

## 🔐 Architektur

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Frontend   │     │   Backend API   │     │  Datenbank   │
│  (Electron)  │────►│   (FastAPI)     │────►│   (SQLite)   │
│              │     │                 │     │              │
│ • LoginForm  │     │ • /auth/login   │     │ • User-Tabelle│
│ • AuthState  │     │ • /auth/refresh │     │ • JWT Secret │
│ • TokenStore │     │ • /auth/me      │     │              │
└──────────────┘     └─────────────────┘     └──────────────┘
```

---

## 🚀 Quick Start

### Development (ohne Auth)

**1. `.env` konfigurieren:**
```env
DEV_MODE=true
```

**2. Backend starten:**
```bash
docker-compose -f docker-compose-modular.yml up --build
```

**3. Frontend starten:**
```bash
cd frontend && npm start
```

**Ergebnis:** Keine Login erforderlich – App öffnet sich direkt mit allen Features.

---

### Production (mit Auth)

**1. JWT_SECRET_KEY generieren:**
```bash
openssl rand -hex 32
# Beispiel-Ausgabe: a1b2c3d4e5f6...
```

**2. `.env` konfigurieren:**
```env
DEV_MODE=false
JWT_SECRET_KEY=a1b2c3d4e5f6...  # Dein generierter Key
```

**3. Backend starten:**
```bash
docker-compose -f docker-compose-modular.yml up -d
```

**4. Ersten Admin-User anlegen:**
```bash
curl -X POST http://localhost:33800/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "sicheres_passwort_123"
  }'
```

**5. Login durchführen:**
```bash
curl -X POST http://localhost:33800/api/v1/auth/login \
  -d "username=admin&password=sicheres_passwort_123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 📡 API Endpoints

### POST `/api/v1/auth/register`

Neuen Benutzer registrieren.

**Request:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "is_active": true,
  "role": "user"
}
```

---

### POST `/api/v1/auth/login`

Benutzer anmelden.

**Request (Form Data):**
```
username=admin
password=secure_password
```

**Response (200):**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

---

### POST `/api/v1/auth/refresh`

Access Token erneuern.

**Request:**
```
GET /api/v1/auth/refresh?refresh_token=eyJhbGci...
```

**Response (200):**
```json
{
  "access_token": "eyJhbGci...",  // Neuer Access Token
  "refresh_token": "eyJhbGci...",  // Neuer Refresh Token (Rotation)
  "token_type": "bearer"
}
```

---

### GET `/api/v1/auth/me`

Aktuellen Benutzer abrufen (geschützt).

**Request:**
```
GET /api/v1/auth/me
Authorization: Bearer eyJhbGci...
```

**Response (200):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_active": true,
  "role": "admin"
}
```

---

## 🔑 Token-Verwaltung

### Token-Storage (Frontend)

Das Frontend speichert Tokens im `localStorage`:

```javascript
// Schlüssel
const TOKEN_KEY = 'pantheonmail_token';
const REFRESH_TOKEN_KEY = 'pantheonmail_refresh_token';
const USER_KEY = 'pantheonmail_user';

// Speichern
localStorage.setItem(TOKEN_KEY, access_token);
localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
localStorage.setItem(USER_KEY, JSON.stringify(user));

// Abrufen
const token = localStorage.getItem(TOKEN_KEY);
const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
const user = JSON.parse(localStorage.getItem(USER_KEY));

// Löschen (Logout)
localStorage.removeItem(TOKEN_KEY);
localStorage.removeItem(REFRESH_TOKEN_KEY);
localStorage.removeItem(USER_KEY);
```

### Auto-Refresh Interceptor

Das Frontend erneuert Tokens automatisch bei 401-Fehlern:

```javascript
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Bei 401: Refresh versuchen
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        await authService.refreshToken();
        const token = authService.getToken();
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return client(originalRequest);
      } catch (refreshError) {
        // Refresh fehlgeschlagen → Logout
        authService.logout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

---

## 🛠️ Development Mode

### Funktionsweise

Wenn `DEV_MODE=true`:

1. **Kein JWT erforderlich**: Alle Endpoints sind ohne Token zugänglich
2. **Dummy-User**: `get_current_user()`返回 einen Dummy-User
   ```python
   User(
       username="dev_user",
       email="dev@localhost",
       is_active=True,
       role="admin"
   )
   ```
3. **Kein Login-Form**: Frontend zeigt direkt die Haupt-UI
4. **Keine Token-Validierung**: `decode_token()` wird nicht aufgerufen

### Umschalten Production

```bash
# 1. .env bearbeiten
DEV_MODE=false
JWT_SECRET_KEY=<dein_key>

# 2. Backend neu starten
docker-compose restart email_assistant

# 3. Browser-Cache leeren (localStorage)
# 4. Login durchführen
```

---

## 🔒 Security Best Practices

### Für Production

1. **JWT_SECRET_KEY sicher aufbewahren**
   - Niemals im Code hardcoden
   - Nur in `.env` oder Environment-Variablen
   - Regelmäßig rotieren (alle 90 Tage)

2. **HTTPS verwenden**
   - Tokens niemals über unverschlüsselte Verbindungen
   - Especially wichtig für Login/Refresh

3. **Token-Expiry konfigurieren**
   ```python
   # In src/core/auth.py
   ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Kurzlebig
   REFRESH_TOKEN_EXPIRE_DAYS = 7     # Langlebig
   ```

4. **Rate Limiting aktivieren**
   - Login-Endpunkte gegen Brute-Force schützen
   - Siehe `03-rate-limiting.md`

5. **Logout implementieren**
   - Tokens clientseitig löschen
   - Optional: Refresh-Token-Blacklist im Backend

---

## 🐛 Troubleshooting

### 401 Unauthorized bei allen Requests

**Ursache:** Token fehlt oder ist ungültig

**Lösung:**
```bash
# Token prüfen
curl -H "Authorization: Bearer DEIN_TOKEN" http://localhost:33800/api/v1/auth/me

# Neu login
curl -X POST http://localhost:33800/api/v1/auth/login -d "username=admin&password=..."
```

### Refresh Token expired

**Ursache:** Refresh Token ist abgelaufen (nach 7 Tagen)

**Lösung:** Erneut anmelden
```bash
curl -X POST http://localhost:33800/api/v1/auth/login ...
```

### DEV_MODE=true aber Login wird angezeigt

**Ursache:** Frontend-Cache oder alte Tokens

**Lösung:**
1. Browser DevTools öffnen
2. Application → LocalStorage → Alle `pantheonmail_*` Keys löschen
3. Seite neu laden

### JWT_SECRET_KEY nicht gesetzt

**Fehler:** `JWT_SECRET_KEY is not set` in Backend-Logs

**Lösung:**
```bash
# In .env eintragen
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Backend neu starten
docker-compose restart email_assistant
```

---

## 📚 Weitere Ressourcen

- **Changelog:** [CHANGELOG.md](CHANGELOG.md) — Alle Änderungen in v5.0
- **README:** [../readme_v4.md](../readme_v4.md) — Übersicht & Quick Start
- **API-Docs:** http://localhost:33800/api/v1/docs — Interaktive Swagger-Dokumentation
- **Planung:** [../planung/todo/01-authentication.md](../planung/todo/01-authentication.md) — Implementierungsplan
- **Frontend:** [../planung/todo/02-frontend-login.md](../planung/todo/02-frontend-login.md) — Frontend-Login-Guide

---

## 🎯 Nächste Schritte

### Geplant für v5.1
- [ ] **Tenant Isolation**: Multi-User mit Datentrennung
- [ ] **RBAC**: Rollenbasierte Berechtigungen (Admin/User/Read-only)
- [ ] **Password Reset**: E-Mail-basierte Zurücksetzung
- [ ] **2FA**: Zwei-Faktor-Authentifizierung

### Contributing
Fehler gefunden oder Verbesserungsvorschlag? Siehe [CONTRIBUTING.md](../CONTRIBUTING.md).
