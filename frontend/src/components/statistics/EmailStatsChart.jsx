import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getEmailStatistics } from '../../api/client';

export default function EmailStatsChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch real email statistics from backend
        const statsData = await getEmailStatistics(30);
        
        if (statsData && statsData.daily_counts) {
          setData(statsData.daily_counts);
        } else {
          setData([]);
        }
        
      } catch (error) {
        console.error('Failed to fetch email stats:', error);
        setError(error.message);
        setData([]); // Fallback to empty data
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) {
    return (
      <Card sx={{ 
        background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
        border: '1px solid #444',
        minHeight: 400
      }}>
        <CardContent sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <CircularProgress />
          <Typography sx={{ ml: 2 }}>Loading email statistics...</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ 
      background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
      border: '1px solid #444',
      minHeight: 400
    }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          📊 Email Activity (Last 30 Days)
        </Typography>

        {error && (
          <Typography color="error" sx={{ mb: 2 }}>
            Error loading data: {error}
          </Typography>
        )}

        <Box sx={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis 
                dataKey="date" 
                stroke="#B0B0B0" 
                tick={{ fontSize: 12 }}
                interval={Math.max(0, Math.floor(data.length / 10))} // Show fewer labels for readability
              />
              <YAxis stroke="#B0B0B0" />
              <Tooltip
                contentStyle={{ 
                  backgroundColor: '#2A2A2A', 
                  border: '1px solid #444',
                  borderRadius: 8
                }}
                labelStyle={{ color: '#E0E0E0' }}
                itemStyle={{ color: '#E0E0E0' }}
                formatter={(value, name) => {
                  const labels = {
                    drafts_created: 'Drafts Created',
                    emails_sent: 'Emails Sent',
                    total_activity: 'Total Activity'
                  };
                  return [value, labels[name] || name];
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="drafts_created"
                name="Drafts Created"
                stroke="#2196F3"
                strokeWidth={2}
                dot={{ fill: '#2196F3', r: 3 }}
                activeDot={{ r: 5, fill: '#42a5f5' }}
              />
              <Line
                type="monotone"
                dataKey="emails_sent"
                name="Emails Sent"
                stroke="#4CAF50"
                strokeWidth={2}
                dot={{ fill: '#4CAF50', r: 3 }}
                activeDot={{ r: 5, fill: '#66BB6A' }}
              />
              <Line
                type="monotone"
                dataKey="total_activity"
                name="Total Activity"
                stroke="#FF9800"
                strokeWidth={2}
                dot={{ fill: '#FF9800', r: 3 }}
                activeDot={{ r: 5, fill: '#FFA726' }}
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
        
        {data.length === 0 && !loading && (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
            No email activity data available yet. Create some drafts to see statistics.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}