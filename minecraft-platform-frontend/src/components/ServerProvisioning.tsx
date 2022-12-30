// react component
import React from 'react';
import { MinecraftServerApi } from '../api';

import Box from '@mui/material/Box';
import LinearProgress from '@mui/material/LinearProgress';

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
            <p>Server is starting up...</p>
            <LinearIndeterminate />
        </div>

    );
};

export default ServerProvisioning;
