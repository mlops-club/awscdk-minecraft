// 1) Import the React and ReactDOM libraries
import React from 'react';
import ReactDom from 'react-dom/client';

const el = document.getElementById('root');

const root = ReactDom.createRoot(el);

function App(){
    return <h1>Hi there</h1>;
}

root.render( < App /> );
