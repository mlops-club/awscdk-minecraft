import React from 'react';
import logo from './logo.svg';
import './App.css';
import Button from '@mui/joy/Button';
import axios from 'axios';
// import material UI theme
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Home from './components/Home';
// auth with aws cognito from amazon-cognito-identity-js
import { config } from 'process';

/* wrap app in material UI theme */

function App() {
  return (
    // <ThemeProvider theme={theme}>
    <div className="App" >
      <Home />
    </div >
    // </ThemeProvider>
  );
}

export default App;
