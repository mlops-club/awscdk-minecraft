from typing import Literal, TypedDict

from fastapi import APIRouter, Request
from minecraft_paas_api.aws.step_functions import trigger_state_machine
from minecraft_paas_api.settings import Settings

ROUTER = APIRouter()


class ProvisionMinecraftServerPayload(TypedDict):
    """Input format supported by the state machine that provisions/destroys the Minecraft server."""

    command: Literal["create", "destroy"]


@ROUTER.get("/deploy")
async def deploy(request: Request):
    """Start the server if it is not already running."""
    app_state = request.app.state
    settings: Settings = app_state.settings
    data = {"command": "deploy"}
    return trigger_state_machine(
        payload=data, state_machine_arn=settings.deploy_server_step_functions_state_machine_arn
    )


@ROUTER.get("/destroy")
async def destroy(request: Request):
    """Stop the server if it is running."""
    app_state = request.app.state
    settings: Settings = app_state.settings
    data = {"command": "destroy"}
    return trigger_state_machine(
        payload=data, state_machine_arn=settings.deploy_server_step_functions_state_machine_arn
    )
