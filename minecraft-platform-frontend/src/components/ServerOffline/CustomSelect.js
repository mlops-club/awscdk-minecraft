import * as React from 'react';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';

export default function CustomSelect(props) {
  const [age, setAge] = React.useState('');

  const handleChange = (event) => {
    setAge(event.target.value);
  };

  return (
    <Box className="TextFormBox" sx={{ minWidth: 120 }}>
      <FormControl fullWidth>
        <InputLabel id="demo-simple-select-label">{props.label}</InputLabel>
        <Select
          labelId="demo-simple-select-label"
          id="demo-simple-select"
          value={age}
          label={props.label}
          onChange={handleChange}
        >
          {props.options.map(dropDownOptionValue => (<MenuItem
            key={dropDownOptionValue}
            value={dropDownOptionValue}
            >{dropDownOptionValue}</MenuItem>
          ))};
        </Select>
      </FormControl>
    </Box>
  );
}