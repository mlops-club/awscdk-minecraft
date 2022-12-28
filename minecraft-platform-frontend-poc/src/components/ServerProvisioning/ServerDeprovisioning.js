import ServerProvisioningBase from './ProvisioningBase';

function ServerProvisioning(){
    let provisioning_content = {
            page_title:"Destroying Server",
            steps:["Step 1","Step 2","Step 3"],
            loading_video:"https://youtu.be/ZqJZsUSSxpo?t=96"
        };
    return (
        <ServerProvisioningBase provisioning_content={provisioning_content} />
    )
}

export default ServerProvisioning;
