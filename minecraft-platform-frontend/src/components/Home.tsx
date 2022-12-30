import React, { useEffect } from 'react';
import { fetchConfig, MinecraftFrontendConfig } from '../config';
import { configureAmplifyCognitoAuthSingleton, logAuthData, readTokenFromLocalStorage } from '../aws-cognito/auth-utils';
import LoginButton from '../aws-cognito/LoginButton';
import { Box, Button, FormControl, InputLabel, MenuItem, Select, SelectChangeEvent, Typography } from '@mui/material';
import { DeploymentStatus, DeploymentStatusResponse, MinecraftServerApi, MinecraftServerApiFactory } from '../api';
import { AxiosResponse } from 'axios';
import { configureAxiosWithToken } from '../aws-cognito/authed-axios-client';
import ServerOffline from './ServerOffline';
import ServerProvisioning from './ServerProvisioning';
import ServerDeprovisioning from './ServerDeprovisioning';
import ServerOnline from './ServerOnline';



const Home = () => {

    // const [config, setConfig] = React.useState<MinecraftFrontendConfig>();
    const [minecraftClient, setMinecraftClient] = React.useState<MinecraftServerApi | null>(null);
    const [serverStatus, setServerStatus] = React.useState<DeploymentStatus>(DeploymentStatus.Offline);
    // const [token, setToken] = React.useState<string | null>(null);





    useEffect(() => {
        setupHomeState(setMinecraftClient, setServerStatus)
    }, [])


    // return a Material UI table with the config.json contents
    return (
        <>
            <Typography variant="h5">Minecraft Server Hosting by the MLOps Club</Typography>

            <DebugTools minecraftClient={minecraftClient} />
            <DeploymentStatusDropdown status={serverStatus} setStatus={setServerStatus} />
            {minecraftClient && renderState(serverStatus, minecraftClient, setServerStatus)}
        </>
    );
};

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

const DebugTools = (props: { minecraftClient: MinecraftServerApi | null }) => {
    const { minecraftClient } = props;
    return (
        <>
            <Button variant="outlined" onClick={() => fetchConfig().then((config) => console.log(config))}>Load config.json</Button>
            <LoginButton />
            <Button variant="outlined" color="info" onClick={logAuthData}>Log auth data</Button>
            {minecraftClient && <Button variant="outlined" color="warning" onClick={() => getServerStatus(minecraftClient)}>Get server status</Button>}
        </>
    )
}

/**
 *
 * @returns a MaterialUI-based picklist that allows the user to select the server status
 */
const DeploymentStatusDropdown = (
    props: {
        status: DeploymentStatus,
        setStatus: React.Dispatch<React.SetStateAction<DeploymentStatus>>
    }
) => {

    const { status, setStatus } = props;

    const handleChange = (event: SelectChangeEvent) => {
        setStatus(event.target.value as DeploymentStatus);
    };

    return (
        <Box sx={{ minWidth: 120 }}>
            <FormControl fullWidth>
                <InputLabel id="demo-simple-select-label">Status</InputLabel>
                <Select
                    labelId="demo-simple-select-label"
                    id="demo-simple-select"
                    value={status}
                    label="Status"
                    onChange={handleChange}
                >
                    <MenuItem value={DeploymentStatus.Offline}>Offline</MenuItem>
                    <MenuItem value={DeploymentStatus.Provisioning}>Provisioning</MenuItem>
                    <MenuItem value={DeploymentStatus.Online}>Online</MenuItem>
                    <MenuItem value={DeploymentStatus.Deprovisioning}>Deprovisioning</MenuItem>
                </Select>
            </FormControl>
        </Box>
    );
}


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

const getServerStatus = async (minecraftClient: MinecraftServerApi): Promise<DeploymentStatus | null> => {
    if (minecraftClient) {
        const response: AxiosResponse<DeploymentStatusResponse> = await minecraftClient.getMinecraftServerDeploymentStatusMinecraftServerStatusGet();
        return response.data.status
    }
    return null
}


const setupHomeState = async (
    setMinecraftClient: React.Dispatch<React.SetStateAction<MinecraftServerApi | null>>,
    setServerStatus: React.Dispatch<React.SetStateAction<DeploymentStatus>>
): Promise<void> => {
    const config: MinecraftFrontendConfig = await fetchConfig()
    const minecraftClient: MinecraftServerApi = await createMinecraftApiClient(config)
    setMinecraftClient(minecraftClient)
    continuallyUpdateServerStatus(minecraftClient, setServerStatus)
}

const createMinecraftApiClient = async (config: MinecraftFrontendConfig): Promise<MinecraftServerApi> => {
    // configure Amplify (abstraction over cognito) and try to read the cognito token from local storage
    configureAmplifyCognitoAuthSingleton(config)
    const token: string = await readTokenFromLocalStorage()
    // create the client, pointed at the correct backend URL and using the token for auth in all requests
    const minecraftClient = MinecraftServerApiFactory(undefined, config.backend_api_url, configureAxiosWithToken(token)) as MinecraftServerApi
    return minecraftClient
}

export default Home;
