import React, {useContext} from 'react';
import './ServerUpdatePage.css';
import Checkbox from '@mui/material/Checkbox';
import LinearWithValueLabel from "../../UI/ProgressBar";
import CurrentPageContext from "../../store/current-page-context";

function ServerProvisioning(props){
    const currentPageCtx = useContext(CurrentPageContext);

    return (
        <div className="serverLoadUpdate">
            {
                props.steps.map((CompletedTaskText, i) => {
                if (i < currentPageCtx.completedSteps) {
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
        </div>
    )
}

export default ServerProvisioning;
