from fastapi import APIRouter
from minecraft_paas_api.schemas.server_status import DeploymentStatusResponse

ROUTER = APIRouter()


@ROUTER.get("/deployment-status", response_model=DeploymentStatusResponse)
def describe_deployment_status():
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
    return {"status": "ok"}
