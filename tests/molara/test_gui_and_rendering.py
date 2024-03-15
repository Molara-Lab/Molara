"""This module tests the GUI and rendering."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest
from Gui.test_main_window import WorkaroundTestMainWindow
from Gui.test_measurement_dialog import WorkaroundTestMeasurementDialog
from Rendering.test_buffers import WorkaroundTestBuffers
from Rendering.test_rendering import WorkaroundTestRenderer

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.Gui.main_window import MainWindow


@pytest.mark.skipif(sys.platform == "win32", reason="Test is not compatible with Windows")
def test_gui_and_rendering(qtbot: QtBot) -> None:
    """Tests the GUI and rendering.

    :param qtbot: provides methods to simulate user interaction
    """
    main_window_tests = WorkaroundTestMainWindow(qtbot)
    _test_main_window(main_window_tests)
    _test_renderer(qtbot, main_window_tests.window)
    _test_measurement_window(qtbot, main_window_tests.window)
    _test_buffers(qtbot, main_window_tests.window)
    main_window_tests.tearDown()


def _test_main_window(main_window_tests: WorkaroundTestMainWindow) -> None:
    """Creates a MainWindow object.

    :param qtbot: provides methods to simulate user interaction
    """
    main_window_tests.test_init()
    main_window_tests.test_ui()
    main_window_tests.test_structure_widget()
    main_window_tests.test_show_builder_dialog()
    main_window_tests.test_show_crystal_dialog()
    main_window_tests.test_show_init_xyz()
    main_window_tests.test_load_molecules()
    main_window_tests.test_show_measurement_dialog()
    main_window_tests.test_show_trajectory_dialog()


# @pytest.mark.skipif(sys.platform == "win32", reason="Test is not compatible with Windows")
def _test_renderer(qtbot: QtBot, main_window: MainWindow) -> None:
    """Tests the Renderer class.

    :param qtbot: provides methods to simulate user interaction
    """
    workaround_test_renderer = WorkaroundTestRenderer(qtbot, main_window)

    # The order of the tests is important, as the tests are not independent.
    # Changing the order of the tests may lead to failing tests.
    workaround_test_renderer.test_init()
    workaround_test_renderer.test_set_shader()
    workaround_test_renderer.test_draw_cylinders()
    workaround_test_renderer.test_remove_cylinder()
    workaround_test_renderer.test_draw_cylinders_from_to()
    workaround_test_renderer.test_draw_spheres()
    workaround_test_renderer.test_remove_sphere()

    workaround_test_renderer.openGLWidget.doneCurrent()


def _test_measurement_window(qtbot: QtBot, main_window: MainWindow) -> None:
    """Tests the MeasurementDialog class.

    :param qtbot: provides methods to simulate user interaction
    """
    workaround_test_measurement_window = WorkaroundTestMeasurementDialog(qtbot, main_window)

    # The order of the tests is important, as the tests are not independent.
    # Changing the order of the tests may lead to failing tests.
    workaround_test_measurement_window.test_init()
    workaround_test_measurement_window.test_display_distances_angles()


def _test_buffers(qtbot: QtBot, main_window: MainWindow) -> None:
    """Tests the buffers module.

    :param qtbot: provides methods to simulate user interaction
    """
    workaround_test_buffers = WorkaroundTestBuffers(qtbot, main_window)

    # The order of the tests is important, as the tests are not independent.
    # Changing the order of the tests may lead to failing tests.
    workaround_test_buffers.test_setup_vao()
