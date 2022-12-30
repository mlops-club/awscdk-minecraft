import React from 'react';
import { Alert, Button, SelectChangeEvent, Typography, Theme, CircularProgress } from '@mui/material';
import { makeStyles, createStyles } from '@mui/styles';
import { FormControl, Select, MenuItem, Checkbox, Card, CardContent, Grid } from '@mui/material';
import { DeploymentStatus, DeploymentStatusResponse, DestroyServer, MinecraftServerApi, ServerIpSchema, StartServerRequestPayload } from '../api';
import { AxiosRequestConfig, AxiosResponse } from 'axios';
import { Box } from '@mui/system';
import { green, red } from '@mui/material/colors';



const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        formControl: {
            minWidth: 200,
            height: '100%',
            textAlign: 'left',
            // put vertical space between the contents
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
        },
        card: {
            marginLeft: 'auto',
            marginRight: 'auto',
            margin: '0 auto',
            width: 'calc(100% - 20%)',
            padding: "30px",
            // center the contents horizontally
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
        },
        grid: {
            height: '100%',
        },
        cell: {},
        select: {
            width: '250px'
        }
    })
);

const getMinecraftServerIpAddress = async (args: {
    minecraftClient: MinecraftServerApi,
}): Promise<string> => {
    const { minecraftClient } = args;
    const response: AxiosResponse<ServerIpSchema> = await minecraftClient.getMinecraftServerIpAddressMinecraftServerIpAddressGet();
    return response.data.server_ip_address;
}

const stopMinecraftServer = async (args: {
    minecraftClient: MinecraftServerApi,
}): Promise<DeploymentStatus> => {
    const { minecraftClient } = args;
    const payload: DestroyServer = {}
    const response: AxiosResponse<DeploymentStatusResponse> = await minecraftClient.stopMinecraftServerMinecraftServerDelete(payload);
    return response.data.status;
}

/**
 * The component exposed by this file.
 *
 * Responsible for rendering any components that are relevant to the server being online.
 * This includes exposing an Alert that contains the Minecraft Server IP address
 *
 * @param props
 * @returns
 */
const ServerOnline = (props: {
    minecraftClient: MinecraftServerApi,
    setServerStatus: (status: DeploymentStatus) => void,
}) => {
    const classes = useStyles();

    const [ipAddress, setIpAddress] = React.useState("");
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        getMinecraftServerIpAddress({ minecraftClient: props.minecraftClient })
            .then((server_ip_address: string) => {
                setIpAddress(server_ip_address);
                setLoading(false);
                return [props.minecraftClient]
            });
    }, [props.minecraftClient]);

    const [stopLoading, setStopLoading] = React.useState(false);

    const handleStopServerClick = () => {
        if (!stopLoading) {
            setStopLoading(true);
            stopMinecraftServer({ minecraftClient: props.minecraftClient })
                .then((status: DeploymentStatus) => {
                    props.setServerStatus(status);
                    setStopLoading(false);
                });
        }
    };

    return (
        <Card className={classes.card}>

            <CardContent>
                {loading ? <CircularProgress size={24} sx={{
                    color: green[500],
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    marginTop: '-12px',
                    marginLeft: '-12px',
                }} /> :
                    <>
                        <Alert severity="success">
                            <Typography>
                                The Minecraft Server is online. IP Address: <strong>{ipAddress}</strong>
                            </Typography>
                        </Alert>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Button
                                variant="contained"
                                sx={{
                                    bgcolor: red[500],
                                    '&:hover': {
                                        bgcolor: red[700],
                                    },
                                }}
                                disabled={stopLoading}
                                onClick={handleStopServerClick}
                            >
                                Stop Server
                            </Button>
                            {stopLoading && (
                                <CircularProgress
                                    size={24}
                                    sx={{
                                        color: green[500],
                                        position: 'absolute',
                                        top: '50%',
                                        left: '50%',
                                        marginTop: '-12px',
                                        marginLeft: '-12px',
                                    }}
                                />
                            )}
                        </Box>
                    </>
                }
            </CardContent>
        </Card>
    );
};

export default ServerOnline;
