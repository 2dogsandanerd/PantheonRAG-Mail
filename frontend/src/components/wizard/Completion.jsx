import React from 'react';
import { Box, Typography } from '@mui/material';
import { CheckCircleOutline } from '@mui/icons-material';

const Completion = () => {
    return (
        <Box textAlign="center" py={4}>
            <CheckCircleOutline sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
                Setup Complete!
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
                Your system is configured and ready to use. You can now start using the AI Assistant to draft emails.
            </Typography>
        </Box>
    );
};

export default Completion;
