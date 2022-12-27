import React, {useState} from 'react';
import './ServerUpdatePage.css';
import Checkbox from '@mui/material/Checkbox';
import LinearWithValueLabel from "../../UI/ProgressBar";

function ServerProvisioning(){

    const [StepsCompleted, setStepsCompleted] = useState(2);

    const [CompletedList, setCompletedList] = useState([]);

    let steps_to_completion = [
        "Step 1",
        "Step 2",
        "Step 3"
    ]

    function renderCompletedSteps(completedSteps){
        let RenderedSteps = []
        for (let i = 0; i < steps_to_completion.length; i++) {
            if (i < completedSteps){
                RenderedSteps.push(
                    <div className="updateGroup">
                        <Checkbox checked />
                        <div>{steps_to_completion[i]}</div>
                    </div>);
            } else {
                RenderedSteps.push(
                    <div className="updateGroup updateGroupUnchecked">
                        <Checkbox unchecked />
                        <div>{steps_to_completion[i]}</div>
                    </div>);
            }
        }
        setCompletedList(RenderedSteps);
    }
    return (
        <div className="serverLoadUpdate">
            {
                steps_to_completion.map((CompletedTaskText, i) => {
                if (i < StepsCompleted) {
                  return (<div className="updateGroup">
                        <Checkbox checked />
                        <div>{CompletedTaskText}</div>
                    </div>);
                }
                return (<div className="updateGroup updateGroupUnchecked">
                        <Checkbox unchecked />
                        <div>{CompletedTaskText}</div>
                    </div>);
              })
            }
            <LinearWithValueLabel/>
        </div>
    )
}

export default ServerProvisioning;

