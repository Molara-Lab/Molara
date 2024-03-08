"""This module tests the GUI and rendering."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest
from Gui.test_main_window import WorkaroundTestMainWindow
from Rendering.test_rendering import WorkaroundTestRenderer

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


@pytest.mark.skipif(sys.platform == "win32", reason="Test is not compatible with Windows")
def test_gui_and_rendering(qtbot: QtBot) -> None:
    """Tests the GUI and rendering.

    :param qtbot: provides methods to simulate user interaction
    """
    main_window_tests = WorkaroundTestMainWindow(qtbot)
    _test_main_window(main_window_tests)
    _test_renderer(qtbot)
    main_window_tests.tearDown()


def _test_main_window(main_window_tests: WorkaroundTestMainWindow) -> None:
    """Creates a MainWindow object.

    :param qtbot: provides methods to simulate user interaction.
    """
    main_window_tests.test_init()
    main_window_tests.test_ui()
    main_window_tests.test_structure_widget()
    main_window_tests.test_show_builder_dialog()
    main_window_tests.test_show_crystal_dialog()


# @pytest.mark.skipif(sys.platform == "win32", reason="Test is not compatible with Windows")
def _test_renderer(qtbot: QtBot) -> None:
    """Tests the Renderer class.

    :param qtbot: provides methods to simulate user interaction
    """
    workaround_test_renderer = WorkaroundTestRenderer(qtbot)

    # The order of the tests is important, as the tests are not independent.
    # Changing the order of the tests may lead to failing tests.
    workaround_test_renderer.test_init()
    workaround_test_renderer.test_set_shader()
    workaround_test_renderer.test_draw_cylinders()
    workaround_test_renderer.test_remove_cylinder()
    workaround_test_renderer.test_draw_cylinders_from_to()
    workaround_test_renderer.test_draw_spheres()

    workaround_test_renderer.openGLWidget.doneCurrent()
