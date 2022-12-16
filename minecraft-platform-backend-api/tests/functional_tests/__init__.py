"""Functional tests."""

import sys
from pathlib import Path

tests_path = Path(sys.path[0])
sys.path.append(str(tests_path.parent))
