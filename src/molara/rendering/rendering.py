"""Contains the rendering function for the opengl widget."""

# mypy: disable-error-code="name-defined"
from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING

import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_FALSE,
    GL_FILL,
    GL_FLOAT,
    GL_FRAMEBUFFER,
    GL_FRONT_AND_BACK,
    GL_LINE,
    GL_MULTISAMPLE,
    GL_STATIC_DRAW,
    GL_TEXTURE0,
    GL_TEXTURE1,
    GL_TEXTURE2,
    GL_TEXTURE3,
    GL_TEXTURE_2D,
    GL_TRIANGLES,
    GL_UNSIGNED_INT,
    glActiveTexture,
    glBindBuffer,
    glBindFramebuffer,
    glBindTexture,
    glBindVertexArray,
    glBufferData,
    glClear,
    glDisable,
    glDrawArrays,
    glDrawArraysInstanced,
    glDrawElementsInstanced,
    glEnable,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenVertexArrays,
    glPolygonMode,
    glUniform1i,
    glUniform3fv,
    glUniformMatrix4fv,
    glVertexAttribPointer,
    glViewport,
)

from molara.rendering.billboards import Billboards
from molara.rendering.cylinders import Cylinders
from molara.rendering.framebuffers import Framebuffer
from molara.rendering.polygons import Polygon
from molara.rendering.shaders import Shader
from molara.rendering.spheres import Spheres

if TYPE_CHECKING:
    from numpy import floating
    from PIL import Image

    from molara.gui.structure_widget import StructureWidget
    from molara.rendering.camera import Camera
    from molara.rendering.object3d import Object3D

__copyright__ = "Copyright 2024, Molara"

SHADED = "Shaded"
UNSHADED = "Unshaded"
OUTLINED_SHADED = "OutlinedShaded"
OUTLINED_UNSHADED = "OutlinedUnshaded"
MODES = [SHADED, UNSHADED, OUTLINED_SHADED, OUTLINED_UNSHADED]


class Renderer:
    """Contains the rendering function for the opengl widget."""

    def __init__(self, opengl_widget: StructureWidget) -> None:
        """Create a Renderer object."""
        self.shaders: dict = {}
        self.opengl_widget = opengl_widget
        self.default_framebuffer = opengl_widget.defaultFramebufferObject()
        self.camera: Camera = opengl_widget.camera

        # multisampling anti-aliasing
        self.msaa = True
        # supersampling anti-aliasing factor
        self.ssaa_factor = 1.2

        self.device_pixel_ratio = 1
        self.objects3d: dict = {}
        self.textured_objects3d: dict = {}
        self.screen_vao = -1
        self.framebuffers: dict = {"Main": Framebuffer(), "Inter": Framebuffer()}
        self.framebuffers["Main"].ssaa_factor = self.ssaa_factor
        self.framebuffers["Inter"].ssaa_factor = self.ssaa_factor
        self.mode: str = ""
        self.shade: str = ""
        self.set_mode(OUTLINED_SHADED)

    def set_mode(self, mode: str) -> None:
        """Set the mode of the renderer.

        :param mode: Mode of the renderer.
        """
        assert mode in MODES
        self.mode = mode
        if mode in (SHADED, OUTLINED_SHADED):
            self.shade = "Shaded"
        elif mode in (UNSHADED, OUTLINED_UNSHADED):
            self.shade = "Unshaded"

    def create_framebuffers(self, width: float, height: float) -> None:
        """Create the framebuffers of the renderer."""
        self.framebuffers["Main"].create(width, height)
        self.framebuffers["Inter"].create(width, height)
        self.framebuffers["Main"].buffer_size_factor = self.device_pixel_ratio * self.ssaa_factor
        self.framebuffers["Inter"].buffer_size_factor = self.device_pixel_ratio * self.ssaa_factor

    def create_screen_vao(self) -> None:
        """Create a screen vao."""
        self.screen_vao = glGenVertexArrays(1)
        glBindVertexArray(self.screen_vao)

        quad_vertices = np.array(
            [
                -1.0,
                -1.0,
                0.0,
                0.0,  # Bottom-left
                1.0,
                -1.0,
                1.0,
                0.0,  # Bottom-right
                1.0,
                1.0,
                1.0,
                1.0,  # Top-right
                -1.0,
                -1.0,
                0.0,
                0.0,  # Bottom-left
                1.0,
                1.0,
                1.0,
                1.0,  # Top-right
                -1.0,
                1.0,
                0.0,
                1.0,  # Top-left
            ],
            dtype=np.float32,
        )

        screen_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, screen_vbo)
        glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * quad_vertices.itemsize, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * quad_vertices.itemsize, ctypes.c_void_p(8))

        glBindVertexArray(0)

    def enable_antialiasing(self) -> None:
        """Enable antialiasing."""
        self.msaa = True

    def disable_antialiasing(self) -> None:
        """Disable antialiasing."""
        self.msaa = False

    def set_shaders(self) -> None:
        """Set the shader program for the opengl widget."""

        def add_shader(name: str, vertex_path: str, fragment_path: str) -> None:
            """Add a shader to the shader program.

            :param name: Name of the shader.
            :param vertex_path: Path to the vertex shader.
            :param fragment_path: Path to the fragment shader.
            """
            shader = Shader()
            shader.compile_shaders(vertex_path, fragment_path)
            self.shaders[name] = shader

        shader_code_path = "src/molara/rendering/shadercode/"

        vertex_path = "vertex_main.glsl"
        fragment_path = "fragment_main_shaded.glsl"
        add_shader("MainShaded", shader_code_path + vertex_path, shader_code_path + fragment_path)

        vertex_path = "vertex_main.glsl"
        fragment_path = "fragment_main_unshaded.glsl"
        add_shader("MainUnshaded", shader_code_path + vertex_path, shader_code_path + fragment_path)

        vertex_path = "vertex_texture.glsl"
        fragment_path = "fragment_texture_shaded.glsl"
        add_shader("TextureShaded", shader_code_path + vertex_path, shader_code_path + fragment_path)

        vertex_path = "vertex_texture.glsl"
        fragment_path = "fragment_texture_unshaded.glsl"
        add_shader("TextureUnshaded", shader_code_path + vertex_path, shader_code_path + fragment_path)

        vertex_path = "vertex_screen.glsl"

        fragment_path = "fragment_screen_default.glsl"
        add_shader("Screen", shader_code_path + vertex_path, shader_code_path + fragment_path)

        fragment_path = "fragment_screen_blur.glsl"
        add_shader("Blur", shader_code_path + vertex_path, shader_code_path + fragment_path)

        fragment_path = "fragment_screen_outline.glsl"
        add_shader("Outline", shader_code_path + vertex_path, shader_code_path + fragment_path)

    def draw_billboards(
        self,
        name: str,
        positions: np.ndarray,
        normals: np.ndarray,
        sizes: np.ndarray,
        texture: Image.Image,
    ) -> None:
        """Draw one or multiple billboards with the same textures.

        If only one billboard is drawn, the positions, normals, and sizes are given
        as np.ndarray containing only one array, for instance: positions = np.array([[0, 0, 0]]). If multiple
        billboards are drawn, the positions, normals, and sizes are given as np.ndarray containing multiple arrays, for
        instance: positions = np.array([[0, 0, 0], [1, 1, 1]]).

        :param name: Name of the billboards that were created, this is used to remove the billboards again.
        :param positions: Positions of the billboards.
        :param normals: Normals of the billboards.
        :param sizes: Sizes of the cylinders.
        :param texture: A PIL image used as a texture.
        """
        self.opengl_widget.makeCurrent()
        self.textured_objects3d[name] = Billboards(positions, normals, sizes, texture)
        self.textured_objects3d[name].generate_buffers()

    def draw_polygon(
        self,
        name: str,
        vertices: np.ndarray,
        color: np.ndarray,
    ) -> None:
        """Draws one polygon.

        :param vertices: Vertices in the following order x,y,z,nx,ny,nz,..., where xyz are the cartesian coordinates.
        :param color: Colors of the vertices.
        """
        self.opengl_widget.makeCurrent()
        self.objects3d[name] = Polygon(vertices, color)
        self.objects3d[name].generate_buffers()

    def draw_cylinders(  # noqa: PLR0913
        self,
        name: str,
        positions: np.ndarray,
        directions: np.ndarray,
        dimensions: np.ndarray,
        colors: np.ndarray,
        subdivisions: int,
    ) -> None:
        """Draws one or multiple cylinders.

        If only one cylinder is drawn, the positions, directions, radii, lengths and colors are given as np.ndarray
        containing only one array, for instance: positions = np.array([[0, 0, 0]]). If multiple cylinders are drawn,
        the positions, directions, radii, lengths and colors are given as np.ndarray containing multiple arrays, for
        instance: positions = np.array([[0, 0, 0], [1, 1, 1]]).

        :param name: Name of the cylinders that were created, this is used to remove the cylinders again.
        :param positions: Positions of the cylinders.
        :param directions: Directions of the cylinders.
        :param dimensions: Dimensions of the cylinders ([[radius, length, radius] * number_of_instances]).
        :param colors: Colors of the cylinders.
        :param subdivisions: Number of subdivisions of the cylinder.
        :return: Returns the index of the cylinder in the list of cylinders.
        """
        self.opengl_widget.makeCurrent()
        self.objects3d[name] = Cylinders(subdivisions, positions, directions, dimensions, colors)
        self.objects3d[name].generate_buffers()

    def draw_cylinders_from_to(
        self,
        name: str,
        positions: np.ndarray,
        radii: np.ndarray,
        colors: np.ndarray,
        subdivisions: int,
    ) -> None:
        """Draws one or multiple cylinders.

        :param name: Name of the spheres that were created, this is used to remove the spheres again.
        :param positions: Positions [[start, end], [start, end], ...] of the cylinders.
        :param radii: Radii of the cylinders.
        :param colors: Colors of the cylinders.
        :param subdivisions: Number of subdivisions of the cylinder.
        :return: Returns the index of the cylinder in the list of cylinders.
        """
        self.opengl_widget.makeCurrent()
        _directions: list[list[floating]] = []
        _lengths: list[floating] = []
        _positions_middle: list[list[list[floating]]] = []

        pos1, pos2 = positions[:, 0], positions[:, 1]
        lengths = np.linalg.norm(pos2 - pos1, axis=1)
        valid = lengths > np.finfo(np.float32).eps
        _directions = (pos2 - pos1)[valid].tolist()
        _lengths = lengths[valid].tolist()
        _positions_middle = (0.5 * (pos1 + pos2))[valid].tolist()

        positions_middle = np.array(_positions_middle, dtype=np.float32)
        lengths = np.array(_lengths)
        dimensions = np.zeros((len(_lengths), 3), dtype=np.float32)
        dimensions[:, 0] = radii[valid]
        dimensions[:, 1] = lengths
        dimensions[:, 2] = radii[valid]
        directions = np.array(_directions) / lengths[:, None]
        self.draw_cylinders(name, positions_middle, -directions.astype(np.float32), dimensions, colors, subdivisions)

    def draw_spheres(  # noqa: PLR0913
        self,
        name: str,
        positions: np.ndarray,
        radii: np.ndarray,
        colors: np.ndarray,
        subdivisions: int,
        wire_frame: bool = False,
    ) -> None:
        """Draws one or multiple spheres.

        If only one sphere is drawn, the positions, radii and colors are given
        as np.ndarray containing only one array, for instance: positions = np.array([[0, 0, 0]]). If multiple
        spheres are drawn, the positions, radii and colors are given as np.ndarray containing multiple arrays, for
        instance: positions = np.array([[0, 0, 0], [1, 1, 1]]).

        :param name: Name of the spheres that were created, this is used to remove the spheres again.
        :param positions: Positions of the spheres.
        :param radii: Radii of the spheres.
        :param colors: Colors of the spheres.
        :param subdivisions: Number of subdivisions of the sphere.
        :param wire_frame: If True, the sphere is drawn as wire mesh.
        :return: Returns the index of the sphere in the list of spheres.
        """
        self.opengl_widget.makeCurrent()
        self.objects3d[name] = Spheres(subdivisions, positions, radii, colors, wire_frame=wire_frame)
        self.objects3d[name].generate_buffers()

    def remove_object(self, name: str) -> None:
        """Remove an object3d from the list of object3ds.

        :param name: name of the object to be removed.
        """
        self.opengl_widget.makeCurrent()
        if name in self.objects3d:
            del self.objects3d[name]
        elif name in self.textured_objects3d:
            del self.textured_objects3d[name]
        else:
            msg = f"Spheres with the name '{name}' not found!"
            raise ValueError(msg)

    def _init_rendering(self, shader_name: str) -> None:
        """Initialize the uniform location of the shader code.

        :param shader_name: Name of the shader to be initialized.
        """
        self.shaders[shader_name].use()
        light_direction_loc = self.shaders[shader_name].get_uniform_location("light_direction")
        proj_loc = self.shaders[shader_name].get_uniform_location("projection")
        camera_loc = self.shaders[shader_name].get_uniform_location("camera_position")
        view_loc = self.shaders[shader_name].get_uniform_location("view")

        light_direction = -self.camera.position - self.camera.up_vector * self.camera.distance_from_target * 0.5
        glUniform3fv(light_direction_loc, 1, light_direction)
        glUniform3fv(camera_loc, 1, self.camera.position)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, self.camera.projection_matrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, self.camera.view_matrix)

    def draw_scene(
        self,
    ) -> None:
        """Draws the scene."""
        if self.mode in (SHADED, UNSHADED):
            if not self.msaa:
                glDisable(GL_MULTISAMPLE)
            else:
                glEnable(GL_MULTISAMPLE)
            self.draw_scene_default()
        elif self.mode in (OUTLINED_UNSHADED, OUTLINED_SHADED):
            glDisable(GL_MULTISAMPLE)
            size_factor = self.framebuffers["Main"].buffer_size_factor
            glViewport(0, 0, int(self.camera.width * size_factor), int(self.camera.height * size_factor))
            self.draw_scene_outlined()

    def render_objects(self) -> None:
        """Render the objects in the scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        self._init_rendering(shader_name="Main" + self.shade)
        for object_ in self.objects3d.values():
            _render_object(object_)

        self._init_rendering(shader_name="Texture" + self.shade)

        for object_ in self.textured_objects3d.values():
            glBindTexture(GL_TEXTURE_2D, object_.buffers.texture)
            _render_object(object_)
            glBindTexture(GL_TEXTURE_2D, 0)

    def render_to_screen(self, shader_name: str, width: float, height: float) -> None:
        """Blur the color buffer inter framebuffer as a sort of antialiasing.

        :param shader_name: Name of the shader to be used. Can also contain one more post-processing step.
        :param width: Width of the screen.
        :param height: Height of the screen.
        """
        self.shaders[shader_name].use()
        glBindFramebuffer(GL_FRAMEBUFFER, self.default_framebuffer)
        glViewport(0, 0, int(width * self.device_pixel_ratio), int(height * self.device_pixel_ratio))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        glUniform1i(self.shaders[shader_name].get_uniform_location("screenTexture"), 0)  # Texture unit 0
        glActiveTexture(GL_TEXTURE0)
        self.framebuffers["Inter"].bind_color_texture()

        glBindVertexArray(self.screen_vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)

    def init_post_processing_shader(self, post_processing_shader: str) -> None:
        """Initialize the post-processing shader.

        :param post_processing_shader: Name of the post-processing shader.
        """
        # Use the post-processing shader
        self.shaders[post_processing_shader].use()

        # Set the uniforms for the texture locations inside the shader program
        # texture unit 0
        glUniform1i(self.shaders[post_processing_shader].get_uniform_location("screenTexture"), 0)
        # texture unit 1
        glUniform1i(self.shaders[post_processing_shader].get_uniform_location("depthTexture"), 1)
        # texture unit 2
        glUniform1i(self.shaders[post_processing_shader].get_uniform_location("normalTexture"), 2)
        # texture unit 3
        glUniform1i(self.shaders[post_processing_shader].get_uniform_location("screenUnshadedTexture"), 3)

    def post_process_main_buffer(
        self,
        post_processing_shader: str,
    ) -> None:
        """Post process the main buffer.

        This function uses the post-processing shader to post process the main buffer and render the new image to the
        Inter framebuffer for further use.

        :param post_processing_shader: Name of the post-processing shader.
        :param width: Width of the screen.
        :param height: Height of the screen.
        """
        self.init_post_processing_shader(post_processing_shader)
        self.framebuffers["Inter"].bind()

        # Reset framebuffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        # Bind textures
        glActiveTexture(GL_TEXTURE1)
        self.framebuffers["Main"].bind_depth_texture()
        glActiveTexture(GL_TEXTURE2)
        self.framebuffers["Main"].bind_normal_texture()

        glActiveTexture(GL_TEXTURE0)
        self.framebuffers["Main"].bind_color_texture()
        glActiveTexture(GL_TEXTURE3)
        self.framebuffers["Main"].bind_color_texture2()

        # Draw textured quad across screen
        glBindVertexArray(self.screen_vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)

    def draw_scene_default(
        self,
    ) -> None:
        """Draws the scene.

        Uses the default shader to draw the scene.
        """
        # Render scene directly to the screen
        glBindFramebuffer(GL_FRAMEBUFFER, self.default_framebuffer)
        self.render_objects()

    def draw_scene_outlined(
        self,
    ) -> None:
        """Draws the scene."""
        # initial rendering to framebuffer
        self.framebuffers["Main"].bind()
        self.render_objects()

        # post-processing on framebuffer
        shader_name = "Outline"
        self.post_process_main_buffer(shader_name)

        # Draw to screen
        shader_name = "Screen"
        self.render_to_screen(shader_name, self.camera.width, self.camera.height)


def _render_object(object_: Object3D) -> None:
    """Draw a 3D object.

    :param object_: Object3D object to be drawn.
    """
    if object_.wire_frame:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glBindVertexArray(object_.vao)
    if object_.buffers.ebo != -1:
        glDrawElementsInstanced(
            GL_TRIANGLES,
            object_.number_of_vertices,
            GL_UNSIGNED_INT,
            None,
            object_.number_of_instances,
        )
    else:
        glDrawArraysInstanced(GL_TRIANGLES, 0, object_.number_of_vertices, object_.number_of_instances)
    if object_.wire_frame:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glBindVertexArray(0)
