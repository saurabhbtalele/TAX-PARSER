"""Shared test fixtures."""

import sys
from pathlib import Path

import pytest

# Ensure src and config are importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
