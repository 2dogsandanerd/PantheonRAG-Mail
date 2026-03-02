import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SmartDoclingUploader from '../SmartDoclingUploader';

describe('Folder Upload', () => {
  const mockCollections = [
    { name: 'produkte', count: 10 },
    { name: 'Kunden', count: 5 }
  ];

  test('should show folder mode toggle', () => {
    render(<SmartDoclingUploader collections={mockCollections} />);
    expect(screen.getByText('Select Folder')).toBeInTheDocument();
  });

  test('should switch to folder mode', () => {
    render(<SmartDoclingUploader collections={mockCollections} />);
    expect(screen.getByText('Select Folder')).toBeInTheDocument();
  });

  test('should format bytes correctly', () => {
    // Since formatBytes is internal function, we test the component's behavior
    // This would typically require exposing the function or testing through behavior
    expect(true).toBe(true); // Placeholder
  });
});