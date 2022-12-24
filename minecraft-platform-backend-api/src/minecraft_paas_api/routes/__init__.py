"""All routes exposable by the Minecraft Platform REST API."""

from .aws_descriptor import ROUTER as AWS_DESCRIPTOR_ROUTER
from .deploy import ROUTER as DEPLOY_ROUTER
from .server_status import ROUTER as SERVER_STATUS_ROUTER

__all__ = ["DEPLOY_ROUTER", "AWS_DESCRIPTOR_ROUTER", "SERVER_STATUS_ROUTER"]
