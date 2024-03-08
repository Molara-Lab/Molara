"""Unittests for the shaders module."""

from __future__ import annotations

import hashlib
import unittest

from molara.Rendering import shaders


class TestShaders(unittest.TestCase):
    """This class contains the tests for the shaders module."""

    def test_compile_shaders(self) -> None:
        """Tests the compile_shaders function of the shaders module."""
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
