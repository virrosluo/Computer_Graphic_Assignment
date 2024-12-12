#version 330 core

uniform float maxDistance; // Maximum possible distance for normalization
uniform vec3 cameraPos;    // Position of the camera

in vec3 fragPos;           // Position of the fragment
in vec3 fragment_color;    // Color of the fragment
out vec4 FragColor;

void main() {
    float distance = length(fragPos - cameraPos);
    float intensity = clamp(distance / maxDistance, 0.0, 1.0); // Normalize
    FragColor = vec4(vec3(intensity), 1.0); // Heatmap: Red for close, fade to black
}
