import React from 'react';
import './App.css';
// @ts-ignore
import Main from './components/Main';
import { AuthContextProvider } from './store/auth-context';
import { CurrentPageContextProvider } from './store/current-page-context';

function App() {
  return (
    <div className="App" >
        <AuthContextProvider>
            <CurrentPageContextProvider>
                <Main/>
            </CurrentPageContextProvider>
        </AuthContextProvider>
    </div >
  );
}

export default App;
