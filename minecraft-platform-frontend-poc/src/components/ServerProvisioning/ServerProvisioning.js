import ServerProvisioningBase from './ProvisioningBase';

function ServerProvisioning(){
    let provisioning_content = {page_title:"Building Server",steps:["Step 1","Step 2","Step 3"],loading_video:"https://www.youtube.com/watch?v=hyXciy8UM4k"};
    return (
        <ServerProvisioningBase provisioning_content={provisioning_content} />
    )
}

export default ServerProvisioning;
