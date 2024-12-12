# version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;

uniform mat4 projection, modelview;

out vec3 fragment_color;
out vec3 fragPos;

void main()
{
    fragment_color = color;
    gl_Position = projection * modelview * vec4(position, 1.0);
    fragPos = position;
}