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
from dataclasses import dataclass, field
from typing import List, Optional

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from minecraft_paas_api.aws_descriptor_routes import ROUTER as AWS_DESCRIPTOR_ROUTES
from minecraft_paas_api.deploy_routes import ROUTER as DEPLOY_ROUTES

ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "dev")
DEV_PORT: int = int(os.environ.get("PORT", "8000"))
STATE_MACHINE_ARN: str = os.environ.get("DEPLOY_SERVER_STEP_FUNCTIONS_STATE_MACHINE_ARN")
ROUTER = APIRouter()

@ROUTER.get("/status")
async def status(request: Request):
    """Return 200 to demonstrate that this REST API is reachable and can execute."""
    # return all of request scope as a dictionary
    return str(request.scope.get("aws", "AWS key not present"))


@dataclass
class Config:
    """API settings that are defined at startup time."""

    allowed_cors_origins: List[str] = field(default_factory=lambda: [f"http://localhost:{DEV_PORT}"])


@dataclass
class Services:
    """
    Container for all ``Service``s used by the running application.

    The ``Service`` abstraction should be used for any code that
    makes calls over the network to services external to this API.
    """

    ...


def create_app(
    config: Optional[Config] = None,
) -> FastAPI:

    if not config:
        config = Config()

    app = FastAPI(
        title="Minecraft API",
        description="A FastAPI app for the Minecraft API.",
        version="0.0.1",
        docs_url="/",
        openapi_url=f"/openapi.json",
        redoc_url=None,
        # openapi_prefix=f"/{ENVIRONMENT}",
    )
    app.state.config: Config = config
    app.state.services = Services()

    # configure startup behavior: initialize services on startup
    @app.on_event("startup")
    async def on_startup():
        print(dict(os.environ))
        print("We're starting up!")

    # add routes
    app.include_router(ROUTER, tags=["Admin"])
    app.include_router(AWS_DESCRIPTOR_ROUTES, tags=["AWS"])
    app.include_router(DEPLOY_ROUTES)

    # add authorized CORS origins (add these origins to response headers to
    # enable frontends at these origins to receive requests from this API)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def create_default_app() -> FastAPI:
    """
    Return an initialized FastAPI object using configuration from environment variables.

    This is a factory method that can be used by WSGI/ASGI runners like gunicorn and uvicorn.
    It is also useful for providing an application invokable by AWS Lambda.
    """
    config = Config()
    return create_app(config=config)


if __name__ == "__main__":
    import uvicorn

    config = Config()
    app = create_app(config=config)
    uvicorn.run(app, host="0.0.0.0", port=DEV_PORT)
    while True:
        pass
