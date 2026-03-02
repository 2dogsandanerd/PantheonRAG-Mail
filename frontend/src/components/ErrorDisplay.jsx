import React from 'react';
import { Alert, AlertTitle, Button, Box } from '@mui/material';
import { Refresh, ErrorOutline } from '@mui/icons-material';
import PropTypes from 'prop-types';

/**
 * ErrorDisplay Component
 *
 * Displays errors in a consistent, user-friendly way with optional retry button.
 *
 * @param {string|Error} error - Error message or Error object
 * @param {Function} onRetry - Optional retry callback
 * @param {string} title - Error title (default: "Error")
 * @param {string} severity - Alert severity: 'error'|'warning'|'info' (default: 'error')
 *
 * @example
 * <ErrorDisplay error="Failed to load data" onRetry={() => fetchData()} />
 * <ErrorDisplay error={new Error('Network error')} title="Connection Failed" />
 */
export function ErrorDisplay({
  error,
  onRetry,
  title = 'Error',
  severity = 'error'
}) {
  // Extract error message from Error object or string
  const errorMessage = error instanceof Error
    ? error.message
    : String(error);

  return (
    <Box sx={{ my: 2 }}>
      <Alert
        severity={severity}
        icon={<ErrorOutline />}
        action={
          onRetry && (
            <Button
              color="inherit"
              size="small"
              startIcon={<Refresh />}
              onClick={onRetry}
            >
              Retry
            </Button>
          )
        }
      >
        <AlertTitle>{title}</AlertTitle>
        {errorMessage}
      </Alert>
    </Box>
  );
}

ErrorDisplay.propTypes = {
  error: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.instanceOf(Error),
  ]).isRequired,
  onRetry: PropTypes.func,
  title: PropTypes.string,
  severity: PropTypes.oneOf(['error', 'warning', 'info']),
};

export default ErrorDisplay;
