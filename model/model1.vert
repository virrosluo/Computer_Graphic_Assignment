#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec2 texcoord;

uniform mat4 modelview;
uniform mat4 projection;

out vec3 fragColor;
out vec2 fragTexcoord;

void main() {
    fragColor = color;
    fragTexcoord = texcoord;
    gl_Position = projection * modelview * vec4(position, 1.0);
}
