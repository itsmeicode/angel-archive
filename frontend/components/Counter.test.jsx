import { describe, it, expect, vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import { render, screen } from '../src/test/utils';
import { Counter } from './Counter';

describe('Counter', () => {
  it('renders current count', () => {
    render(<Counter count={3} />);
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('renders 0 when count is undefined', () => {
    render(<Counter />);
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('calls onChange with incremented value when + is clicked', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Counter count={2} onChange={onChange} />);
    await user.click(screen.getByText('+'));
    expect(onChange).toHaveBeenCalledWith(3);
  });

  it('calls onChange with decremented value when - is clicked', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Counter count={5} onChange={onChange} />);
    await user.click(screen.getByText('-'));
    expect(onChange).toHaveBeenCalledWith(4);
  });

  it('does not decrement below 0', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<Counter count={0} onChange={onChange} />);
    await user.click(screen.getByText('-'));
    expect(onChange).toHaveBeenCalledWith(0);
  });
});
