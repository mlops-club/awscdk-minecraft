import React, { useEffect } from 'react';
import { Typography } from '@mui/material';
import { DeploymentStatus, MinecraftServerApi, MinecraftServerApiFactory } from '../../api';
import { fetchConfig, MinecraftFrontendConfig } from '../../config';
import { configureAxiosWithToken, getServerStatus } from '../../api-wrapper/minecraft-client';
import { configureAmplifyCognitoAuthSingleton, readTokenFromLocalStorage } from '../../aws-cognito/auth-utils';
import ServerOffline from '../ServerOffline';
import ServerProvisioning from '../ServerProvisioning';
import ServerOnline from '../ServerOnline';
import ServerDeprovisioning from '../ServerDeprovisioning';
import DebugTools from './DebugTools';
import LoginButton from '../../aws-cognito/LoginButton';



const Home = (props: {
    debug: boolean
}) => {

    // const [config, setConfig] = React.useState<MinecraftFrontendConfig>();
    const [minecraftClient, setMinecraftClient] = React.useState<MinecraftServerApi | null>(null);
    // const [token, setToken] = React.useState<string | null>(null);
    const [serverStatus, setServerStatus] = React.useState<DeploymentStatus>(DeploymentStatus.Offline);

    useEffect(() => {
        setupHomeState(setMinecraftClient, setServerStatus)
    }, [])


    // return a Material UI table with the config.json contents
    return (
        <>
            <Typography variant="h5">Minecraft Server Hosting by the MLOps Club</Typography>

            {props.debug ? <DebugTools minecraftClient={minecraftClient} serverStatus={serverStatus} setServerStatus={setServerStatus} /> : <LoginButton />}

            {minecraftClient && renderState(serverStatus, minecraftClient, setServerStatus)}
        </>
    );
};

const setupHomeState = async (
    setMinecraftClient: React.Dispatch<React.SetStateAction<MinecraftServerApi | null>>,
    setServerStatus: React.Dispatch<React.SetStateAction<DeploymentStatus>>
): Promise<void> => {
    const config: MinecraftFrontendConfig = await fetchConfig()
    const minecraftClient: MinecraftServerApi = await createMinecraftApiClient(config)
    setMinecraftClient(minecraftClient)
    continuallyUpdateServerStatus(minecraftClient, setServerStatus)
}

/**
 * Fetch the minecraft server status every N seconds and update Home component state if it changes.
 *
 * @param minecraftClient
 * @param setServerStatus
 */
const continuallyUpdateServerStatus = (minecraftClient: MinecraftServerApi, setServerStatus: React.Dispatch<React.SetStateAction<DeploymentStatus>>) => {
    setInterval(() => {
        getServerStatus(minecraftClient).then((status: DeploymentStatus | null) => {
            console.log("Server status: ", status)
            status && setServerStatus(status)
        })
    }, 10_000)
}


/**
 * Create a MinecraftServerApi client that makes authenticated requests to the backend API.
 */
const createMinecraftApiClient = async (config: MinecraftFrontendConfig): Promise<MinecraftServerApi> => {
    // configure Amplify (abstraction over cognito) and try to read the cognito token from local storage
    configureAmplifyCognitoAuthSingleton(config)
    const token: string = await readTokenFromLocalStorage()
    // create the client, pointed at the correct backend URL and using the token for auth in all requests
    const minecraftClient = MinecraftServerApiFactory(undefined, config.backend_api_url, configureAxiosWithToken(token)) as MinecraftServerApi
    return minecraftClient
}

/**
 * Return the correct component based on which state the minecraft server is in.
 */
const renderState = (
    deploymentStatus: DeploymentStatus,
    minecraftClient: MinecraftServerApi,
    setServerStatus: React.Dispatch<React.SetStateAction<DeploymentStatus>>,
) => {
    switch (deploymentStatus) {
        case DeploymentStatus.Offline:
            return <ServerOffline
                minecraftClient={minecraftClient}
                setServerStatus={setServerStatus}
            />
        case DeploymentStatus.Provisioning:
            return <ServerProvisioning minecraftClient={minecraftClient} />
        case DeploymentStatus.Online:
            return <ServerOnline minecraftClient={minecraftClient} setServerStatus={setServerStatus} />
        case DeploymentStatus.Deprovisioning:
            return <ServerDeprovisioning minecraftClient={minecraftClient} />
        case DeploymentStatus.DeprovisioningFailed:
            return ""
        case DeploymentStatus.ProvisioningFailed:
            return ""
    }
}

export default Home;
