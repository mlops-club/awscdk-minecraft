import React, {useState} from 'react';
import './ServerUpdatePage.css';
import Checkbox from '@mui/material/Checkbox';
import LinearWithValueLabel from "../../UI/ProgressBar";

function ServerProvisioning(props){

    const [StepsCompleted, setStepsCompleted] = useState(2);

    const [CompletedList, setCompletedList] = useState([]);


    return (
        <div className="serverLoadUpdate">
            {
                props.steps.map((CompletedTaskText, i) => {
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
            {/*<LinearWithValueLabel/>*/}
        </div>
    )
}

export default ServerProvisioning;

