
import React from 'react';
import { Alert, Button, SelectChangeEvent, Typography, Theme, CircularProgress } from '@mui/material';
import { makeStyles, createStyles } from '@mui/styles';
import { FormControl, Select, MenuItem, Checkbox, Card, CardContent, Grid } from '@mui/material';
import { DeploymentStatus, DeploymentStatusResponse, MinecraftServerApi, StartServerRequestPayload } from '../api';
import { AxiosRequestConfig, AxiosResponse } from 'axios';
import { Box } from '@mui/system';
import { green } from '@mui/material/colors';
import { startMinecraftServer } from '../api-wrapper/minecraft-client';



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


/**
 * The component exposed by this file.
 *
 * Responsible for rendering any components that are relevant to the server being offline.
 * This includes exposing a form that allows a user to launch a server.
 *
 * @param props
 * @returns
 */
const ServerOffline = (props: {
    minecraftClient: MinecraftServerApi,
    setServerStatus: (status: DeploymentStatus) => void,
}) => {
    const classes = useStyles();

    const [hours, setHours] = React.useState('');
    const [allowRisk, setAllowRisk] = React.useState('');
    const [serverSize, setServerSize] = React.useState('');

    const isDisabled = hours === '' || serverSize === '' || allowRisk === '';

    return (
        <Card className={classes.card}>

            <CardContent>
                <Typography variant="h5" style={{ marginBottom: "20px" }}>The server is <strong>offline</strong>. Sign in and submit this form to start it.</Typography>
                <Grid container direction="row" spacing={2} className={classes.grid}>
                    <ServerUptimeInput hours={hours} setHours={setHours} cellClass={classes.cell} formControlClass={classes.formControl} />
                    <ServerSizeInput serverSize={serverSize} setServerSize={setServerSize} cellClass={classes.cell} formControlClass={classes.formControl} />
                    <RiskInput allowRisk={allowRisk} setAllowRisk={setAllowRisk} cellClass={classes.cell} formControlClass={classes.formControl} />
                </Grid>

            </CardContent>

            <LaunchServerButton
                minecraftClient={props.minecraftClient}
                setServerStatus={props.setServerStatus}
                disabled={isDisabled}
                hours={Number(hours)}
                serverSize={serverSize}
                allowRisk={allowRisk.toLowerCase() === "yes"}
            />

        </Card>
    );
};

const ServerUptimeInput = (props: {
    hours: string,
    setHours: (hours: string) => void,
    cellClass: string,
    formControlClass: string,
}) => {
    const { hours, setHours, cellClass, formControlClass } = props;
    return (
        <Grid item xs={12} md={6} className={cellClass}>
            <FormControl className={formControlClass}>
                <Typography>How many hours would you like to run the server for?</Typography>
                <Select value={hours} onChange={(event) => setHours(event.target.value as string)}>
                    <MenuItem value={""}>Select</MenuItem>
                    <MenuItem value={1}>1 Hour</MenuItem>
                    <MenuItem value={2}>2 Hours</MenuItem>
                    <MenuItem value={3}>3 Hours</MenuItem>
                </Select>
            </FormControl>
        </Grid>
    );
};

const ServerSizeInput = (props: {
    serverSize: string,
    setServerSize: (serverSize: string) => void,
    cellClass: string,
    formControlClass: string,
}) => {
    const { serverSize, setServerSize, cellClass, formControlClass } = props;
    return (
        <Grid item xs={12} md={6} className={cellClass}>
            <FormControl className={formControlClass}>
                <Typography>What size server would you like?</Typography>
                <Select value={serverSize} onChange={(event) => setServerSize(event.target.value as string)}>
                    <MenuItem value={""}>Select</MenuItem>
                    <MenuItem value={"small"}>Small $0.10/hour</MenuItem>
                    <MenuItem value={"medium"}>Medium $0.20/hour</MenuItem>
                    <MenuItem value={"large"}>Large $0.30/hour</MenuItem>
                </Select>
            </FormControl>
        </Grid>
    );
};

const RiskInput = (props: {
    allowRisk: string,
    setAllowRisk: (allowRisk: string) => void,
    cellClass: string,
    formControlClass: string,
}) => {
    const { allowRisk, setAllowRisk, cellClass, formControlClass } = props;
    return (
        <Grid item xs={12} md={6} className={cellClass}>
            <FormControl className={formControlClass}>
                <Typography>Are you willing to risk the server stopping suddenly? (up to 3x cheaper)</Typography>
                <Select value={allowRisk} onChange={(event) => setAllowRisk(event.target.value as string)}>
                    <MenuItem value={""}>Select</MenuItem>
                    <MenuItem value={"yes"}>Yes</MenuItem>
                    <MenuItem value={"no"}>No</MenuItem>
                </Select>
            </FormControl>
        </Grid>
    );
};



const LaunchServerButton = (props: {
    minecraftClient: MinecraftServerApi,
    setServerStatus: (status: DeploymentStatus) => void,
    disabled: boolean,
    hours: number,
    serverSize: string,
    allowRisk: boolean,
}) => {
    // TODO: minecraftClient.getDeploymentStatus() is a function that returns a promise with the result of an API call {"server_status": DeploymentStatus.Online}
    // we should call it here and set the server status to the result. The Launch button should show a circular progress indicator while the API call is in progress.
    const { minecraftClient, setServerStatus, disabled, hours, serverSize, allowRisk } = props;
    // return <Button variant="contained" color={"success"} disabled={disabled} style={{ margin: '0 auto', display: 'block' }}> Launch server</Button>


    const [loading, setLoading] = React.useState(false);

    const handleClick = () => {
        if (!loading) {
            setLoading(true);

            startMinecraftServer({ minecraftClient, hours, serverSize, allowRisk })
                .then((serverStatus: DeploymentStatus) => {
                    setServerStatus(serverStatus);
                    setLoading(false);
                })
        }
    }

    const buttonSx = {
        ...(loading && {
            bgcolor: green[500],
            '&:hover': {
                bgcolor: green[700],
            },
        }),
    };

    return (
        <Box sx={{ position: 'relative' }}>
            <Button
                variant="contained"
                color="success"
                sx={buttonSx}
                disabled={disabled || loading}
                onClick={handleClick}
            >
                {loading ? <CircularProgress size={24} sx={{
                    color: green[500],
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    marginTop: '-12px',
                    marginLeft: '-12px',
                }} /> : "Launch Server"}
            </Button>
        </Box>
    );
};

export default ServerOffline;
