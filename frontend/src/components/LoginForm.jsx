import React, { useState } from 'react';
import {
    Container,
    Box,
    Paper,
    TextField,
    Button,
    Typography,
    Alert,
    CircularProgress,
    Divider,
} from '@mui/material';
import { Lock as LockIcon } from '@mui/icons-material';
import { authService } from '../api/auth';

/**
 * LoginForm — zeigt Login und Register in einer Komponente.
 * Props:
 *   onLoginSuccess(user) — wird nach erfolgreichem Login aufgerufen
 */
function LoginForm({ onLoginSuccess }) {
    const [mode, setMode] = useState('login'); // 'login' | 'register'
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            if (mode === 'register') {
                // Zuerst registrieren
                await authService.register(username, email, password);
                // Dann automatisch einloggen
                await authService.login(username, password);
            } else {
                await authService.login(username, password);
            }
            // User-Daten vom Backend holen
            const user = await authService.getMe();
            authService.setUser(user);
            onLoginSuccess(user);
        } catch (err) {
            const detail = err.response?.data?.detail;
            if (detail) {
                setError(detail);
            } else {
                setError('Login fehlgeschlagen. Bitte prüfe Benutzername und Passwort.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="xs" sx={{ mt: 10 }}>
            <Paper elevation={4} sx={{ p: 4, borderRadius: 2 }}>
                {/* Logo / Titel */}
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
                    <LockIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                    <Typography variant="h5" fontWeight="bold">
                        PantheonMail
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {mode === 'login' ? 'Bitte anmelden' : 'Neues Konto erstellen'}
                    </Typography>
                </Box>

                {/* Fehlermeldung */}
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}

                {/* Formular */}
                <Box component="form" onSubmit={handleSubmit}>
                    <TextField
                        fullWidth
                        label="Benutzername"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        margin="normal"
                        required
                        autoComplete="username"
                        autoFocus
                    />

                    {/* Email nur bei Registrierung */}
                    {mode === 'register' && (
                        <TextField
                            fullWidth
                            label="E-Mail"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            margin="normal"
                            required
                            autoComplete="email"
                        />
                    )}

                    <TextField
                        fullWidth
                        label="Passwort"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        margin="normal"
                        required
                        autoComplete="current-password"
                    />

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        size="large"
                        disabled={loading}
                        sx={{ mt: 3, mb: 1 }}
                    >
                        {loading ? (
                            <CircularProgress size={24} color="inherit" />
                        ) : mode === 'login' ? (
                            'Anmelden'
                        ) : (
                            'Konto erstellen'
                        )}
                    </Button>
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Modus wechseln */}
                <Button
                    fullWidth
                    variant="text"
                    onClick={() => {
                        setMode(mode === 'login' ? 'register' : 'login');
                        setError('');
                    }}
                    disabled={loading}
                >
                    {mode === 'login'
                        ? 'Noch kein Konto? Registrieren'
                        : 'Bereits registriert? Anmelden'}
                </Button>
            </Paper>
        </Container>
    );
}

export default LoginForm;
