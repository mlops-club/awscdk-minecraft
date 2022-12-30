// react component
import React from 'react';
import { MinecraftServerApi } from '../api';

import Box from '@mui/material/Box';
import LinearProgress from '@mui/material/LinearProgress';
import { Typography } from '@mui/material';

const LinearIndeterminate = () => {
    return (
        <Box sx={{ width: '100%' }}>
            <LinearProgress />
        </Box>
    );
}

const ServerProvisioning = (props: {
    minecraftClient: MinecraftServerApi;
}) => {

    return (
        // linear progress bar from material UI that never ends
        <div>
            <Typography>Starting Minecraft server...</Typography>
            <Typography>(This may take 5-10 minutes)</Typography>
            <LinearIndeterminate />
        </div>

    );
};

export default ServerProvisioning;
