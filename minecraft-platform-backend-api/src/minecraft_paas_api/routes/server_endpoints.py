"""Module defines endpoints for server information & acitons."""

from fastapi import APIRouter, HTTPException, Request
from minecraft_paas_api.schemas.server_destroy_post import DestroyServer
from minecraft_paas_api.schemas.server_ip import ServerIpSchema
from minecraft_paas_api.schemas.server_status import DeploymentStatusResponse
from minecraft_paas_api.services.minecraft_server_provisioner import MinecraftServerProvisioner
from minecraft_paas_api.settings import Settings

ROUTER = APIRouter()


def get_server_provisioner(request: Request) -> MinecraftServerProvisioner:
    """Get a server provisioner using the settings provided by the request."""
    app_state = request.app.state
    settings: Settings = app_state.settings
    server_provisioner = MinecraftServerProvisioner.from_settings(settings)
    return server_provisioner


@ROUTER.get("/deploy")
async def deploy(request: Request):
    """Start the server if it is not already running."""
    server_provisioner = get_server_provisioner(request)
    return server_provisioner.start_server()


@ROUTER.post("/destroy-server-after-seconds")
async def destroy_after_seconds(request: Request, body: DestroyServer):
    """Stop the server if it is running after specified amount of time."""
    server_provisioner = get_server_provisioner(request)
    return server_provisioner.stop_server_in_n_minutes(body.time_to_wait_before_destroying_server)


@ROUTER.get("/destroy-server")
async def destroy(request: Request):
    """Stop the server if it is running."""
    server_provisioner = get_server_provisioner(request)
    return server_provisioner.stop_server()


@ROUTER.get("/minecraft-server-ip-address", response_model=ServerIpSchema)
async def get_minecraft_server_ip_address(request: Request):
    """Get the minecraft server ip address."""
    server_provisioner = get_server_provisioner(request)

    try:
        response_dict = {"server_ip_address": server_provisioner.get_server_ip_address()}
    except TypeError as exception:
        raise HTTPException(status_code=404, detail="Error retrieving server ip address.") from exception
    return response_dict


@ROUTER.get("/deployment-status", response_model=DeploymentStatusResponse)
async def describe_deployment_status(request: Request):
    """
    Describe the current state of the minecraft deployment.

    Deployment can be in any of 4 states:

    - Server is offline
    - Server is provisioning
    - Server is online
    - Server is deprovisioning

    Behind the scenes, these four states correspond with the following activiites:

    - `SERVER_OFFLINE`: The `awscdk-minecraft-server` CloudFormation stack does not exist or is in a `DELETE_COMPLETE` state.
    - `SERVER_PROVISIONING`: The latest execution of the `provision-minecraft-server` Step Function state machine
      is in a `RUNNING` state.
    - `SERVER_PROVISIONING_FAILED`: The latest execution of the `provision-minecraft-server` Step Function state machine
      is in a `FAILED` state.
    - `SERVER_ONLINE`: The `awscdk-minecraft-server` CloudFormation stack exists and is in a `CREATE_COMPLETE` state.
    - `SERVER_DEPROVISIONING`: The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine
      is in a `RUNNING` state AND the execution does not have a `wait_n_minutes_before_deprovisioning` input parameter.
    - `SERVER_DEPROVISIONING_FAILED`: The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine.

    Depending on which `FAILED` state is the most recent, the status will be
    `SERVER_PROVISIONING_FAILED` or `SERVER_DEPROVISIONING_FAILED`.


    """
    server_provisioner = get_server_provisioner(request)
    response_dict = {"status": server_provisioner.get_minecraft_server_status()}
    return response_dict
