import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Input } from './Input';

describe('Input Component Accessibility', () => {
  it('should associate the label with the input field', () => {
    render(<Input label="Email Address" />);
    
    // This will fail if the label is not correctly associated with an input
    const inputElement = screen.getByLabelText('Email Address');
    expect(inputElement).toBeDefined();
    expect(inputElement.tagName).toBe('INPUT');
  });

  it('should use provided id if given', () => {
    render(<Input label="Password" id="custom-password-id" />);
    
    const inputElement = screen.getByLabelText('Password');
    expect(inputElement.id).toBe('custom-password-id');
  });
});
