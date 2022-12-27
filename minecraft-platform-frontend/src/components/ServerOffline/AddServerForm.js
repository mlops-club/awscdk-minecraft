import './AddServerForm.css'
import CustomSelect from "./CustomSelect";
import * as React from 'react';
import TextField from '@mui/material/TextField';
import Checkbox from '@mui/material/Checkbox';
import Card from '../../UI/Card'
import PinkCard from '../../UI/PinkCard'
import Button from '@mui/material/Button';

function AddServerForm(){
    let serverSizeOptions = ["Small", "Medium", "Large"]
    let potOptions = ["Default"]
    return (

        <PinkCard SectionHeader="Launch New Server">

            <div id="AddServerFormEntries">
                <div className="AddServerFormGroup">
                    <label>Number Of Minutes To Run Server</label>
                    <TextField
                        type="number"
                        InputProps={{
                            inputProps: {
                                max: 100, min: 1, step: 1
                            }
                        }}
                        label="Minutes"
                    />
                </div>

                <div className="AddServerFormGroup">
                    <label>Run On Server That May Crash But Is Cheaper</label>
                    <div className="Box">
                        <Checkbox />
                    </div>
                </div>

            </div>
                <div id="AddServerFormEntries">
                <div className="AddServerFormGroup">
                    <label>Select Server Size</label>
                    <CustomSelect options={serverSizeOptions} label="Server Size"/>
                </div>

                <div className="AddServerFormGroup">
                    <label>Pot To Pull Money From</label>
                    <CustomSelect options={potOptions} label="Select Pot"/>
                </div>

            </div>

            <div id="AddServerFormEntries">
                <div className="AddServerFormGroup">
                    <Button variant="contained">Start Server</Button>
                </div>
            </div>

        </PinkCard>
    )
}

export default AddServerForm;
