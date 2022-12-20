"""Settings instance for tests."""

import pytest
from minecraft_paas_api.settings import Settings


@pytest.fixture
def settings(state_machine_arn: str) -> Settings:
    """Fixture to create a settings object."""
    return Settings(
        minecraft_server_state_machine_arn=state_machine_arn,
        frontend_cors_url="https://awesome-minecraft-platform-domain.io",
        environment="development",
    )
