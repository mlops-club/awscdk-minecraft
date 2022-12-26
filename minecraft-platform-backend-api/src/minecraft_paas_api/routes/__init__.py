"""All routes exposable by the Minecraft Platform REST API."""

from .aws_descriptor import ROUTER as AWS_DESCRIPTOR_ROUTER
from .server_endpoints import ROUTER as SERVER_ROUTER

__all__ = ["SERVER_ROUTER", "AWS_DESCRIPTOR_ROUTER"]
