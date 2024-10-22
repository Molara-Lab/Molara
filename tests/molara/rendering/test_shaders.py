"""Unittests for the shaders module."""

from __future__ import annotations

import hashlib
import sys
import unittest

import pytest
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow

from molara.rendering import shaders


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Test is not compatible with Windows",
)
class TestShaders(unittest.TestCase):
    """Contains the tests for the shaders module."""

    def test_compile_shaders(self) -> None:
        """Tests the compile_shaders function of the shaders module."""
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
        program = shaders.compile_shaders()
        assert isinstance(program, list)

    def test_shader_src(self) -> None:
        """Tests the vertex_src variable of the shaders module.

        This is done by comparing the hash of the vertex_src and fragment_src C codes with the expected hashes.
        Basically, this means that these codes should not be changed unless one really knows what they are doing.
        """
        assert isinstance(shaders.vertex_src_main, str)
        vertex_src_hash = hashlib.sha256(shaders.vertex_src_main.encode()).hexdigest()
        assert vertex_src_hash == "650efcd6e07d8d24f014d9be78edb39016949260ce5776f3f98e50893d1d30e9"
        fragment_src_hash = hashlib.sha256(
            shaders.fragment_src_main.encode(),
        ).hexdigest()

        assert fragment_src_hash == "ab6ad33c9678f8ca7b8a0be445cae2ad2f5c10ff7e08efc14aaa688e922b335e"
