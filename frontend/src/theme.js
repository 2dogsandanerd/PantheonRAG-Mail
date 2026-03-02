import { createTheme } from '@mui/material/styles';

/**
 * PantheonMail - Material-UI Theme
 *
 * Color Palette:
 * - Primary: Material Blue (#1976d2) - Main actions, headers
 * - Secondary: Material Pink (#dc004e) - Accents, notifications
 * - Success: Green (#4caf50) - Completed states
 * - Error: Red (#f44336) - Errors, warnings
 * - Warning: Orange (#ff9800) - Warnings, pending states
 *
 * Typography:
 * - Font Family: Roboto (Material Design standard)
 * - Base Size: 14px
 * - Scale: 1.2 (modular scale)
 *
 * Spacing:
 * - Base Unit: 8px
 * - Usage: theme.spacing(1) = 8px, theme.spacing(2) = 16px, etc.
 */

export const theme = createTheme({
  palette: {
    mode: 'dark', // 🌙 DARK METAL MODE
    primary: {
      main: '#42a5f5', // Lighter blue for dark mode
      light: '#80d6ff',
      dark: '#0077c2',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#ff5983', // Lighter pink for dark mode
      light: '#ff8bb4',
      dark: '#c62055',
      contrastText: '#ffffff',
    },
    success: {
      main: '#4caf50', // ✅ Keep green
      light: '#80e27e',
      dark: '#087f23',
    },
    error: {
      main: '#f44336', // ❌ Keep red
      light: '#ff7961',
      dark: '#ba000d',
    },
    warning: {
      main: '#ff9800',
      light: '#ffc947',
      dark: '#c66900',
    },
    info: {
      main: '#2196f3',
      light: '#64b5f6',
      dark: '#1976d2',
    },
    background: {
      default: '#2C2C2C', // 🔲 Dark Metal Base
      paper: '#1E1E1E', // 🔲 Darker Paper for cards
    },
    text: {
      primary: '#E0E0E0', // ⚪ Light gray text
      secondary: '#B0B0B0', // ⚪ Dimmer gray
      disabled: 'rgba(255, 255, 255, 0.38)',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Arial',
      'sans-serif',
    ].join(','),
    fontSize: 14,
    fontWeightLight: 300,
    fontWeightRegular: 400,
    fontWeightMedium: 500,
    fontWeightBold: 700,
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.6,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.43,
    },
    button: {
      textTransform: 'none', // Disable uppercase
      fontWeight: 500,
    },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.66,
    },
  },
  spacing: 8, // 8px base unit
  shape: {
    borderRadius: 8, // 8px default border radius
  },
  components: {
    // 🎨 DARK METAL: No white edges!
    MuiCssBaseline: {
      styleOverrides: (theme) => ({
        body: {
          margin: 0,
          padding: 0,
          background: 'linear-gradient(145deg, #3A3A3A, #2C2C2C)',
          backgroundAttachment: 'fixed',
          minHeight: '100vh',
          width: '100%',
          overflow: 'auto',
        },
        '#root': {
          minHeight: '100vh',
        },
      }),
    },
    // 🔲 Metal Paper with gradient and border
    MuiPaper: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
          border: '1px solid #444',
          boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.5)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 16px',
          fontSize: '0.875rem',
        },
        contained: {
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.4)',
          '&:hover': {
            boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.6)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.5)',
          background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
          border: '1px solid #444',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            '& fieldset': {
              borderColor: '#555',
            },
            '&:hover fieldset': {
              borderColor: '#777',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#42a5f5',
            },
          },
        },
      },
    },
    // 🎯 Tabs styling for dark metal
    MuiTab: {
      styleOverrides: {
        root: {
          color: '#B0B0B0',
          '&.Mui-selected': {
            color: '#42a5f5',
          },
        },
      },
    },
  },
});

export default theme;
