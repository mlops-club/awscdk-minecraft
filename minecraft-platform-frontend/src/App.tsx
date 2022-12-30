import React from 'react';
import logo from './logo.svg';
import './App.css';
import axios from 'axios';
// import material UI theme
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Home from './components/Home';
// auth with aws cognito from amazon-cognito-identity-js
import { config } from 'process';

/* wrap app in material UI theme */

const theme = createTheme()

function App() {
  return (
    <ThemeProvider theme={theme}>
      <div className="App" >
        <Home />
      </div >
    </ThemeProvider>
  );
}

export default App;
