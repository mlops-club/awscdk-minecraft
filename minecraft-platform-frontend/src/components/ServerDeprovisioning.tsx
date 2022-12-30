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

const ServerDeprovisioning = (props: {
    minecraftClient: MinecraftServerApi;
}) => {

    return (
        // linear progress bar from material UI that never ends
        <div>
            <p>Server is shutting down...</p>
            <LinearIndeterminate />
        </div>

    );
};

export default ServerDeprovisioning;
