"""Reusable fixtures for the tests."""
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent
sys.path.append(str(THIS_DIR))


pytest_plugins = []
