import React, { useState, useEffect } from 'react';
import {
    Box,
    Stepper,
    Step,
    StepLabel,
    Button,
    Typography,
    Paper,
    CircularProgress
} from '@mui/material';
import axios from 'axios';

import SystemCheck from './wizard/SystemCheck';
import ModelSelector from './wizard/ModelSelector';
import DataIngestion from './wizard/DataIngestion';
import Completion from './wizard/Completion';

const COMPONENT_MAP = {
    'SystemCheck': SystemCheck,
    'ModelSelector': ModelSelector,
    'DataIngestion': DataIngestion,
    'Completion': Completion
};

const OnboardingWizard = () => {
    const [activeStep, setActiveStep] = useState(0);
    const [steps, setSteps] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSteps = async () => {
            try {
                // Use localhost URL directly for now as per project convention
                const response = await axios.get('http://localhost:33800/api/v1/onboarding/steps');
                setSteps(response.data);
            } catch (error) {
                console.error("Failed to fetch wizard steps", error);
            } finally {
                setLoading(false);
            }
        };
        fetchSteps();
    }, []);

    const handleNext = () => {
        setActiveStep((prevActiveStep) => prevActiveStep + 1);
    };

    const handleBack = () => {
        setActiveStep((prevActiveStep) => prevActiveStep - 1);
    };

    const handleReset = () => {
        setActiveStep(0);
    };

    if (loading) {
        return <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>;
    }

    if (steps.length === 0) {
        return <Typography color="error">No steps configuration found.</Typography>;
    }

    const ActiveComponent = COMPONENT_MAP[steps[activeStep]?.component] || (() => <Typography color="error">Component not found</Typography>);

    return (
        <Box sx={{ width: '100%', p: 3 }}>
            <Typography variant="h4" gutterBottom>Setup & Wartung</Typography>
            <Stepper activeStep={activeStep}>
                {steps.map((step, index) => (
                    <Step key={step.id}>
                        <StepLabel>{step.title}</StepLabel>
                    </Step>
                ))}
            </Stepper>

            <Paper sx={{ mt: 4, mb: 4, p: 3, minHeight: '300px' }}>
                {activeStep === steps.length ? (
                    <React.Fragment>
                        <Typography sx={{ mt: 2, mb: 1 }}>
                            All steps completed - you're finished
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
                            <Box sx={{ flex: '1 1 auto' }} />
                            <Button onClick={handleReset}>Reset</Button>
                        </Box>
                    </React.Fragment>
                ) : (
                    <React.Fragment>
                        <Typography variant="h6" gutterBottom>{steps[activeStep].description}</Typography>
                        <Box sx={{ my: 3 }}>
                            <ActiveComponent />
                        </Box>
                        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
                            <Button
                                color="inherit"
                                disabled={activeStep === 0}
                                onClick={handleBack}
                                sx={{ mr: 1 }}
                            >
                                Back
                            </Button>
                            <Box sx={{ flex: '1 1 auto' }} />
                            <Button onClick={handleNext}>
                                {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
                            </Button>
                        </Box>
                    </React.Fragment>
                )}
            </Paper>
        </Box>
    );
}

export default OnboardingWizard;
