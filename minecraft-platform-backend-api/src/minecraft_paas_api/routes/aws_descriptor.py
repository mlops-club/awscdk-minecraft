from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from minecraft_paas_api.aws.step_functions import describe_state_machine, get_latest_statemachine_execution
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


@ROUTER.get("/latest-execution")
def get_statemachine(request: Request):
    """Get the latest execution of a state machine."""
    app_state = request.app.state
    settings: Settings = app_state.settings
    latest_execution: Optional[dict] = get_latest_statemachine_execution(
        state_machine_arn=settings.provision_minecraft_server__state_machine__arn
    )

    if latest_execution:
        return JSONResponse(
            content=replace_datetimes_in_dict_with_strings(latest_execution), status_code=HTTP_200_OK
        )

    return JSONResponse(content={}, status_code=HTTP_404_NOT_FOUND)


@ROUTER.get("/state-machine-status")
def get_state_machine_status(request: Request):
    """Get the stat machine status."""
    app_state = request.app.state
    settings: Settings = app_state.settings
    return describe_state_machine(state_machine_arn=settings.provision_minecraft_server__state_machine__arn)
