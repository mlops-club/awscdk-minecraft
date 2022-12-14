import React, { useDebugValue } from 'react';
import { useEffect } from 'react';
import { fetchConfig, MinecraftFrontendConfig } from '../config';
import { configureAmplifyCognitoAuthSingleton, logAuthData } from '../aws-cognito/auth-utils';
import LoginButton from '../aws-cognito/LoginButton';
import Button from '@mui/joy/Button';


const Home = () => {

    const [config, setConfig] = React.useState<MinecraftFrontendConfig>();

    // fetch the global app config (rather than using redux, we'll use the Home component);
    // then configure the aws-amplify.Auth singleton for managing the current logged-in user
    useEffect(() => {
        fetchConfig().then((config: MinecraftFrontendConfig) => {
            setConfig(config);
            configureAmplifyCognitoAuthSingleton(config)
        }
        )
    }, []);

    // return a Material UI table with the config.json contents
    return (
        <>
            <h1>Home</h1>
            <Button variant="outlined" onClick={() => console.log(config)}>Load config.json</Button>
            <LoginButton />
            <Button variant="solid" color="info" onClick={logAuthData}>Log auth data</Button>
        </>
    );
};

export default Home;
