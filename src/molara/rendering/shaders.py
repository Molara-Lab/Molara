"""Contains the shader source code for the rendering of the structures."""

from __future__ import annotations

from pathlib import Path

from OpenGL.GL import (
    GL_FRAGMENT_SHADER,
    GL_VERTEX_SHADER,
    glAttachShader,
    glCreateProgram,
    glGetUniformLocation,
    glLinkProgram,
    glUseProgram,
)
from OpenGL.GL.shaders import compileShader

__copyright__ = "Copyright 2024, Molara"


class Shader:
    """Contains the shader source code for the rendering of the structures."""

    def __init__(self) -> None:
        """Initialize the Shader class."""
        self.program: int = -1

    def compile_shaders(self, vertex_path: str, fragment_path: str) -> None:
        """Compiles the shader program with the given shader source code in glsl.

        :param vertex_path: The path to the vertex shader source code.
        :param fragment_path: The path to the fragment shader source code.
        """

        def load_shader(path_: str) -> str:
            path = Path(path_)
            with path.open() as file:
                return file.read()

        # Main shader
        vertex_shader = compileShader(load_shader(vertex_path), GL_VERTEX_SHADER)
        fragment_shader = compileShader(load_shader(fragment_path), GL_FRAGMENT_SHADER)
        self.program = glCreateProgram()
        glAttachShader(self.program, vertex_shader)
        glAttachShader(self.program, fragment_shader)
        glLinkProgram(self.program)

    def use(self) -> None:
        """Use the shader program."""
        glUseProgram(self.program)

    def get_uniform_location(self, name: str) -> int:
        """Get the uniform location of the given uniform name.

        :param name: The name of the uniform.
        :return: The uniform location.
        """
        return glGetUniformLocation(self.program, name)
