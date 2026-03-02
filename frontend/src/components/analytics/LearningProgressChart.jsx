import React, { useState } from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

export default function LearningProgressChart() {
  const [data, setData] = useState([
    { date: 'Oct 1', count: 12 },
    { date: 'Oct 2', count: 18 },
    { date: 'Oct 3', count: 15 },
    { date: 'Oct 4', count: 22 },
    { date: 'Oct 5', count: 28 },
    { date: 'Oct 6', count: 24 },
    { date: 'Oct 7', count: 35 },
    { date: 'Oct 8', count: 32 },
    { date: 'Oct 9', count: 40 },
    { date: 'Oct 10', count: 38 },
    { date: 'Oct 11', count: 45 },
    { date: 'Oct 12', count: 42 },
    { date: 'Oct 13', count: 50 },
    { date: 'Oct 14', count: 48 },
    { date: 'Oct 15', count: 55 },
    { date: 'Oct 16', count: 58 },
    { date: 'Oct 17', count: 62 },
    { date: 'Oct 18', count: 60 },
    { date: 'Oct 19', count: 68 },
    { date: 'Oct 20', count: 65 },
    { date: 'Oct 21', count: 72 },
    { date: 'Oct 22', count: 70 },
    { date: 'Oct 23', count: 78 },
    { date: 'Oct 24', count: 75 },
    { date: 'Oct 25', count: 82 },
    { date: 'Oct 26', count: 80 },
    { date: 'Oct 27', count: 88 },
    { date: 'Oct 28', count: 85 },
    { date: 'Oct 29', count: 92 },
    { date: 'Oct 30', count: 90 }
  ]);

  return (
    <Card sx={{ 
      background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
      border: '1px solid #444'
    }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          📈 Learning Progress (Last 30 Days)
        </Typography>

        <Box sx={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="date" stroke="#B0B0B0" />
              <YAxis stroke="#B0B0B0" />
              <Tooltip
                contentStyle={{ 
                  backgroundColor: '#2A2A2A', 
                  border: '1px solid #444',
                  borderRadius: 8
                }}
                labelStyle={{ color: '#E0E0E0' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#4CAF50"
                strokeWidth={2}
                dot={{ fill: '#4CAF50', r: 4 }}
                activeDot={{ r: 6, fill: '#42a5f5' }}
                name="Learning Pairs"
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
}