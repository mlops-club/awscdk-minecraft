import React, { useContext, useState } from 'react';
import './AddServerForm.css';
import CustomSelect from "../../UI/CustomSelect";
import TextField from '@mui/material/TextField';
import Checkbox from '@mui/material/Checkbox';
import PinkCard from '../../UI/PinkCard'
import Button from '@mui/material/Button';
import CurrentPageContext from '../../store/current-page-context';

function AddServerForm(){
    let serverSizeOptions = ["Small", "Medium", "Large"]
    let potOptions = ["Default"]

    const [numberMinutesToRunServer, setNumberMinutesToRunServer] = useState();
    const [useSpotInstance, setUseSpotInstance] = useState(false);
    const [serverSize, setserverSize] = useState();
    const [potToUse, setPotToUse] = useState();

    const ctx = useContext(CurrentPageContext);

    function submitHandler(event){
        event.preventDefault();
        if (
            numberMinutesToRunServer != null && numberMinutesToRunServer !== ''
            && serverSize != null && serverSize !== ''
            && potToUse != null && potToUse !== ''
        ){
            ctx.onLaunchServer({
                numberMinutesToRunServer:numberMinutesToRunServer,
                useSpotInstance:useSpotInstance,
                serverSize:serverSize,
                potToUse:potToUse
            });
        } else {
            alert("Error In Form")
        }
    }

    function updateMinutesToRunServer(event){
        setNumberMinutesToRunServer(event.target.value);
    }

    function updateUseSpotInstance(event){
        setUseSpotInstance(event.target.value);
    }

    function updateServerSizeSelection(event){
        setserverSize(event);
    }
    function updatePotSelection(event){
        setPotToUse(event);
    }

    return (
        <PinkCard SectionHeader="Launch New Server">
            <form onSubmit={submitHandler}>
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
                        value={numberMinutesToRunServer}
                        label="Minutes"
                        onChange={updateMinutesToRunServer}
                    />
                </div>

                <div className="AddServerFormGroup">
                    <label>Run On Server That May Crash But Is Cheaper</label>
                    <div className="Box">
                        <Checkbox value={useSpotInstance} onChange={updateMinutesToRunServer} />
                    </div>
                </div>

            </div>
                <div id="AddServerFormEntries">
                <div className="AddServerFormGroup">
                    <label>Select Server Size</label>
                    <CustomSelect options={serverSizeOptions} label="Server Size" onChange={updateServerSizeSelection} />
                </div>

                <div className="AddServerFormGroup">
                    <label>Pot To Pull Money From</label>
                    <CustomSelect options={potOptions} label="Select Pot" onChange={updatePotSelection} />
                </div>
            </div>

            <div id="AddServerFormEntries">
                <div className="AddServerFormGroup">
                    <Button variant="contained" type="submit">Start Server</Button>
                </div>
            </div>
            </form>
        </PinkCard>
    )
}

export default AddServerForm;
