"""Test the routes related to deployment."""

from datetime import datetime

import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
from minecraft_paas_api.main import create_app
from minecraft_paas_api.settings import Settings
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND


def parse_execution_time(execution_time: str) -> datetime:
    """Parse an AWS-formatted datetime string to a datetime object."""
    return datetime.strptime(execution_time, "%Y-%m-%dT%H:%M:%S.%f%z")


@pytest.fixture()
def test_client(settings: Settings) -> TestClient:
    """Prepare a FastAPI test client which allows us to execute our endpoints with a ``requests``-like interface."""
    minecraft_pass_api: FastAPI = create_app(settings=settings)
    with TestClient(minecraft_pass_api) as client:
        yield client


def test_deploy(test_client: TestClient):
    """Test that the deploy endpoint can execute returns a 200 response."""
    response: Response = test_client.get("/deploy")
    assert response.status_code == HTTP_200_OK
    assert response.json() == "Success!"


def test_get_latest_execution(test_client: TestClient):
    """
    Test that the latest-execution endpoint can describe executions.

    Verify that the described execution is indeed the most recent one.
    """
    # no executions have happened yet
    response: Response = test_client.get("/latest-execution")
    assert response.status_code == HTTP_404_NOT_FOUND

    # trigger and describe the first execution
    test_client.get("/deploy")
    response: Response = test_client.get("/latest-execution")
    assert response.status_code == HTTP_200_OK
    execution_start_time_1: datetime = parse_execution_time(response.json()["startDate"])

    # trigger and describe the second execution
    test_client.get("/deploy")
    response: Response = test_client.get("/latest-execution")
    assert response.status_code == HTTP_200_OK
    execution_start_time_2 = parse_execution_time(response.json()["startDate"])

    # the second execution should have started after the first
    assert execution_start_time_1 < execution_start_time_2
