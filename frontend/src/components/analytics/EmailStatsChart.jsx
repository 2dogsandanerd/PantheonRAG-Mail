import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Box, CircularProgress, Alert } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { getDailyEmailCounts } from '../../api/client';

// Simple chart component without external dependencies
const SimpleLineChart = ({ data, width = '100%', height = 300 }) => {
  if (!data || data.length === 0) {
    return (
      <Box sx={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          No data available
        </Typography>
      </Box>
    );
  }

  const maxValue = Math.max(...data.map(d => d.count));
  const minValue = Math.min(...data.map(d => d.count));
  const range = maxValue - minValue || 1;

  const points = data.map((item, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - ((item.count - minValue) / range) * 80; // 80% of height for data
    return { x, y, ...item };
  });

  const pathData = points.map((point, index) =>
    `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`
  ).join(' ');

  return (
    <Box sx={{ width, height, position: 'relative' }}>
      <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map(y => (
          <line
            key={y}
            x1="0"
            y1={y}
            x2="100"
            y2={y}
            stroke="#444"
            strokeWidth="0.1"
            opacity="0.3"
          />
        ))}

        {/* Chart line */}
        <path
          d={pathData}
          fill="none"
          stroke="#2196F3"
          strokeWidth="0.5"
        />

        {/* Data points */}
        {points.map((point, index) => (
          <circle
            key={index}
            cx={point.x}
            cy={point.y}
            r="1"
            fill="#2196F3"
          />
        ))}
      </svg>

      {/* Y-axis labels */}
      <Box sx={{ position: 'absolute', left: 0, top: 0, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', fontSize: '10px', color: 'text.secondary' }}>
        <Typography variant="caption">{maxValue}</Typography>
        <Typography variant="caption">{Math.round((maxValue + minValue) / 2)}</Typography>
        <Typography variant="caption">{minValue}</Typography>
      </Box>

      {/* X-axis labels */}
      <Box sx={{ position: 'absolute', bottom: -20, left: 0, right: 0, display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'text.secondary' }}>
        {points.filter((_, index) => index % Math.ceil(points.length / 5) === 0).map((point, index) => (
          <Typography key={index} variant="caption">
            {point.date}
          </Typography>
        ))}
      </Box>
    </Box>
  );
};

export default function EmailStatsChart() {
  const { t } = useTranslation();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null);
        const apiData = await getDailyEmailCounts(30);

        const chartData = (apiData.daily_counts || []).map(item => ({
          date: new Date(item.date).toLocaleDateString('de-DE', {
            month: 'short',
            day: 'numeric'
          }),
          count: item.total_activity,
          fullDate: item.date
        }));

        setData(chartData);
      } catch (err) {
        setError(`Failed to load email statistics: ${err.message}`);
        console.error('Error loading email statistics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const totalEmails = data.reduce((sum, item) => sum + item.count, 0);
  const avgEmails = data.length > 0 ? Math.round(totalEmails / data.length) : 0;
  const maxEmails = Math.max(...data.map(d => d.count), 0);

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          📊 Emails per Day (Last 30 Days)
        </Typography>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">
            {error}
          </Alert>
        ) : (
          <>
            {/* Summary Stats */}
            <Box sx={{ display: 'flex', gap: 3, mb: 3, flexWrap: 'wrap' }}>
              <Box>
                <Typography variant="h4" color="primary.main" sx={{ fontWeight: 'bold' }}>
                  {totalEmails}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Emails
                </Typography>
              </Box>
              <Box>
                <Typography variant="h4" color="success.main" sx={{ fontWeight: 'bold' }}>
                  {avgEmails}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Daily Average
                </Typography>
              </Box>
              <Box>
                <Typography variant="h4" color="warning.main" sx={{ fontWeight: 'bold' }}>
                  {maxEmails}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Peak Day
                </Typography>
              </Box>
            </Box>

            {/* Chart */}
            <Box sx={{ height: 300, mb: 2 }}>
              <SimpleLineChart data={data} />
            </Box>

            {/* Data Table */}
            {data.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Recent Activity
                </Typography>
                <Box sx={{ maxHeight: 120, overflow: 'auto' }}>
                  {data.slice(-7).reverse().map((item, index) => (
                    <Box
                      key={index}
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        py: 0.5,
                        borderBottom: index < 6 ? '1px solid' : 'none',
                        borderColor: 'divider'
                      }}
                    >
                      <Typography variant="caption">
                        {item.fullDate}
                      </Typography>
                      <Typography variant="caption" sx={{ fontWeight: 'medium' }}>
                        {item.count} emails
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

