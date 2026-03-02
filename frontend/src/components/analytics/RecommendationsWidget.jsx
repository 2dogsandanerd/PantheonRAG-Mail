import React, { useState } from 'react';
import { Card, CardContent, Typography, Alert, Stack } from '@mui/material';

export default function RecommendationsWidget() {
  const [recommendations, setRecommendations] = useState([
    { type: 'success', message: '✅ Good job on maintaining high engagement levels!' },
    { type: 'focus', message: '🎯 Focus on reducing average response time to improve efficiency' },
    { type: 'warning', message: '⚠️ Warning: Reply rate has decreased by 5% this week' }
  ]);

  const getSeverity = (type) => {
    if (type === 'success') return 'success';
    if (type === 'warning') return 'warning';
    if (type === 'focus') return 'info';
    return 'info';
  };

  return (
    <Card sx={{ 
      background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
      border: '1px solid #444'
    }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          💡 Learning Recommendations
        </Typography>

        <Stack spacing={2} sx={{ mt: 2 }}>
          {recommendations.map((rec, i) => (
            <Alert key={i} severity={getSeverity(rec.type)}>
              {rec.message}
            </Alert>
          ))}

          {recommendations.length === 0 && (
            <Typography color="text.secondary">
              No recommendations at this time. Keep up the good work!
            </Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}