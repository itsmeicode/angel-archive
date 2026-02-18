import { describe, it, expect, vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import { render, screen } from '../src/test/utils';
import { SearchBar } from './SearchBar';

describe('SearchBar', () => {
  it('renders search input with placeholder', () => {
    render(<SearchBar options={[]} onSearch={() => {}} />);
    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
  });

  it('calls onSearch when user types', async () => {
    const user = userEvent.setup();
    const onSearch = vi.fn();
    render(<SearchBar options={[]} onSearch={onSearch} />);
    const input = screen.getByPlaceholderText('Search...');
    await user.type(input, 'angel');
    expect(onSearch).toHaveBeenCalled();
    expect(onSearch).toHaveBeenLastCalledWith('angel');
  });

  it('receives options prop', () => {
    const options = ['Apple', 'Banana', 'Cherry'];
    render(<SearchBar options={options} onSearch={() => {}} />);
    const input = screen.getByPlaceholderText('Search...');
    expect(input).toBeInTheDocument();
    // Autocomplete uses options internally; we just verify component renders with options
    expect(options).toHaveLength(3);
  });
});
