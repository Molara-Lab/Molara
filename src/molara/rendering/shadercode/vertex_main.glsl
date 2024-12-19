#version 330 core

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