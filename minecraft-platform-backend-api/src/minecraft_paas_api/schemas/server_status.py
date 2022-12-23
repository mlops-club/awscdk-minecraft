from enum import Enum

from pydantic import BaseModel, Field


class DeploymentStatus(str, Enum):
    """State that the deployment currently occupies."""

    SERVER_OFFLINE = "SERVER_OFFLINE"
    SERVER_PROVISIONING = "SERVER_PROVISIONING"
    SERVER_ONLINE = "SERVER_ONLINE"
    SERVER_DEPROVISIONING = "SERVER_DEPROVISIONING"
    SERVER_PROVISIONING_FAILED = "SERVER_PROVISIONING_FAILED"
    SERVER_DEPROVISIONING_FAILED = "SERVER_DEPROVISIONING_FAILED"


class DeploymentStatusResponse(BaseModel):
    """Response model for the `/deployment-status` endpoint."""

    status: DeploymentStatus = Field(description="Current state of the minecraft server.")

    class Config:
        use_values = True
