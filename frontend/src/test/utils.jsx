import React from 'react';
import { render as rtlRender } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import theme from '../theme';

/**
 * Custom render that wraps components with ThemeProvider and optional Router.
 * Use this for components that need MUI theme or routing.
 */
function render(ui, { wrapper: CustomWrapper, ...options } = {}) {
  function Wrapper({ children }) {
    return (
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          {CustomWrapper ? <CustomWrapper>{children}</CustomWrapper> : children}
        </BrowserRouter>
      </ThemeProvider>
    );
  }
  return rtlRender(ui, { wrapper: Wrapper, ...options });
}

export * from '@testing-library/react';
export { render };
