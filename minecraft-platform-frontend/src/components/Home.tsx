import React, { useEffect } from 'react';
import { fetchConfig, MinecraftFrontendConfig } from '../config';
import { configureAmplifyCognitoAuthSingleton, logAuthData, getUserIdToken } from '../aws-cognito/auth-utils';
import { CognitoIdToken } from 'amazon-cognito-identity-js';
import LoginButton from '../aws-cognito/LoginButton';
import ServerOffline from './ServerOffline';
import { Button, Typography } from '@mui/material';
import { Configuration, DeploymentStatusResponse, MinecraftServerApi, MinecraftServerApiFactory } from '../api';
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import ServerDeprovisioning from './ServerDeprovisioning';


const readToken = async (): Promise<string> => {
    try {
        const idToken: CognitoIdToken = await getUserIdToken()
        const token: string = idToken.getJwtToken()
        return token
    } catch (error) {
        console.log("Error reading token: ", error)
        console.log("Trying again in 1 second.")

        // set timeout that resolves with the result of a recursive call to readToken
        return await new Promise(
            (resolve, reject) => {
                setTimeout(() => {
                    readToken().then((token) => {
                        resolve(token)
                    })
                }, 1_000)
            })
    }
}

const configureAxiosWithToken = (token: string): AxiosInstance => {
    // axios.defaults.headers.common['Authorization'] = token;
    // create an axios client
    const client = axios.create({
        headers: {
            'Authorization': token
        }
    })
    return client

}


const Home = () => {

    // const [config, setConfig] = React.useState<MinecraftFrontendConfig>();
    const [minecraftClient, setMinecraftClient] = React.useState<MinecraftServerApi | null>(null);
    // const [token, setToken] = React.useState<string | null>(null);

    // fetch the global app config (rather than using redux, we'll use the Home component);
    // then configure the aws-amplify.Auth singleton for managing the current logged-in user;
    // also, create a MinecraftServerApi client for making API calls to the Minecraft server

    const getMinecraftClientEffect = async (): Promise<void> => {
        const config_: MinecraftFrontendConfig = await fetchConfig()
        configureAmplifyCognitoAuthSingleton(config_)
        const token: string = await readToken()

        const minecraftClient_ = MinecraftServerApiFactory(undefined, config_.backend_api_url, configureAxiosWithToken(token)) as MinecraftServerApi
        console.log(config_, token, minecraftClient_)
        setMinecraftClient(minecraftClient_)
    }

    useEffect(() => {
        Promise.resolve(getMinecraftClientEffect())
    }, [])

    const getServerStatus = async () => {
        console.log("client", minecraftClient)
        if (minecraftClient) {
            const response: AxiosResponse<DeploymentStatusResponse> = await minecraftClient.getMinecraftServerDeploymentStatusMinecraftServerStatusGet();
            console.log("The server status is: ", response.data.status)
        }
    }

    // return a Material UI table with the config.json contents
    return (
        <>
            <Typography variant="h5">Minecraft Server Hosting by the MLOps Club</Typography>

            <ServerDeprovisioning />

            <Button variant="outlined" onClick={() => fetchConfig().then((config) => console.log(config))}>Load config.json</Button>
            <LoginButton />
            <Button variant="outlined" color="info" onClick={logAuthData}>Log auth data</Button>
            <Button variant="outlined" color="warning" onClick={getServerStatus}>Get server status</Button>

            <ServerOffline />
        </>
    );
};

export default Home;
