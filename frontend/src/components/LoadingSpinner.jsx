import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import PropTypes from 'prop-types';

/**
 * LoadingSpinner Component
 *
 * Displays a centered loading spinner with optional message.
 *
 * @param {string} message - Loading message to display below spinner
 * @param {number} size - Size of spinner in pixels (default: 40)
 * @param {string} color - Color of spinner: 'primary'|'secondary'|'inherit' (default: 'primary')
 *
 * @example
 * <LoadingSpinner message="Loading emails..." />
 * <LoadingSpinner message="Processing..." size={60} color="secondary" />
 */
export function LoadingSpinner({
  message = 'Loading...',
  size = 40,
  color = 'primary'
}) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '200px',
        padding: 4,
      }}
    >
      <CircularProgress size={size} color={color} />
      {message && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mt: 2 }}
        >
          {message}
        </Typography>
      )}
    </Box>
  );
}

LoadingSpinner.propTypes = {
  message: PropTypes.string,
  size: PropTypes.number,
  color: PropTypes.oneOf(['primary', 'secondary', 'inherit']),
};

export default LoadingSpinner;
