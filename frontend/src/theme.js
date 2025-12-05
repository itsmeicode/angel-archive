import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: "#f2a4a9", 
      light: "#f8c1c5", 
      dark: "#a86a6d", 
      contrastText: "#fff", 
    },
    secondary: {
      main: '#dc004e', 
      light:'#f48fb1',
    },
    otherColor: {
      main: "#999"
    }
  },
  typography: {
    fontFamily: 'Arial, sans-serif',
  },
});

export default theme;
