import React, { useState } from 'react';
import {
    Box,
    IconButton,
    Rating,
    TextField,
    Button,
    Collapse,
    Typography,
    Alert,
    Paper
} from '@mui/material';
import {
    ThumbUp as ThumbUpIcon,
    ThumbDown as ThumbDownIcon,
    Send as SendIcon
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:33800';

/**
 * Feedback Widget Component
 * 
 * Allows users to provide feedback on query responses:
 * - Thumbs up/down
 * - Star rating
 * - Optional comment
 * 
 * Usage:
 * <FeedbackWidget queryId="abc123" />
 */
const FeedbackWidget = ({ queryId, onFeedbackSubmitted }) => {
    const [helpful, setHelpful] = useState(null);
    const [showDetails, setShowDetails] = useState(false);
    const [rating, setRating] = useState(0);
    const [comment, setComment] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState(null);

    const handleThumbClick = (isHelpful) => {
        setHelpful(isHelpful);
        setShowDetails(true);
    };

    const handleSubmit = async () => {
        if (!queryId) {
            setError('No query ID provided');
            return;
        }

        setSubmitting(true);
        setError(null);

        try {
            await axios.post(`${API_BASE}/api/v1/feedback/`, {
                query_id: queryId,
                helpful: helpful,
                rating: rating > 0 ? rating : null,
                comment: comment.trim() || null
            });

            setSubmitted(true);
            setShowDetails(false);

            if (onFeedbackSubmitted) {
                onFeedbackSubmitted({ helpful, rating, comment });
            }

            // Auto-hide after 3 seconds
            setTimeout(() => {
                setSubmitted(false);
            }, 3000);

        } catch (err) {
            console.error('Failed to submit feedback:', err);
            setError(err.response?.data?.detail || err.message);
        } finally {
            setSubmitting(false);
        }
    };

    if (submitted) {
        return (
            <Alert severity="success" sx={{ mt: 2 }}>
                ✅ Thank you for your feedback!
            </Alert>
        );
    }

    return (
        <Paper elevation={0} sx={{ p: 2, mt: 2, bgcolor: 'background.default' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="body2" color="text.secondary">
                    Was this helpful?
                </Typography>

                <IconButton
                    onClick={() => handleThumbClick(true)}
                    color={helpful === true ? 'success' : 'default'}
                    size="small"
                >
                    <ThumbUpIcon />
                </IconButton>

                <IconButton
                    onClick={() => handleThumbClick(false)}
                    color={helpful === false ? 'error' : 'default'}
                    size="small"
                >
                    <ThumbDownIcon />
                </IconButton>
            </Box>

            <Collapse in={showDetails}>
                <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                        Rate this response (optional):
                    </Typography>
                    <Rating
                        value={rating}
                        onChange={(event, newValue) => setRating(newValue)}
                        size="large"
                    />

                    <TextField
                        fullWidth
                        multiline
                        rows={2}
                        placeholder="Any additional comments? (optional)"
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        sx={{ mt: 2 }}
                        size="small"
                    />

                    {error && (
                        <Alert severity="error" sx={{ mt: 1 }}>
                            {error}
                        </Alert>
                    )}

                    <Button
                        variant="contained"
                        startIcon={<SendIcon />}
                        onClick={handleSubmit}
                        disabled={submitting || helpful === null}
                        sx={{ mt: 2 }}
                        size="small"
                    >
                        {submitting ? 'Submitting...' : 'Submit Feedback'}
                    </Button>
                </Box>
            </Collapse>
        </Paper>
    );
};

export default FeedbackWidget;
