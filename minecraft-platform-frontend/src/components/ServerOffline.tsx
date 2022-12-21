// react component
// import React from 'react';

// import { FormControl, FormHelperText, Input, InputLabel } from '@mui/material';

// /**
//  * Material UI form with the following layout:
//  *
//  * - a dropdown menu to select how many hours to run the server for (1, 2, or 3)
//  * - a checkbox determining whether the user can risk the server stopping suddenly (it's cheaper if so)
//  * - a dropdown menu asking what the server size should be (small, medium, or large)
//  *
//  * These items are vertically aligned. Each item below the one before.
//  */
// const ServerOffline = () => {

//     return (
//         <div>

//             <h1>Server is offline</h1>

//             {/* dropdown menu to select 1, 2, or 3 hours */}


//             {/* checkbox to determine whether the user can risk the server stopping suddenly */}
//             {/* dropdown menu to select small, medium, or large server size */}

//             {/* <FormControl>
//                 <InputLabel htmlFor="my-input">Email address</InputLabel>
//                 <Input id="my-input" aria-describedby="my-helper-text" />
//                 <FormHelperText id="my-helper-text">We'll never share your email.</FormHelperText>
//             </FormControl> */}


//         </div>
//     )

// };

// export default ServerOffline;


import React from 'react';
import { SelectChangeEvent, Theme } from '@mui/material';
import { makeStyles } from '@mui/styles';

// import useStyles
import { FormControl, Select, MenuItem, Checkbox } from '@mui/material';


const useStyles = makeStyles((theme: Theme) => ({
    formControl: {
        margin: theme.spacing(1),
        minWidth: 120,
    },
}));

const ServerOffline = () => {


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
        <form>
            <FormControl>
                <Select defaultValue={1} value={hours} onChange={handleHoursChange} >
                    <MenuItem value={1}>1 Hour</MenuItem>
                    <MenuItem value={2}>2 Hours</MenuItem>
                    <MenuItem value={3}>3 Hours</MenuItem>
                </Select>
            </FormControl>
            <FormControl>
                <Checkbox
                    checked={allowRisk}
                    onChange={handleAllowRiskChange}
                />
                Allow Risk
            </FormControl>
            <FormControl>
                <Select value={serverSize} onChange={handleServerSizeChange}>
                    <MenuItem value="small">Small</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="large">Large</MenuItem>
                </Select>
            </FormControl>
        </form>
    );
};

export default ServerOffline;
