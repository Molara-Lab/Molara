#version 330 core

in vec2 v_texcoord;           // Interpolated texture coordinates
in vec3 v_light_dir;
in vec3 v_normal;
in vec3 v_fragment_position;

uniform sampler2D u_texture;  // The texture sampler
uniform vec3 camera_position;

layout (location = 0) out vec4 out_color;  // Color output
layout (location = 1) out vec4 out_normal;  // Normal output
layout (location = 2) out vec4 out_color_unshaded;  // Color output without shading

void main()
{
    vec3 normal = normalize(v_normal);
    vec3 light_dir = normalize(-v_light_dir);
    vec3 light_fragment_direction = normalize(light_dir - v_fragment_position);
    vec3 camera_fragment_direction = normalize(camera_position - v_fragment_position);
    vec3 halfway = normalize(light_fragment_direction + camera_fragment_direction);

    // Diffuse lighting
    float diff = max(dot(normal, light_dir), 0.0);

    // Sample the texture
    vec4 tex_color = texture(u_texture, v_texcoord);

    vec3 light_color = vec3(0.99, 0.99, 0.99);    // Light color

    vec3 red = vec3(1.0, 0.0, 0.0);

    vec3 result = tex_color.rgb * light_color;
    out_color = vec4(result, tex_color.a);        // Include texture alpha
    out_color = vec4(result * diff, 1.0);
    out_normal = vec4(normal, 1.0);
    out_color_unshaded = vec4(red * diff, 1.0);
}
