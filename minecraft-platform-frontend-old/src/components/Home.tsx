import React, { useDebugValue } from 'react';
import { useEffect } from 'react';
import { fetchConfig, MinecraftFrontendConfig } from '../config';
import { configureAmplifyCognitoAuthSingleton, logAuthData } from '../aws-cognito/auth-utils';
import LoginButton from '../aws-cognito/LoginButton';
import ServerOffline from './ServerOffline';
import { Button, Typography } from '@mui/material';
import { Configuration, DeploymentStatusResponse, MinecraftServerApi, MinecraftServerApiFactory } from '../api';
import { AxiosResponse } from 'axios';


const Home = () => {

    const [config, setConfig] = React.useState<MinecraftFrontendConfig>();
    const [minecraftApi, setMinecraftApi] = React.useState<MinecraftServerApi | null>(null);

    // fetch the global app config (rather than using redux, we'll use the Main component);
    // then configure the aws-amplify.Auth singleton for managing the current logged-in user
    useEffect(() => {
        fetchConfig().then((config: MinecraftFrontendConfig) => {
            setConfig(config);
            configureAmplifyCognitoAuthSingleton(config)

            setMinecraftApi(new MinecraftServerApi(
                new Configuration({

                }),
                config.backend_api_url,
            ))
        }
        )
    }, []);

    const getServerStatus = async () => {
        if (minecraftApi) {
            const response: AxiosResponse<DeploymentStatusResponse> = await minecraftApi.getMinecraftServerDeploymentStatusMinecraftServerStatusGet();
            console.log("The server status is: ", response.data.status)
        }
    }

    // return a Material UI table with the config.json contents
    return (
        <>
            <Typography variant="h5">Minecraft Server Hosting by the MLOps Club</Typography>

            <Button variant="outlined" onClick={() => console.log(config)}>Load config.json</Button>
            <LoginButton />
            <Button variant="outlined" color="info" onClick={logAuthData}>Log auth data</Button>

            <Button variant="outlined" color="warning" onClick={getServerStatus}>Get server status</Button>

            <ServerOffline />
        </>
    );
};

export default Home;
