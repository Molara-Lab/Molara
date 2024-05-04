"""Test the GUI and rendering."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest
from gui.test_main_window import WorkaroundTestMainWindow
from gui.test_measurement_dialog import WorkaroundTestMeasurementDialog
from rendering.test_buffers import WorkaroundTestBuffers
from rendering.test_rendering import WorkaroundTestRenderer

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


@pytest.mark.skipif(sys.platform == "win32", reason="Test is not compatible with Windows")
def test_gui_and_rendering(qtbot: QtBot) -> None:
    """Tests the GUI and rendering.

    :param qtbot: provides methods to simulate user interaction
    """
    main_window_tests = WorkaroundTestMainWindow(qtbot)
    main_window_tests.run_tests()

    workaround_test_renderer = WorkaroundTestRenderer(qtbot, main_window_tests.window)
    workaround_test_renderer.run_tests()

    workaround_test_measurement_window = WorkaroundTestMeasurementDialog(qtbot, main_window_tests.window)
    workaround_test_measurement_window.run_tests()

    workaround_test_buffers = WorkaroundTestBuffers(qtbot, main_window_tests.window)
    workaround_test_buffers.run_tests()

    main_window_tests.tearDown()
