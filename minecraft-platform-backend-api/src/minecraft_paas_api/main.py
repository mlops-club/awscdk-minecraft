"""
A FastAPI app for the Minecraft API.

This app will have a /status endpoint which will return 200 if the server is alive.
It will also have a /deploy endpoint which will start the server if it is not already running.
It will have a /destroy endpoint which will stop the server if it is running.

The deploy and destroy endpoints will be responsible for creating a JSON message to post
to a AWS Step Function with a single variable: "command" which will be either "deploy" or "destroy".
The Step Function will then be responsible for starting and stopping the server.
"""


from dataclasses import dataclass
from typing import Literal, Optional, TypedDict

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from minecraft_paas_api.routes import SERVER_ROUTER
from minecraft_paas_api.settings import Settings

ROUTER = APIRouter()


class ProvisionMinecraftServerPayload(TypedDict):
    """Input format supported by the state machine that provisions/destroys the Minecraft server."""

    command: Literal["create", "destroy"]


@ROUTER.get("/healthcheck")
async def ping_this_api(request: Request):
    """Return 200 to demonstrate that this REST API is reachable and can execute."""
    # return all of request scope as a dictionary
    return str(request.scope)


@dataclass
class Services:
    """
    Container for all ``Service``s used by the running application.

    The ``Service`` abstraction should be used for any code that
    makes calls over the network to services external to this API.
    """

    ...


def create_app(
    settings: Optional[Settings] = None,
) -> FastAPI:

    if not settings:
        settings = Settings()

    app = FastAPI(
        title="🎁 Minecraft Platform-as-a-Service API 🎄",
        description="A FastAPI app for the Minecraft API.",
        version="0.0.1",
        docs_url="/",
        redoc_url=None,
    )

    # we can put arbitrary attributes onto app.state and access them from the routes
    app.state.settings = settings
    app.state.services = Services()

    # configure startup behavior: initialize services on startup
    @app.on_event("startup")
    async def on_startup():
        """Initialize each service."""
        # calls to services init methods should be made here
        print(settings.json())

    # add routes
    app.include_router(ROUTER, tags=["Admin"])
    app.include_router(SERVER_ROUTER, tags=["Minecraft Server"])
    # app.include_router(AWS_DESCRIPTOR_ROUTER, tags=["AWS"])

    # add authorized CORS origins (add these origins to response headers to
    # enable frontends at these origins to receive requests from this API)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_cors_origins,
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
    settings = Settings()
    return create_app(settings=settings)


if __name__ == "__main__":
    import uvicorn

    config = Settings()
    app = create_app(settings=config)
    uvicorn.run(app, host="0.0.0.0", port=config.dev_port)
