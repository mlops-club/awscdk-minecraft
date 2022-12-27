import './ServerProvisioning.css';
import LinearProgress from '@mui/material/LinearProgress';
import ReactPlayer from 'react-player';
import React, {useState} from 'react';
import ServerUpdatePage from "./ServerUpdatePage";

function ServerProvisioning(){
    const [progress, setProgress] = useState(0);

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
            <h1>Building Provisioning</h1>
            <ReactPlayer controls="0" width="1000px" height="500px" playing={true} muted={true} url="https://www.youtube.com/watch?v=hyXciy8UM4k"/>
            <ServerUpdatePage/>
        </div>
    )
}
export default ServerProvisioning;
