"""Contains the shader source code for the rendering of the structures."""

from __future__ import annotations

from OpenGL.GL import (
    GL_FRAGMENT_SHADER,
    GL_VERTEX_SHADER,
    GL_GEOMETRY_SHADER,
    GLuint,
    glAttachShader,
    glCreateProgram,
    glLinkProgram,
)
from OpenGL.GL.shaders import compileShader

__copyright__ = "Copyright 2024, Molara"


def compile_shaders() -> list[GLuint]:
    """Compiles the shader program with the given shader source code in glsl.

    :return: The compiled shader program from pyopengl.
    """
    vertex_shader = compileShader(vertex_src_main, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_src_main, GL_FRAGMENT_SHADER)
    shader = glCreateProgram()
    glAttachShader(shader, vertex_shader)
    glAttachShader(shader, fragment_shader)
    glLinkProgram(shader)
    shaders: list[GLuint] = [shader]

    vertex_shader = compileShader(vertex_src_lines, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_src_lines, GL_FRAGMENT_SHADER)
    geometry_shader = compileShader(geometry_src_lines, GL_GEOMETRY_SHADER)
    shader = glCreateProgram()
    glAttachShader(shader, vertex_shader)
    glAttachShader(shader, fragment_shader)
    glAttachShader(shader, geometry_shader)
    glLinkProgram(shader)
    shaders.append(shader)
    return shaders


vertex_src_main = """
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

fragment_src_main = """
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

vertex_src_lines = """
#version 410 core
layout (location = 0) in vec2 aPos;

void main()
{
    gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0);
    gl_PointSize = 10.0;
}
"""

fragment_src_lines = """
#version 410 core
out vec4 out_color;

void main()
{
    out_color = vec4(0.0, 1.0, 0.0, 1.0);   
}
"""

geometry_src_lines = """
#version 330 core
layout (points) in;
layout (line_strip, max_vertices = 5) out;

void build_house(vec4 position)
{    
    gl_Position = position + vec4(-0.2, -0.2, 0.0, 0.0);    // 1:bottom-left
    EmitVertex();   
    gl_Position = position + vec4( 0.2, -0.2, 0.0, 0.0);    // 2:bottom-right
    EmitVertex();
    gl_Position = position + vec4(-0.2,  0.2, 0.0, 0.0);    // 3:top-left
    EmitVertex();
    gl_Position = position + vec4( 0.2,  0.2, 0.0, 0.0);    // 4:top-right
    EmitVertex();
    gl_Position = position + vec4( 0.0,  0.4, 0.0, 0.0);    // 5:top
    EmitVertex();
    EndPrimitive();
}

void main() {    
    build_house(gl_in[0].gl_Position);
}  
"""

geometry_src_lines_with_linewidth = """
#version 330 core
layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;

uniform float lineWidth;

void main() {
    vec4 p0 = gl_in[0].gl_Position;
    vec4 p1 = gl_in[1].gl_Position;

    vec2 dir = normalize(p1.xy - p0.xy);
    vec2 normal = vec2(-dir.y, dir.x) * lineWidth * 0.5;

    gl_Position = p0 + vec4(normal, 0.0, 0.0);
    EmitVertex();

    gl_Position = p1 + vec4(normal, 0.0, 0.0);
    EmitVertex();

    gl_Position = p0 - vec4(normal, 0.0, 0.0);
    EmitVertex();

    gl_Position = p1 - vec4(normal, 0.0, 0.0);
    EmitVertex();

    EndPrimitive();
}
"""

