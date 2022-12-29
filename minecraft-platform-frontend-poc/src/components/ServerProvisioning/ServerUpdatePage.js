import './ServerUpdatePage.css';
import Checkbox from '@mui/material/Checkbox';

function ServerProvisioning(props){
    return (
        <div className="serverLoadUpdate">
            {
                props.steps.map((CompletedTaskText, i) => {
                if (i < props.completedSteps) {
                  return (<div className="updateGroup">
                        <Checkbox checked />
                        <div>{CompletedTaskText}</div>
                    </div>);
                }
                return (<div className="updateGroup updateGroupUnchecked">
                        <Checkbox disabled />
                        <div>{CompletedTaskText}</div>
                    </div>);
              })
            }
        </div>
    )
}

export default ServerProvisioning;
