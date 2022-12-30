import React from "react";
import { Box, Button, FormControl, InputLabel, MenuItem, Select, SelectChangeEvent } from "@mui/material";
import { DeploymentStatus, MinecraftServerApi } from "../../api";
import { getServerStatus } from "../../api-wrapper/minecraft-client";
import { logAuthData } from "../../aws-cognito/auth-utils";
import LoginButton from "../../aws-cognito/LoginButton";
import { fetchConfig } from "../../config";

/**
 * Buttons and a dropdown that can be used to view the frontend state and switch between pages.
 * 
 * @param props 
 * @returns 
 */
const DebugTools = (props: {
    minecraftClient: MinecraftServerApi | null,
    serverStatus: DeploymentStatus,
    setServerStatus: (status: DeploymentStatus) => void,
}) => {
    const { minecraftClient, serverStatus, setServerStatus } = props;
    return (
        <>
            <Button variant="outlined" onClick={() => fetchConfig().then((config) => console.log(config))}>Load config.json</Button>
            <LoginButton />
            <Button variant="outlined" color="info" onClick={logAuthData}>Log auth data</Button>
            {minecraftClient && <Button variant="outlined" color="warning" onClick={() => getServerStatus(minecraftClient)}>Get server status</Button>}
            <DeploymentStatusDropdown status={serverStatus} setStatus={setServerStatus} />
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
        setStatus: (status: DeploymentStatus) => void
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

export default DebugTools;