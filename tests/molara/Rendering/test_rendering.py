"""This module contains the tests for the rendering module."""

from __future__ import annotations

import unittest

from molara.Rendering.rendering import Renderer


class TestRenderer(unittest.TestCase):
    """This class contains the tests for the Renderer class."""

    def setUp(self) -> None:
        """Instantiates the Renderer object."""
        self.renderer = Renderer()

    def test_init(self) -> None:
        """Tests the __init__ method of the Renderer class."""
        assert isinstance(self.renderer, Renderer)
        assert isinstance(self.renderer.atoms_vao, dict)
        assert isinstance(self.renderer.bonds_vao, dict)
        assert isinstance(self.renderer.spheres, list)
        assert isinstance(self.renderer.cylinders, list)
        assert self.renderer.shader == 0
