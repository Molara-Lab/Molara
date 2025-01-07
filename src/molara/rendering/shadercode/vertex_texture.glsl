#version 330 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec2 a_texcoord; // Texture coordinates
layout(location = 3) in mat4 a_model;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;
uniform vec3 light_direction;

out vec2 v_texcoord;          // Pass texture coordinates to the fragment shader
out vec3 v_normal;
out vec3 v_light_dir;
out vec3 v_fragment_position;

void main()
{
    vec3 fragment_position = vec3(a_model * vec4(a_position, 1.0));
    v_fragment_position = fragment_position;
    gl_Position = projection * view * vec4(fragment_position, 1.0);

    v_texcoord = a_texcoord;  // Pass texture coordinates
    v_light_dir = light_direction;
    v_normal = mat3(transpose(inverse(a_model))) * a_normal;
}
