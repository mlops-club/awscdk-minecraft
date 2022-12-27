import React from 'react';
import { Alert, Button, SelectChangeEvent, Theme, Typography } from '@mui/material';
import { makeStyles } from '@mui/styles';
import { FormControl, Select, MenuItem, Checkbox } from '@mui/material';

const useStyles = makeStyles({
    formControl: {
        minWidth: 120,
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: "flex-start",
    }
});

const ServerOffline = () => {

    const classes = useStyles();

    const [hours, setHours] = React.useState(1);
    const [allowRisk, setAllowRisk] = React.useState(false);
    const [serverSize, setServerSize] = React.useState('small');

    const handleHoursChange = (event: SelectChangeEvent<number>) => {
        setHours(Number(event.target.value as string));
    };

    const handleAllowRiskChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setAllowRisk(event.target.checked);
    };

    const handleServerSizeChange = (event: SelectChangeEvent<string>) => {
        setServerSize(event.target.value as string);
    };

    return (
        <form className={classes.form}>

            <Typography>How many hours would you like to run the server for?</Typography>
            <FormControl>
                <Select defaultValue={1} value={hours} onChange={handleHoursChange} >
                    <MenuItem value={1}>1 Hour</MenuItem>
                    <MenuItem value={2}>2 Hours</MenuItem>
                    <MenuItem value={3}>3 Hours</MenuItem>
                </Select>
            </FormControl>

            <Typography>Are you willing to risk the server stopping suddenly? (up to 3 times cheaper)</Typography>
            <FormControl>
                <Checkbox
                    checked={allowRisk}
                    onChange={handleAllowRiskChange}
                />
            </FormControl>

            <Typography>What size server would you like?</Typography>
            <FormControl>
                <Select value={serverSize} onChange={handleServerSizeChange}>
                    <MenuItem value="small">Small $0.10/hour</MenuItem>
                    <MenuItem value="medium">Medium $0.20/hour</MenuItem>
                    <MenuItem value="large">Large $0.30/hour</MenuItem>
                </Select>
            </FormControl>

            <Alert severity="info">
                Your total cost will be (<strong>{hours}</strong> hours) * <strong>$0.20/hour</strong> for a <strong>Medium</strong> size = <strong>$0.40</strong>
            </Alert >


            <Button variant="contained" color={"success"}>Launch server</Button>
        </form >
    );
};

export default ServerOffline;
