"""Test the GUI and rendering."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest
from gui.test_builder import WorkaroundTestBuilderDialog
from gui.test_cusotmizer_dialog import WorkaroundTestCustomizerDialog
from gui.test_export_image_dialog import WorkaroundTestExportImageDialog
from gui.test_main_window import WorkaroundTestMainWindow
from gui.test_measurement_dialog import WorkaroundTestMeasurementDialog
from gui.test_mos_dialog import WorkaroundTestMOsDialog
from gui.test_structure_widget import WorkaroundTestStructureWidget
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

    workaround_test_structure_widget = WorkaroundTestStructureWidget(qtbot, main_window_tests.window)
    workaround_test_structure_widget.run_tests()

    workaround_test_renderer = WorkaroundTestRenderer(qtbot, main_window_tests.window)
    workaround_test_renderer.run_tests()

    workaround_test_measurement_window = WorkaroundTestMeasurementDialog(qtbot, main_window_tests.window)
    workaround_test_measurement_window.run_tests()

    workaround_test_export_image_dialog = WorkaroundTestExportImageDialog(qtbot, main_window_tests.window)
    workaround_test_export_image_dialog.run_tests()

    workaround_test_buffers = WorkaroundTestBuffers(qtbot, main_window_tests.window)
    workaround_test_buffers.run_tests()

    workaround_test_mos_dialog = WorkaroundTestMOsDialog(
        qtbot,
        main_window_tests.window,
    )
    workaround_test_mos_dialog.run_tests()

    workaround_test_customizer_dialog = WorkaroundTestCustomizerDialog(
        qtbot,
        main_window_tests.window,
    )
    workaround_test_customizer_dialog.run_tests()

    main_window_tests.tearDown()


@pytest.mark.skipif(sys.platform == "win32", reason="Test is not compatible with Windows")
def test_builder(qtbot: QtBot) -> None:
    """Tests the BuilderDialog class.

    Note: This test is separated from the above methods to have a clear MainWindow without other molecules.

    :param qtbot: provides methods to simulate user interaction
    """
    main_window_tests = WorkaroundTestMainWindow(qtbot)

    workaround_test_builder_window = WorkaroundTestBuilderDialog(qtbot, main_window_tests.window)
    workaround_test_builder_window.run_tests()

    main_window_tests.tearDown()
