import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

export default function EngagementScoreCard() {
  const [data, setData] = useState({
    score: 85,
    effort_level: "High Effort",
    metrics: {
      total_conversations: 1247,
      avg_response_time: "2.3",
      reply_rate: 78,
      avg_conversation_length: 4.2
    }
  });

  const getColor = (score) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'info.main';
    if (score >= 40) return 'warning.main';
    return 'error.main';
  };

  const getEffortColor = (effort) => {
    if (effort === "High Effort" || effort === "Critical") return 'success.main';
    if (effort === "Medium Effort") return 'info.main';
    if (effort === "Low Effort") return 'warning.main';
    return 'text.primary';
  };

  return (
    <Card sx={{ 
      background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
      border: '1px solid #444'
    }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          🎯 Customer Engagement Score
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 2 }}>
          <Typography variant="h3" sx={{ color: getColor(data.score) }}>
            {data.score}
          </Typography>
          <Typography variant="h6" color="text.secondary">
            / 100
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
          <Box sx={{ color: getEffortColor(data.effort_level) }}>
            {data.score >= 50 ? <TrendingUp /> : <TrendingDown />}
          </Box>
          <Typography variant="body2" color="text.secondary">
            {data.effort_level}
          </Typography>
        </Box>

        <Box sx={{ mt: 3, p: 2, background: 'rgba(255, 255, 255, 0.02)', borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom color="text.secondary">
            Metrics
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption">Conversations: {data.metrics.total_conversations}</Typography>
            <Typography variant="caption">Avg Time: {data.metrics.avg_response_time}h</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="caption">Reply Rate: {data.metrics.reply_rate}%</Typography>
            <Typography variant="caption">Avg Length: {data.metrics.avg_conversation_length}</Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}