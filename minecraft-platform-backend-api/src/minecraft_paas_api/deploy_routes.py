import json
from typing import Literal, TypedDict

import boto3
from fastapi import APIRouter, Request
from minecraft_paas_api.settings import Settings
from starlette.responses import JSONResponse

ROUTER = APIRouter()

try:
    from mypy_boto3_stepfunctions.client import SFNClient
    from mypy_boto3_stepfunctions.type_defs import StartExecutionOutputTypeDef
except ImportError:
    print("Warning: boto3-stubs[stepfunctions] not installed")


class ProvisionMinecraftServerPayload(TypedDict):
    """Input format supported by the state machine that provisions/destroys the Minecraft server."""

    command: Literal["create", "destroy"]


def trigger_state_machine(payload: ProvisionMinecraftServerPayload, state_machine_arn: str) -> JSONResponse:
    """Send command to state machine.

    Parameters
    ----------
    data : dict
        A dictionary with a single key "command" which will be either "deploy" or "destroy".

    Returns
    -------
    JSONResponse
        A JSON response with a status code of 200 if the state machine was triggered successfully.
        A JSON response with a status code of 500 if the state machine was not triggered successfully.
    """
    sfn_client: SFNClient = boto3.client("stepfunctions")
    start_exec: StartExecutionOutputTypeDef = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(payload),
    )
    if start_exec["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return JSONResponse(content="Failure!", status_code=500)

    # get status of state machine
    # status = sfn_client.describe_execution(executionArn=start_exec["executionArn"])
    # return JSONResponse(content="Success! {status}", status_code=200)
    return JSONResponse(content="Success!", status_code=200)


@ROUTER.get("/deploy")
async def deploy(request: Request):
    """Start the server if it is not already running."""
    app_state = request.app.state
    settings: Settings = app_state.settings
    data = {"command": "deploy"}
    return trigger_state_machine(
        payload=data, state_machine_arn=settings.provision_minecraft_server__state_machine__arn
    )


@ROUTER.get("/destroy")
async def destroy(request: Request):
    """Stop the server if it is running."""
    app_state = request.app.state
    settings: Settings = app_state.settings
    data = {"command": "destroy"}
    return trigger_state_machine(
        payload=data, state_machine_arn=settings.provision_minecraft_server__state_machine__arn
    )
