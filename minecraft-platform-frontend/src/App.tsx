import React from 'react';
import './App.css';
// @ts-ignore
import Home from './components/Home';
import { AuthContextProvider } from './store/auth-context';
import { CurrentPageContextProvider } from './store/current-page-context';

function App() {
  return (
    <div className="App" >
        <AuthContextProvider>
            <CurrentPageContextProvider>
                <Home/>
            </CurrentPageContextProvider>
        </AuthContextProvider>
    </div >
  );
}

export default App;
