import './ServerProvisioning.css';
import LinearProgress from '@mui/material/LinearProgress';
import ReactPlayer from 'react-player';
import React, {useState} from 'react';
import ServerUpdatePage from "./ServerUpdatePage";

function ServerProvisioning(props){
    const [progress, setProgress] = useState(0);

    let content_information = {
        provisioning_server:{
            page_title:"Building Server",
            steps:["Step 1","Step 2","Step 3"],
            loading_video:"https://www.youtube.com/watch?v=hyXciy8UM4k"
        },
        de_provisioning_server:{
            page_title:"Destroying Server",
            steps:["Step 1","Step 2","Step 3"],
            loading_video:"https://youtu.be/ZqJZsUSSxpo?t=96"
        }
    }

    let content_details = content_information[props.provisioning_type]

      React.useEffect(() => {
    const timer = setInterval(() => {
      setProgress((oldProgress) => {
        if (oldProgress === 100) {
          return 0;
        }
        const diff = Math.random() * 10;
        return Math.min(oldProgress + diff, 100);
      });
    }, 500);

    return () => {
      clearInterval(timer);
    };
  }, []);

    return (
        <div className="ServerProvisioningMain">
            <h1>{content_details.page_title}</h1>
            <ReactPlayer controls="0" width="1000px" height="500px" playing={true} muted={false} url={content_details.loading_video}/>
            <ServerUpdatePage steps={content_details.steps} />
        </div>
    )
}

export default ServerProvisioning;
