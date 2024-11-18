"""Contains the shader source code for the rendering of the structures."""

from __future__ import annotations

from OpenGL.GL import (
    GL_FRAGMENT_SHADER,
    GL_GEOMETRY_SHADER,
    GL_VERTEX_SHADER,
    GLuint,
    glAttachShader,
    glCreateProgram,
    glLinkProgram,
)
from OpenGL.GL.shaders import ShaderCompilationError, compileShader

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

    vertex_shader = compileShader(vertex_src_numbers, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_src_numbers, GL_FRAGMENT_SHADER)
    try:
        geometry_shader = compileShader(geometry_src_numbers_indices, GL_GEOMETRY_SHADER)
    except ShaderCompilationError:
        geometry_shader = compileShader(geometry_src_numbers_no_indices, GL_GEOMETRY_SHADER)
        print("Using geometry shader without indices")  # noqa: T201
    shader = glCreateProgram()
    glAttachShader(shader, vertex_shader)
    glAttachShader(shader, fragment_shader)
    glAttachShader(shader, geometry_shader)
    glLinkProgram(shader)
    shaders.append(shader)
    return shaders


vertex_src_main = """
# version 330 core

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
# version 330 core

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

    // not exactly 0.33334 to ensure that pixels of atoms or any other object are never completely white
    // This is used for the transparent background
    float diff = max(dot(normal, light_dir), 0.0) * 0.66667 + 0.33;

    float spec = pow(max(dot(normal, halfway), 0.0), 25);

    vec3 light_color = vec3(1.0, 1.0, 1.0);    // Light color

    vec3 result = v_color * light_color * diff;// + spec;
    out_color = vec4(result, 1.0);
}
"""

vertex_src_numbers = """
#version 410 core
layout (location = 0) in uint digit;
layout (location = 1) in vec3 position;

uniform float aspect_ratio;
uniform float scale;
uniform mat4 projection;
uniform mat4 view;

out float aspect_ratio_v;
out uint digit_v;
out float scale_v;

void main()
{
    aspect_ratio_v = aspect_ratio;
    digit_v = digit;
    scale_v = scale;
    gl_Position = projection * view * vec4(position, 1.0);
}
"""

fragment_src_numbers = """
#version 410 core
uniform vec3 color_in;

out vec4 out_color;

void main()
{
    out_color = vec4(color_in, 1.0);
}
"""

geometry_src_numbers_indices = """
#version 330 core
layout (points) in;
layout (triangle_strip, max_vertices = 350) out;

in float aspect_ratio_v[];
in uint digit_v[];
in float scale_v[];

void draw_horizontal_line(vec4 position, float aspect_ratio, float scale)
{
    float radius = 0.05 * scale;
    float angle = 0.0;
    int subsections = 2;
    float pi = 3.14159265359;
    float pi_2 = pi / 2;
    float inv_ar = 1 / aspect_ratio;
    float x = 0.2 * inv_ar * scale;
    float y = 0.05 * scale;

    gl_Position = position + vec4(-x, -y, 0.0, 0.0);    // 1:bottom-left
    EmitVertex();
    gl_Position = position + vec4( x, -y, 0.0, 0.0);    // 2:bottom-right
    EmitVertex();
    gl_Position = position + vec4(-x,  y, 0.0, 0.0);    // 3:top-left
    EmitVertex();
    gl_Position = position + vec4( x,  y, 0.0, 0.0);    // 4:top-right
    EmitVertex();
    vec4 temp_pos = position + vec4(x, 0.0, 0.0, 0.0);
    gl_Position = temp_pos;
    EmitVertex();

    for (int i = 0; i <= subsections; i++)
    {
        gl_Position = temp_pos + vec4(radius * cos(angle - pi_2) * inv_ar, radius * sin(angle - pi_2), 0.0, 0.0);
        EmitVertex();
        gl_Position = temp_pos;
        EmitVertex();
        angle += 3.14159265359 / subsections;
    }
    EndPrimitive();

    temp_pos = position + vec4(-x, 0.0, 0.0, 0.0);
    gl_Position = temp_pos;
    EmitVertex();

    angle = 0.0;
    for (int i = 0; i <= subsections; i++)
    {
        gl_Position = temp_pos + vec4(radius * cos(angle + pi_2) * inv_ar, radius * sin(angle + pi_2), 0.0, 0.0);
        EmitVertex();
        gl_Position = temp_pos;
        EmitVertex();
        angle += 3.14159265359 / subsections;
    }
    EndPrimitive();
}
void draw_vertical_line(vec4 position_, float aspect_ratio, float scale)
{
    float radius = 0.05 * scale;
    float angle = 0.0;
    int subsections = 2;
    float pi = 3.14159265359;
    float pi_2 = pi / 2;
    float inv_ar = 1 / aspect_ratio;
    float x = 0.05 * inv_ar * scale;
    float y = 0.2 * scale;

    gl_Position = position_ + vec4(-x, -y, 0.0, 0.0);    // 1:bottom-left
    EmitVertex();
    gl_Position = position_ + vec4( x, -y, 0.0, 0.0);    // 2:bottom-right
    EmitVertex();
    gl_Position = position_ + vec4(-x,  y, 0.0, 0.0);    // 3:top-left
    EmitVertex();
    gl_Position = position_ + vec4( x,  y, 0.0, 0.0);    // 4:top-right
    EmitVertex();
    vec4 temp_pos = position_ + vec4(0.0, y, 0.0, 0.0);
    gl_Position = temp_pos;
    EmitVertex();

    for (int i = 0; i <= subsections; i++)
    {
        gl_Position = temp_pos + vec4(radius * cos(angle) * inv_ar, radius * sin(angle), 0.0, 0.0);
        EmitVertex();
        gl_Position = temp_pos;
        EmitVertex();
        angle += 3.14159265359 / subsections;
    }
    EndPrimitive();

    temp_pos = position_ + vec4(0.0, -y, 0.0, 0.0);
    gl_Position = temp_pos;
    EmitVertex();

    angle = 0.0;
    for (int i = 0; i <= subsections; i++)
    {
        gl_Position = temp_pos + vec4(radius * cos(angle) * inv_ar, radius * sin(angle), 0.0, 0.0);
        EmitVertex();
        gl_Position = temp_pos;
        EmitVertex();
        angle -= 3.14159265359 / subsections;
    }
    EndPrimitive();
}

void display_0(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_1(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;

    vec4 temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_2(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x * 1.0, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x* 1.0, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x* 1.0, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_3(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_4(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);


    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_5(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_6(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_7(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;

    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_8(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_9(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_digit(vec4 position, float aspect_ratio, uint digit, float scale)
{
    if (digit == 0u){
        display_0(position, aspect_ratio, scale);
    }
    else if (digit == 1u){
        display_1(position, aspect_ratio, scale);
    }
    else if (digit == 2u){
        display_2(position, aspect_ratio, scale);
    }
    else if (digit == 3u){
        display_3(position, aspect_ratio, scale);
    }
    else if (digit == 4u){
        display_4(position, aspect_ratio, scale);
    }
    else if (digit == 5u){
        display_5(position, aspect_ratio, scale);
    }
    else if (digit == 6u){
        display_6(position, aspect_ratio, scale);
    }
    else if (digit == 7u){
        display_7(position, aspect_ratio, scale);
    }
    else if (digit == 8u){
        display_8(position, aspect_ratio, scale);
    }
    else if (digit == 9u){
        display_9(position, aspect_ratio, scale);
    }
}

void main() {
    float ooo = 0.0;
    uint digit = digit_v[0];
    if (digit < 10u){
        display_digit(gl_in[0].gl_Position, aspect_ratio_v[0], digit, scale_v[0]);
    }
    else if (digit < 100u){
        uint digit1 = digit / 10u;
        display_digit(gl_in[0].gl_Position - vec4(0.2,0.0,0.0,0.0) * scale_v[0], aspect_ratio_v[0], digit1, scale_v[0]);
        uint digit2 = digit % 10u;
        display_digit(gl_in[0].gl_Position + vec4(0.2,0.0,0.0,0.0) * scale_v[0], aspect_ratio_v[0], digit2, scale_v[0]);
    }
    else if (digit < 1000u){
        uint digit1 = digit / 100u;
        display_digit(gl_in[0].gl_Position - vec4(0.4,0.0,0.0,0.0) * scale_v[0], aspect_ratio_v[0], digit1, scale_v[0]);
        uint digit2 = (digit % 100u) / 10u;
        display_digit(gl_in[0].gl_Position, aspect_ratio_v[0], digit2, scale_v[0]);
        uint digit3 = digit % 10u;
        display_digit(gl_in[0].gl_Position + vec4(0.4,0.0,0.0,0.0) * scale_v[0], aspect_ratio_v[0], digit3, scale_v[0]);
    }
}
"""

geometry_src_numbers_no_indices = """
#version 330 core
layout (points) in;
layout (triangle_strip, max_vertices = 100) out;

in float aspect_ratio_v[];
in uint digit_v[];
in float scale_v[];

void draw_horizontal_line(vec4 position, float aspect_ratio, float scale)
{
    float radius = 0.05 * scale;
    float angle = 0.0;
    int subsections = 2;
    float pi = 3.14159265359;
    float pi_2 = pi / 2;
    float inv_ar = 1 / aspect_ratio;
    float x = 0.2 * inv_ar * scale;
    float y = 0.05 * scale;

    gl_Position = position + vec4(-x, -y, 0.0, 0.0);    // 1:bottom-left
    EmitVertex();
    gl_Position = position + vec4( x, -y, 0.0, 0.0);    // 2:bottom-right
    EmitVertex();
    gl_Position = position + vec4(-x,  y, 0.0, 0.0);    // 3:top-left
    EmitVertex();
    gl_Position = position + vec4( x,  y, 0.0, 0.0);    // 4:top-right
    EmitVertex();
    vec4 temp_pos = position + vec4(x, 0.0, 0.0, 0.0);
    gl_Position = temp_pos;
    EmitVertex();

    for (int i = 0; i <= subsections; i++)
    {
        gl_Position = temp_pos + vec4(radius * cos(angle - pi_2) * inv_ar, radius * sin(angle - pi_2), 0.0, 0.0);
        EmitVertex();
        gl_Position = temp_pos;
        EmitVertex();
        angle += 3.14159265359 / subsections;
    }
    EndPrimitive();

    temp_pos = position + vec4(-x, 0.0, 0.0, 0.0);
    gl_Position = temp_pos;
    EmitVertex();

    angle = 0.0;
    for (int i = 0; i <= subsections; i++)
    {
        gl_Position = temp_pos + vec4(radius * cos(angle + pi_2) * inv_ar, radius * sin(angle + pi_2), 0.0, 0.0);
        EmitVertex();
        gl_Position = temp_pos;
        EmitVertex();
        angle += 3.14159265359 / subsections;
    }
    EndPrimitive();
}
void draw_vertical_line(vec4 position_, float aspect_ratio, float scale)
{
    float radius = 0.05 * scale;
    float angle = 0.0;
    int subsections = 2;
    float pi = 3.14159265359;
    float pi_2 = pi / 2;
    float inv_ar = 1 / aspect_ratio;
    float x = 0.05 * inv_ar * scale;
    float y = 0.2 * scale;

    gl_Position = position_ + vec4(-x, -y, 0.0, 0.0);    // 1:bottom-left
    EmitVertex();
    gl_Position = position_ + vec4( x, -y, 0.0, 0.0);    // 2:bottom-right
    EmitVertex();
    gl_Position = position_ + vec4(-x,  y, 0.0, 0.0);    // 3:top-left
    EmitVertex();
    gl_Position = position_ + vec4( x,  y, 0.0, 0.0);    // 4:top-right
    EmitVertex();
    vec4 temp_pos = position_ + vec4(0.0, y, 0.0, 0.0);
    gl_Position = temp_pos;
    EmitVertex();

    for (int i = 0; i <= subsections; i++)
    {
        gl_Position = temp_pos + vec4(radius * cos(angle) * inv_ar, radius * sin(angle), 0.0, 0.0);
        EmitVertex();
        gl_Position = temp_pos;
        EmitVertex();
        angle += 3.14159265359 / subsections;
    }
    EndPrimitive();

    temp_pos = position_ + vec4(0.0, -y, 0.0, 0.0);
    gl_Position = temp_pos;
    EmitVertex();

    angle = 0.0;
    for (int i = 0; i <= subsections; i++)
    {
        gl_Position = temp_pos + vec4(radius * cos(angle) * inv_ar, radius * sin(angle), 0.0, 0.0);
        EmitVertex();
        gl_Position = temp_pos;
        EmitVertex();
        angle -= 3.14159265359 / subsections;
    }
    EndPrimitive();
}

void display_0(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_1(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;

    vec4 temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_2(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x * 1.0, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x* 1.0, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x* 1.0, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_3(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_4(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);


    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_5(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_6(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_7(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;

    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_8(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_9(vec4 position, float aspect_ratio, float scale)
{
    float inv_ar = 1 / aspect_ratio;
    vec4 temp_pos = vec4(position.x, position.y + 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y - 0.4 * scale, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4(position.x, position.y, position.z, position.w);
    draw_horizontal_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x - 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y + 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);

    temp_pos = vec4((position.x + 0.2 * scale * inv_ar), position.y - 0.2*scale, position.z, position.w);
    draw_vertical_line(temp_pos, aspect_ratio, scale);
}

void display_digit(vec4 position, float aspect_ratio, uint digit, float scale)
{
    if (digit == 0u){
        display_0(position, aspect_ratio, scale);
    }
    else if (digit == 1u){
        display_1(position, aspect_ratio, scale);
    }
    else if (digit == 2u){
        display_2(position, aspect_ratio, scale);
    }
    else if (digit == 3u){
        display_3(position, aspect_ratio, scale);
    }
    else if (digit == 4u){
        display_4(position, aspect_ratio, scale);
    }
    else if (digit == 5u){
        display_5(position, aspect_ratio, scale);
    }
    else if (digit == 6u){
        display_6(position, aspect_ratio, scale);
    }
    else if (digit == 7u){
        display_7(position, aspect_ratio, scale);
    }
    else if (digit == 8u){
        display_8(position, aspect_ratio, scale);
    }
    else if (digit == 9u){
        display_9(position, aspect_ratio, scale);
    }
}

void main() {
    float ooo = 0.0;
    uint digit = digit_v[0];
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
