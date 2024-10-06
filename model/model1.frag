#version 330 core
in vec3 fragColor;
in vec2 fragTexcoord;

uniform sampler2D textureSampler;

out vec4 finalColor;

void main() {
    vec4 texColor = texture(textureSampler, fragTexcoord);
    finalColor = texColor * vec4(fragColor, 1.0);
}
