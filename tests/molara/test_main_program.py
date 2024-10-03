"""Test the GUI and rendering."""

from __future__ import annotations

import sys

import pytest

from molara.__main__ import main


@pytest.mark.skipif(
    sys.platform == "win32", reason="Test is not compatible with Windows"
)
def test_main_program() -> None:
    """Tests the GUI and rendering.

    :param qtbot: provides methods to simulate user interaction
    """
    main(test=True)
