import React, { useDebugValue } from 'react';
import { useEffect } from 'react';
import { fetchConfig, MinecraftFrontendConfig } from '../config';
import { configureAmplifyCognitoAuthSingleton, logAuthData } from '../aws-cognito/auth-utils';
import LoginButton from '../aws-cognito/LoginButton';
import ServerOffline from './ServerOffline';
import { Button, Typography } from '@mui/material';


const Home = () => {

//     return (
//         <p>sdfsdf</p>
//     );
// }

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
            <Typography variant="h5">Minecraft Server Hosting by the MLOps Club</Typography>

            <Button variant="outlined" onClick={() => console.log(config)}>Load config.json</Button>
            <LoginButton />
            <Button variant="outlined" color="info" onClick={logAuthData}>Log auth data</Button>

            <ServerOffline />
        </>
    );
};

export default Home;
