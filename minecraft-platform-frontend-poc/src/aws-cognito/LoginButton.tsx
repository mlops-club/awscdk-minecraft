// react component for a login button using Amplify
import React from 'react';

import { Button } from '@mui/material';
import { signInWithCognito } from './auth-utils';

const LoginButton = () => {
    return (
        <Button variant="contained" onClick={() => signInWithCognito()}>Login</Button>
    )
}

export default LoginButton;
