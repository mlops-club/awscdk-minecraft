"""
Entrypoint for AWS Lambda.

This file exposes a ``handler`` function which is imported and executed
by AWS Lambda. The Mangum library converts the "event" object passed
by lambda into a form that is usable by FastAPI.

So Mangum is a FastAPI to Lambda converter.
"""

from fastapi import FastAPI
from mangum import Mangum
from minecraft_paas_api.main import create_default_app

APP: FastAPI = create_default_app()
handler = Mangum(APP)
