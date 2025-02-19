"""Unittests for the shaders module."""

from __future__ import annotations

import sys
import unittest

import pytest
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow

from molara.rendering.shaders import Shader


@pytest.mark.skipif(sys.platform == "win32", reason="Test is not compatible with Windows")
class TestShaders(unittest.TestCase):
    """Contains the tests for the shaders module."""

    def test_compile_shaders(self) -> None:
        """Tests the compile_shaders function of the shaders module."""

        def add_shader(vertex_path: str, fragment_path: str) -> Shader:
            """Add a shader to the shader program.

            :param vertex_path: Path to the vertex shader.
            :param fragment_path: Path to the fragment shader.
            """
            shader = Shader()
            shader.compile_shaders(vertex_path, fragment_path)
            return shader

        QApplication.instance().shutdown() if QApplication.instance() else None  # type: ignore[union-attr]
        QApplication([])
        _format = QSurfaceFormat()
        _format.setVersion(3, 3)
        _format.setSamples(4)
        _format.setProfile(QSurfaceFormat.CoreProfile)  # type: ignore[attr-defined]
        QSurfaceFormat.setDefaultFormat(_format)
        main_window = QMainWindow()
        openglwidget = QOpenGLWidget(main_window)
        openglwidget.show()
        main_window.show()

        shader_code_path = ""

        shaders = []

        vertex_path = "vertex_main.glsl"
        fragment_path = "fragment_main_shaded.glsl"
        shaders.append(add_shader(shader_code_path + vertex_path, shader_code_path + fragment_path))

        vertex_path = "vertex_main.glsl"
        fragment_path = "fragment_main_unshaded.glsl"
        shaders.append(add_shader(shader_code_path + vertex_path, shader_code_path + fragment_path))

        vertex_path = "vertex_texture.glsl"
        fragment_path = "fragment_texture_shaded.glsl"
        shaders.append(add_shader(shader_code_path + vertex_path, shader_code_path + fragment_path))

        vertex_path = "vertex_texture.glsl"
        fragment_path = "fragment_texture_unshaded.glsl"
        shaders.append(add_shader(shader_code_path + vertex_path, shader_code_path + fragment_path))

        vertex_path = "vertex_screen.glsl"

        fragment_path = "fragment_screen_default.glsl"
        shaders.append(add_shader(shader_code_path + vertex_path, shader_code_path + fragment_path))

        fragment_path = "fragment_screen_blur.glsl"
        shaders.append(add_shader(shader_code_path + vertex_path, shader_code_path + fragment_path))

        fragment_path = "fragment_screen_outline.glsl"
        shaders.append(add_shader(shader_code_path + vertex_path, shader_code_path + fragment_path))

        for shader in shaders:
            shader.use()

        shaders[0].use()
        model_loc = shaders[0].get_uniform_location("projection")
        assert model_loc == 0
