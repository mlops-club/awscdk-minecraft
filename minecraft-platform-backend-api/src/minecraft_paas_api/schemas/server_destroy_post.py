"""Pydantic model for the destroy server post requests."""

from datetime import timedelta
from typing import Optional

from pydantic import PositiveInt
from pydantic.main import BaseModel


class DestroyServer(BaseModel):
    """Response model for the `/destroy-server-after-seconds` endpoint."""

    wait_n_minutes_before_destroy: Optional[PositiveInt] = None

    @property
    def destroy_delay_time(self) -> Optional[timedelta]:
        """Return the time to wait before destroying the server."""
        if self.wait_n_minutes_before_destroy:
            return timedelta(minutes=self.wait_n_minutes_before_destroy)
        return None
