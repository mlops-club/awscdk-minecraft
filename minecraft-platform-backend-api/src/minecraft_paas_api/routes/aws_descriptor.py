from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from minecraft_paas_api.aws.cloudformation import get_cloud_form_output_value
from minecraft_paas_api.aws.step_functions import describe_state_machine, get_latest_statemachine_execution
from minecraft_paas_api.schemas.server_ip import ServerIpSchema
from minecraft_paas_api.settings import Settings
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

ROUTER = APIRouter()


def replace_datetimes_in_dict_with_strings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Replace all datetime objects in a dict with strings."""
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, dict):
            data[key] = replace_datetimes_in_dict_with_strings(value)
    return data


def load_settings_from_request_state(request: Request) -> Settings:
    """
    Load settings from request state.

    :param request: request object to load the settings from

    :return: settings object from the request state object
    """
    app_state = request.app.state
    return app_state.settings


@ROUTER.get("/latest-execution")
def get_statemachine(request: Request):
    """Get the latest execution of a state machine."""
    settings: Settings = load_settings_from_request_state(request)
    latest_execution: Optional[dict] = get_latest_statemachine_execution(
        state_machine_arn=settings.state_machine_arn
    )

    if latest_execution:
        return JSONResponse(
            content=replace_datetimes_in_dict_with_strings(latest_execution), status_code=HTTP_200_OK
        )

    return JSONResponse(content={}, status_code=HTTP_404_NOT_FOUND)


@ROUTER.get("/state-machine-status")
def get_state_machine_status(request: Request):
    """Get the state machine status."""
    settings: Settings = load_settings_from_request_state(request)
    return describe_state_machine(state_machine_arn=settings.state_machine_arn)


@ROUTER.get("/minecraft_server_ip_address", response_model=ServerIpSchema)
def get_minecraft_server_ip_address(request: Request):
    """Get the minecraft server ip address."""
    settings: Settings = load_settings_from_request_state(request)
    return get_cloud_form_output_value(
        settings.cloud_formation_stack_name, settings.cloud_formation_server_ip_output_key_name
    )
