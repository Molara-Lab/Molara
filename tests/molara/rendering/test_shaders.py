"""Unittests for the shaders module."""

from __future__ import annotations

import hashlib
import sys
import unittest

import pytest
from molara.Rendering import shaders
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow


@pytest.mark.skipif(sys.platform == "win32", reason="Test is not compatible with Windows")
class TestShaders(unittest.TestCase):
    """Contains the tests for the shaders module."""

    def test_compile_shaders(self) -> None:
        """Tests the compile_shaders function of the shaders module."""
        QApplication.instance().shutdown() if QApplication.instance() else None  # type: ignore[union-attr]
        QApplication([])
        _format = QSurfaceFormat()
        _format.setVersion(4, 1)
        _format.setSamples(4)
        _format.setProfile(QSurfaceFormat.CoreProfile)  # type: ignore[attr-defined]
        QSurfaceFormat.setDefaultFormat(_format)
        main_window = QMainWindow()
        openglwidget = QOpenGLWidget(main_window)
        openglwidget.show()
        main_window.show()
        program = shaders.compile_shaders()
        assert isinstance(program, int)

    def test_vertex_src(self) -> None:
        """Tests the vertex_src variable of the shaders module.

        This is done by comparing the hash of the vertex_src and fragment_src C codes with the expected hashes.
        Basically, this means that these codes should not be changed unless one really knows what they are doing.
        """
        assert isinstance(shaders.vertex_src, str)
        vertex_src_hash = hashlib.sha256(shaders.vertex_src.encode()).hexdigest()
        assert vertex_src_hash == "2c5f85792b0479049bab350bab526d4340fa77fd3c5841a1b31bcc5d1bce8f85"
        fragment_src_hash = hashlib.sha256(shaders.fragment_src.encode()).hexdigest()
        assert fragment_src_hash == "2ba20ad6145f29b5ea0e47405c3bad0fe484ff81e961e4f865d4bc763f6e507f"
