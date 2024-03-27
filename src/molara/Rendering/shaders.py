"""Contains the shader source code for the rendering of the structures."""

from __future__ import annotations

from OpenGL.GL import (
    GL_FRAGMENT_SHADER,
    GL_VERTEX_SHADER,
    GLuint,
    glAttachShader,
    glCreateProgram,
    glLinkProgram,
    glUseProgram,
)
from OpenGL.GL.shaders import compileShader

__copyright__ = "Copyright 2024, Molara"


def compile_shaders() -> GLuint:
    """Compiles the shader program with the given shader source code in glsl.

    :return: The compiled shader program from pyopengl.
    """
    vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)
    shader = glCreateProgram()
    glAttachShader(shader, vertex_shader)
    glAttachShader(shader, fragment_shader)
    glLinkProgram(shader)
    glUseProgram(shader)
    return shader


vertex_src = """
# version 410 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec3 a_color;
layout(location = 3) in mat4 a_model;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;
uniform vec3 light_direction;

out vec3 v_color;
out vec3 v_normal;
out vec3 v_light_dir;
out vec3 v_fragment_position;

void main()
{
    vec3 fragment_position = vec3(a_model * vec4(a_position, 1.0));
    v_fragment_position = fragment_position;
    gl_Position = projection * view * vec4(fragment_position, 1.0);
    v_color = a_color;
    v_light_dir = light_direction;
    v_normal = mat3(transpose(inverse(a_model))) * a_normal;
}
"""

fragment_src = """
# version 410 core

in vec3 v_color;
in vec3 v_light_dir;
in vec3 v_normal;
in vec3 v_fragment_position;

uniform vec3 camera_position;

out vec4 out_color;

void main()
{
    vec3 normal = normalize(v_normal);
    vec3 light_dir = normalize(-v_light_dir);
    vec3 light_fragment_direction = normalize(light_dir - v_fragment_position);
    vec3 camera_fragment_direction = normalize(camera_position - v_fragment_position);
    vec3 halfway = normalize(light_fragment_direction + camera_fragment_direction);


    float diff = max(dot(normal, light_dir), 0.0) * 0.66667 + 0.33334;

    float spec = pow(max(dot(normal, halfway), 0.0), 25);

    vec3 light_color = vec3(1.0, 1.0, 1.0);    // Light color

    vec3 result = v_color * light_color * diff;// + spec;
    out_color = vec4(result, 1.0);
}
"""
