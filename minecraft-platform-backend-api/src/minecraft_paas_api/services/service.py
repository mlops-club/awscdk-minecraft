"""This is a docstring."""
from __future__ import annotations

from typing import Protocol

from minecraft_paas_api.settings import Settings


class IService(Protocol):
    """An interface for interacting with external services over the  network."""

    def init(self) -> None:
        """
        Initialize the service.

        This method is called during the "on_startup" lifecycle event of the FastAPI app.
        """

    @classmethod
    def from_settings(cls, settings: Settings) -> IService:
        """
        Create a ``Service`` from the API ``Settings``.

        As a rule, try only to take minimum number of attributes from the ``settings`` object
        needed for this class to operate, then pass them to the __init__ method of the child class.

        Thusly, this factory method follows the "principle of least knowledge" and won't
        break if unnecessary attributes disappear or change.
        """
