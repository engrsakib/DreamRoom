#version 330 core
out vec4 FragColor;

uniform vec3 uiColor;

void main()
{
    FragColor = vec4(uiColor, 1.0);
}
