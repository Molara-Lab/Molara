"""Contains the tests for the rendering module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

from molara.rendering.rendering import MODES, Renderer

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.gui.main_window import MainWindow


class WorkaroundTestRenderer:
    """Contains the tests for the Renderer class."""

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the Renderer object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.openGLWidget = self.main_window.structure_widget
        self.renderer = Renderer(self.openGLWidget)
        self.openGLWidget.show()

    def run_tests(self) -> None:
        """Run all tests."""
        self._test_init()
        self._test_set_shaders()
        self._test_draw_cylinders()
        self._test_remove_cylinder()
        self._test_draw_cylinders_from_to()
        self._test_draw_spheres()
        self._test_remove_sphere()
        self._test_draw_billboards()
        self._test_remove_billboard()
        # self._test_shader_modes()

        self.openGLWidget.doneCurrent()

    def _test_init(self) -> None:
        """Test the __init__ method of the Renderer class."""
        assert isinstance(self.renderer, Renderer)

    def _test_set_shaders(self) -> None:
        """Test the set_shader method of the Renderer class."""
        shader_ints = [24, 27, 30, 33, 36, 39, 42]
        self.renderer.set_shaders()
        for i, shader in enumerate(self.renderer.shaders.values()):
            assert shader.program == shader_ints[i]
        number_of_shader_programs = 7
        assert len(self.renderer.shaders) == number_of_shader_programs

    def _test_draw_billboards(self) -> None:
        """Test the draw_billboards method of the Renderer class."""
        self.openGLWidget.makeCurrent()
        positions = np.array([[0.0, 0.0, 0.0], [1.0, -2.345, 0.12]], dtype=np.float32)
        scales = np.array([[1.0, 2.0, 1.0], [2.0, 1.0, 1.0]], dtype=np.float32)
        image = Image.open("tests/molara/rendering/images/MolaraLogo.png")
        self.renderer.draw_billboards("test5", positions, positions, scales, image)
        assert "test5" in self.renderer.textured_objects3d

    def _test_remove_billboard(self) -> None:
        """Test the remove_billboard method of the Renderer class."""
        self.openGLWidget.makeCurrent()

        self.renderer.remove_object("test5")
        assert "test5" not in self.renderer.textured_objects3d

    def _test_shader_modes(self) -> None:
        """Test the shader_modes method of the Renderer class."""
        self.openGLWidget.makeCurrent()
        positions = np.array([[0, 0, 0], [1, 1, 1], [4, 5, 6]], dtype=np.float32)
        directions = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
        # get a dimensionsarray going with [[radius, length, radius] * number_of_instances]
        dimensions = np.array([[0.5, 1.0, 0.5], [0.3, 2.0, 0.3], [0.2, 3.0, 0.2]], dtype=np.float32)

        colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
        subdivisions = 10

        self.renderer.draw_cylinders("test1", positions, directions, dimensions, colors, subdivisions)

        for mode in MODES:
            self.renderer.set_mode(mode)
            self.openGLWidget.update()

        self.renderer.remove_object("test1")

    def _test_draw_cylinders(self) -> None:
        """Test the draw_cylinders method of the Renderer class."""
        self.openGLWidget.makeCurrent()
        positions = np.array([[0, 0, 0], [1, 1, 1], [4, 5, 6]], dtype=np.float32)
        directions = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
        # get a dimensionsarray going with [[radius, length, radius] * number_of_instances]
        dimensions = np.array([[0.5, 1.0, 0.5], [0.3, 2.0, 0.3], [0.2, 3.0, 0.2]], dtype=np.float32)

        colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
        subdivisions = 10

        self.renderer.draw_cylinders("test1", positions, directions, dimensions, colors, subdivisions)
        assert "test1" in self.renderer.objects3d

    def _test_remove_cylinder(self) -> None:
        """Test the remove_cylinder method of the Renderer class."""
        self.openGLWidget.makeCurrent()

        self.renderer.remove_object("test1")
        assert "test1" not in self.renderer.objects3d

    def _test_draw_cylinders_from_to(self) -> None:
        """Test the draw_cylinders_from_to method of the Renderer class."""
        self.openGLWidget.makeCurrent()
        positions_from_to = np.array(
            [
                [[1.2, 3.4, 5.6], [9.8, 7.6, 5.4]],
                [[-3.3, -2.2, 1.1], [9.9, 8.8, -7.7]],
                [[0, 0, 0], [1, 1, 1]],
            ],
            dtype=np.float32,
        )
        radii = np.array([0.5, 0.3, 0.2], dtype=np.float32)
        colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
        subdivisions = 10

        self.renderer.draw_cylinders_from_to("test2", positions_from_to, radii, colors, subdivisions)
        assert "test2" in self.renderer.objects3d
        self.renderer.remove_object("test2")
        assert "test2" not in self.renderer.objects3d

    def _test_draw_spheres(self) -> None:
        """Test the draw_spheres method of the Renderer class."""
        self.openGLWidget.makeCurrent()
        positions = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)
        radii = np.array([0.5, 0.3], dtype=np.float32)
        colors = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float32)
        subdivisions = 10

        self.renderer.draw_spheres("test3", positions, radii, colors, subdivisions)
        assert "test3" in self.renderer.objects3d

        self.renderer.remove_object("test3")
        assert "test3" not in self.renderer.objects3d

        self.renderer.draw_spheres("test4", positions, radii, colors, subdivisions, wire_frame=True)
        assert "test4" in self.renderer.objects3d

    def _test_remove_sphere(self) -> None:
        """Test the remove_sphere method of the Renderer class."""
        self.openGLWidget.makeCurrent()

        self.renderer.remove_object("test4")
        assert "test4" not in self.renderer.objects3d
