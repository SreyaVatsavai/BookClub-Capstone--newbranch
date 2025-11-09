// BookCard.test.jsx
// I wrote these tests to verify the BookCard component handles both
// complete book data (with cover image) and partial data (no cover)
// properly, since we might not always have cover images.

import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import BookCard from '../BookCard';

describe('BookCard', () => {
  // Test the happy path - a book with all data including cover image
  it('renders title, author and image when cover_image provided', () => {
    // Set up a complete book object with cover
    const book = {
      id: 1,
      title: 'My Book',
      author: 'Author',
      cover_image: 'http://example.com/cover.jpg',
    };
    // Render the card with a dummy onSelect handler
    render(<BookCard book={book} onSelect={() => {}} />);

    // Verify all text content is displayed
    expect(screen.getByText('My Book')).toBeInTheDocument();
    expect(screen.getByText(/by Author/i)).toBeInTheDocument();
    
    // Check that the cover image is rendered with correct src
    const img = screen.getByAltText('My Book');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', 'http://example.com/cover.jpg');
  });

  // Test fallback UI when cover image is missing
  it('shows fallback when no cover_image', () => {
    // Important: Use a different title to avoid confusion with 
    // the "No Cover" placeholder text in the UI
    const book = {
      id: 2,
      title: 'No Cover Book',
      author: 'Anon',
      cover_image: null,
    };
    render(<BookCard book={book} onSelect={() => {}} />);

    // Verify the fallback UI shows both placeholder and book info
    // Using selector to specifically target the placeholder text
    expect(screen.getByText('No Cover', { selector: '.MuiTypography-h6' })).toBeInTheDocument();
    expect(screen.getByText(/by Anon/i)).toBeInTheDocument();
  });

  // Test interaction - clicking the View Details button
  it('calls onSelect when button clicked', () => {
    // Set up a test book - cover_image isn't needed for this test
    const book = {
      id: 3,
      title: 'Click Me',
      author: 'Someone',
      cover_image: null,
    };
    // Create a spy function to verify it gets called
    const onSelect = vi.fn();
    render(<BookCard book={book} onSelect={onSelect} />);

    // Find and click the button using accessible role
    const btn = screen.getByRole('button', { name: /view details/i });
    fireEvent.click(btn);
    
    // Verify the callback was invoked
    expect(onSelect).toHaveBeenCalled();
  });
});
