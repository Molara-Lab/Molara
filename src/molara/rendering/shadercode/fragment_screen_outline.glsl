// shader adapted from https://github.com/OmarShehata/webgl-outlines/blob/main/threejs/src/CustomOutlinePass.js
#version 330 core
out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D screenTexture;
uniform sampler2D depthTexture;
uniform sampler2D normalTexture;
uniform sampler2D screenUnshadedTexture;

vec2 pixelSize = vec2(1.0 / textureSize(screenTexture, 0).x, 1.0 / textureSize(screenTexture, 0).y);

const float zNear = 0.1;
const float zFar = 720.0;

float saturateValue(float num) {
    return clamp(num, 0.0, 1.0);
}

float LinearizeDepth(float depth)
{
    float z = depth * 2.0 - 1.0; // Back to NDC
    return (2.0 * zNear * zFar) / (zFar + zNear - z * (zFar - zNear)); // Linearize the depth value
}

float readDepth(sampler2D depthSampler, vec2 coord) {
    float depth = texture(depthSampler, coord).r;
    return LinearizeDepth(depth);
}

float getPixelDepth(int x, int y) {
    return readDepth(depthTexture, TexCoords + pixelSize.xy * vec2(x, y));
}

vec3 getSurfaceValue(int x, int y) {
    vec3 val = texture(screenUnshadedTexture, TexCoords + pixelSize.xy * vec2(x, y)).rgb;
    return val;
}

float getSufaceIdDiff(vec3 surfaceValue) {
    float surfaceIdDiff = 0.0;
    surfaceIdDiff += distance(surfaceValue, getSurfaceValue(1, 0));
    surfaceIdDiff += distance(surfaceValue, getSurfaceValue(0, 1));
    surfaceIdDiff += distance(surfaceValue, getSurfaceValue(0, 1));
    surfaceIdDiff += distance(surfaceValue, getSurfaceValue(0, -1));

    surfaceIdDiff += distance(surfaceValue, getSurfaceValue(1, 1));
    surfaceIdDiff += distance(surfaceValue, getSurfaceValue(1, -1));
    surfaceIdDiff += distance(surfaceValue, getSurfaceValue(-1, 1));
    surfaceIdDiff += distance(surfaceValue, getSurfaceValue(-1, -1));
    return surfaceIdDiff;
}

void main() {
    vec4 sceneColor = texture(screenTexture, TexCoords);
    // "surfaceValue" is the unshaded color
    vec3 surfaceValue = getSurfaceValue(0, 0);

    // Get the difference between surface values of neighboring pixels
    // and current
    float surfaceValueDiff = getSufaceIdDiff(surfaceValue);

    if (surfaceValueDiff != 0.0) surfaceValueDiff = 1.0;

    float outline = saturateValue(surfaceValueDiff);

    vec3 color = vec3(0.0, 0.0, 0.0);

    // Combine outline with scene color.
    vec4 outlineColor = vec4(color, 1.0);
    FragColor = vec4(mix(sceneColor, outlineColor, outline));
}