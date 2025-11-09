// BookList.test.jsx
// These tests verify the BookList component's ability to:
// 1. Fetch and display books from the API
// 2. Handle empty results gracefully
// 3. Work with the React Router context it needs
//
// I'm using component and API mocking to isolate BookList's behavior
// from its dependencies.

import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';

// Mock BookCard to avoid router navigation issues and simplify testing
// I'm just verifying that BookList renders BookCard with the right data
vi.mock('../BookCard', () => ({
  default: ({ book }) =>
    React.createElement(
      'div',
      { 'data-testid': `book-${book.id}` },
      book.title
    ),
}));

// Mock the API module to control its responses in tests
// This lets us test both success and empty-result scenarios
vi.mock('../../../api/axiosConfig', () => ({
  default: {
    get: vi.fn(),  // We'll control this mock's behavior in each test
  },
}));

import BookList from '../BookList';
import api from '../../../api/axiosConfig';

describe('BookList', () => {
  beforeEach(() => {
    // Reset API mock before each test to ensure clean state
    api.get.mockReset();
  });

  // Test empty results handling - important for UX
  it('shows "No books found." when API returns empty array', async () => {
    // Mock API to return empty results
    api.get.mockResolvedValue({ data: [] });
    
    // Wrap in MemoryRouter since BookList uses routing features
    render(<BookList onBookSelect={() => {}} />, {
      wrapper: ({ children }) => <MemoryRouter>{children}</MemoryRouter>,
    });

    // Wait for async API call and verify empty state message
    await waitFor(() => {
      expect(screen.getByText(/No books found\./i)).toBeInTheDocument();
    });
  });

  // Test successful data fetching and rendering
  it('renders books when API returns results', async () => {
    // Mock API to return a sample book
    const books = [{ id: 1, title: 'A Book', author: 'Auth' }];
    api.get.mockResolvedValue({ data: books });

    // Render with router context
    render(<BookList onBookSelect={() => {}} />, {
      wrapper: ({ children }) => <MemoryRouter>{children}</MemoryRouter>,
    });

    // Wait for and verify both the BookCard render (via testid)
    // and the actual book title display
    await waitFor(() => {
      expect(screen.getByTestId('book-1')).toBeInTheDocument();
      expect(screen.getByText('A Book')).toBeInTheDocument();
    });
  });
});
