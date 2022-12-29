import './ServerProvisioning.css';
import ReactPlayer from 'react-player';
import ServerUpdatePage from "./ServerUpdatePage";

function ServerProvisioningBase(props){
    let content_details = props.provisioning_content;

    return (
        <div className="ServerProvisioningMain">
            <h1>{content_details.page_title}</h1>
            <ReactPlayer controls="0" width="1000px" height="500px" playing={true} muted={false} url={content_details.loading_video}/>
            <ServerUpdatePage steps={content_details.steps} completedSteps={props.completedSteps} />
        </div>
    )
}

export default ServerProvisioningBase;
