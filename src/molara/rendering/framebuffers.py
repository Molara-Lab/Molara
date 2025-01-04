"""Contains the framebuffer class."""

from OpenGL.GL import (
    GL_COLOR_ATTACHMENT0,
    GL_COLOR_ATTACHMENT1,
    GL_COLOR_ATTACHMENT2,
    GL_DEPTH_ATTACHMENT,
    GL_DEPTH_COMPONENT,
    GL_DRAW_FRAMEBUFFER,
    GL_FLOAT,
    GL_FRAMEBUFFER,
    GL_LINEAR,
    GL_READ_FRAMEBUFFER,
    GL_RGB,
    GL_RGB32F,
    GL_RGBA,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_UNSIGNED_BYTE,
    glBindFramebuffer,
    glBindTexture,
    glDrawBuffers,
    glFramebufferTexture2D,
    glGenFramebuffers,
    glGenTextures,
    glTexImage2D,
    glTexParameteri,
)


class Framebuffer:
    """Create a Framebuffer object."""

    def __init__(self) -> None:
        """Initialize the Framebuffer class."""
        self.ssaa_factor = 1
        self.width = 0
        self.height = 0
        self.buffer_size_factor = 1
        self.buffer = -1
        self.texture_color_buffer = -1
        self.texture_color_buffer2 = -1
        self.texture_normal_buffer = -1
        self.texture_depth_buffer = -1

    def create(self, width: int, height: int) -> None:
        """Create a framebuffer object."""

        def create_texture_buffer(
            texture: int,
            var_internal_format: int,
            var_format: int,
            data_type: int,
            attachment: int,
        ) -> None:
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, var_internal_format, self.width, self.height, 0, var_format, data_type, None)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D, texture, 0)

        self.width = width * self.buffer_size_factor
        self.height = height * self.buffer_size_factor

        self.buffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.buffer)
        glDrawBuffers(3, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2])

        self.texture_color_buffer = glGenTextures(1)
        create_texture_buffer(self.texture_color_buffer, GL_RGBA, GL_RGBA, GL_UNSIGNED_BYTE, GL_COLOR_ATTACHMENT0)

        self.texture_normal_buffer = glGenTextures(1)
        create_texture_buffer(self.texture_normal_buffer, GL_RGB32F, GL_RGB, GL_FLOAT, GL_COLOR_ATTACHMENT1)

        self.texture_color_buffer2 = glGenTextures(1)
        create_texture_buffer(self.texture_color_buffer2, GL_RGBA, GL_RGBA, GL_UNSIGNED_BYTE, GL_COLOR_ATTACHMENT2)

        self.texture_depth_buffer = glGenTextures(1)
        create_texture_buffer(
            self.texture_depth_buffer,
            GL_DEPTH_COMPONENT,
            GL_DEPTH_COMPONENT,
            GL_FLOAT,
            GL_DEPTH_ATTACHMENT,
        )

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def bind(self) -> None:
        """Bind the framebuffer."""
        glBindFramebuffer(GL_FRAMEBUFFER, self.buffer)

    def bind_read(self) -> None:
        """Bind the framebuffer for reading."""
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.buffer)

    def bind_draw(self) -> None:
        """Bind the framebuffer for drawing."""
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.buffer)

    def bind_color_texture(self) -> None:
        """Bind the first color texture."""
        glBindTexture(GL_TEXTURE_2D, self.texture_color_buffer)

    def bind_color_texture2(self) -> None:
        """Bind the second color texture."""
        glBindTexture(GL_TEXTURE_2D, self.texture_color_buffer2)

    def bind_normal_texture(self) -> None:
        """Bind the normal texture."""
        glBindTexture(GL_TEXTURE_2D, self.texture_normal_buffer)

    def bind_depth_texture(self) -> None:
        """Bind the depth texture."""
        glBindTexture(GL_TEXTURE_2D, self.texture_depth_buffer)
