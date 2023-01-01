"""Module defines endpoints for server information & acitons."""

from fastapi import APIRouter, HTTPException, Request
from minecraft_paas_api.schemas.server_destroy_post import DestroyServer
from minecraft_paas_api.schemas.server_ip import ServerIpSchema
from minecraft_paas_api.schemas.server_start_post import StartServerRequestPayload
from minecraft_paas_api.schemas.server_status import DeploymentStatus, DeploymentStatusResponse
from minecraft_paas_api.services.minecraft_server_provisioner import MinecraftServerProvisioner
from minecraft_paas_api.settings import Settings
from starlette.status import HTTP_404_NOT_FOUND
from loguru import logger

ROUTER = APIRouter()


def get_server_provisioner(request: Request) -> MinecraftServerProvisioner:
    """Get a server provisioner using the settings provided by the request."""
    app_state = request.app.state
    settings: Settings = app_state.settings
    server_provisioner = MinecraftServerProvisioner.from_settings(settings)
    return server_provisioner


@ROUTER.post("/minecraft-server", response_model=DeploymentStatusResponse)
async def start_minecraft_server(request: Request, payload: StartServerRequestPayload):
    """Start the server if it is not already running."""
    server_provisioner = get_server_provisioner(request)

    server_status: DeploymentStatus = server_provisioner.get_minecraft_server_status()

    if server_status == DeploymentStatus.SERVER_OFFLINE:
        logger.info("Server is offline, starting server...")
        server_provisioner.start_server()
        server_provisioner.stop_server_in_n_minutes(minutes_to_wait_until_stop_server=payload.play_time_minutes)
        return DeploymentStatusResponse(status=DeploymentStatus.SERVER_PROVISIONING)

    logger.info(f"Server is in state {server_status}. Not starting server.")
    return DeploymentStatusResponse(status=server_status)


@ROUTER.delete("/minecraft-server", response_model=DeploymentStatusResponse)
async def stop_minecraft_server(request: Request, payload: DestroyServer):
    """
    Stop the server if it is running.

    If the `wait_n_minutes_before_destroy` parameter is set, the server will be stopped after the specified amount of time.
    Otherwise the server will be stopped immediately.
    """
    server_provisioner = get_server_provisioner(request)
    if payload.wait_n_minutes_before_destroy:
        server_provisioner.stop_server_in_n_minutes(payload.wait_n_minutes_before_destroy)
    else:
        server_provisioner.stop_server()
    return DeploymentStatusResponse(status=DeploymentStatus.SERVER_DEPROVISIONING)


@ROUTER.get("/minecraft-server/ip-address", response_model=ServerIpSchema)
async def get_minecraft_server_ip_address(request: Request):
    """Get the minecraft server ip address."""
    server_provisioner = get_server_provisioner(request)

    try:
        ip_address = server_provisioner.get_server_ip_address()
        return ServerIpSchema(server_ip_address=ip_address)
    except TypeError as exception:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Error retrieving server ip address."
        ) from exception


@ROUTER.get("/minecraft-server/status", response_model=DeploymentStatusResponse)
async def get_minecraft_server_deployment_status(request: Request):
    """
    Describe the current state of the minecraft deployment.

    Deployment can be in any of 6 states:

    | State | Description |
    | --- | --- |
    | `SERVER_OFFLINE` | The `awscdk-minecraft-server` CloudFormation stack does not exist or is in a `DELETE_COMPLETE` state. |
    | `SERVER_PROVISIONING` | The latest execution of the `provision-minecraft-server` Step Function state machine is in a `RUNNING` state. |
    | `SERVER_PROVISIONING_FAILED` | The latest execution of the `provision-minecraft-server` Step Function state machine is in a `FAILED` state. |
    | `SERVER_ONLINE` | The `awscdk-minecraft-server` CloudFormation stack exists and is in a `CREATE_COMPLETE` state. |
    | `SERVER_DEPROVISIONING` | The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine is in a `RUNNING` state AND the execution does not have a `wait_n_minutes_before_deprovisioning` input parameter. |
    | `SERVER_DEPROVISIONING_FAILED` | The latest execution of the `deprovision-minecraft-server` AWS Step Function state machine. |

    Depending on which `FAILED` state is the most recent, the status will be
    `SERVER_PROVISIONING_FAILED` or `SERVER_DEPROVISIONING_FAILED`.
    """
    server_provisioner = get_server_provisioner(request)
    response_dict = {"status": server_provisioner.get_minecraft_server_status()}
    return response_dict
