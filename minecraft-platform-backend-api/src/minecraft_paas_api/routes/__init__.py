"""All routes exposable by the Minecraft Platform REST API."""

from .aws_descriptor import ROUTER as AWS_DESCRIPTOR_ROUTER
from .deploy import ROUTER as DEPLOY_ROUTER

__all__ = ["DEPLOY_ROUTER", "AWS_DESCRIPTOR_ROUTER"]
