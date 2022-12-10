"""
A FastAPI app for the Minecraft API.

This app will have a /status endpoint which will return 200 if the server is alive.
It will also have a /deploy endpoint which will start the server if it is not already running.
It will have a /destroy endpoint which will stop the server if it is running.

The deploy and destroy endpoints will be responsible for creating a JSON message to post
to a AWS Step Function with a single variable: "command" which will be either "deploy" or "destroy".
The Step Function will then be responsible for starting and stopping the server.
"""


import os

import boto3
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse


# def get_state_machine_endpoint():
#     """Read the state machine arn from the environment."""
#     client = boto3.client("stepfunctions")
#     state_machine = client.describe_state_machine(stateMachineArn=os.environ["STATE_MACHINE_ARN"])
#     endpoint = state_machine["stateMachineArn"]
#     return endpoint


# ENDPOINT_URL = get_state_machine_endpoint()

app = FastAPI(
    title="Minecraft API",
    description="A FastAPI app for the Minecraft API.",
    version="0.1.0",
    docs_url="/",
    redoc_url=None,
)

# I DO NOT KNOW IF WE NEED THESE SECTIONS.
# allow all origins - MAY NOT BE WHAT WE WANT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add middleware that will handle https redirect and trusted hosts
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


@app.get("/status")
async def status():
    """Return 200 if the server is alive."""
    return JSONResponse(status_code=200)


# @app.get("/deploy")
# async def deploy():
#     """Start the server if it is not already running."""
#     data = {"command": "deploy"}
#     response = requests.post(ENDPOINT_URL, json=data)
#     if response.status_code != 200:
#         return JSONResponse(status_code=500)
#     return JSONResponse(status_code=200)


# @app.get("/destroy")
# async def destroy():
#     """Stop the server if it is running."""
#     data = {"command": "destroy"}
#     # send to step function
#     response = requests.post(ENDPOINT_URL, json=data)
#     if response.status_code != 200:
#         return JSONResponse(status_code=500)
#     return JSONResponse(status_code=200)
