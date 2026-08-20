#version 330 core
layout (location = 0) in vec2 aPos;

uniform vec2 screenSize;

void main()
{
    vec2 ndc = vec2(
        (aPos.x / screenSize.x) * 2.0 - 1.0,
        1.0 - (aPos.y / screenSize.y) * 2.0
    );
    gl_Position = vec4(ndc, 0.0, 1.0);
}
