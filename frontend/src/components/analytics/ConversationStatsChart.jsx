import React, { useState } from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

export default function ConversationStatsChart() {
  const [data, setData] = useState([
    { status: 'Completed', count: 85, color: '#4CAF50' },
    { status: 'In Progress', count: 23, color: '#2196F3' },
    { status: 'Failed', count: 7, color: '#F44336' }
  ]);

  return (
    <Card sx={{ 
      background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
      border: '1px solid #444'
    }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          📊 Conversations by Status
        </Typography>

        <Box sx={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="status" stroke="#B0B0B0" />
              <YAxis stroke="#B0B0B0" />
              <Tooltip
                contentStyle={{ 
                  backgroundColor: '#2A2A2A', 
                  border: '1px solid #444',
                  borderRadius: 8
                }}
              />
              <Bar
                dataKey="count"
                fill="#4CAF50"
                radius={[4, 4, 0, 0]}
              >
                {data.map((entry, index) => (
                  <rect key={`rect-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
}