#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

out vec3 FragPos;
out vec3 Normal;
out vec4 FragPosMainLight;
out vec4 FragPosLampLight;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 normalMatrix;
uniform mat4 mainLightSpaceMatrix;
uniform mat4 lampLightSpaceMatrix;

void main()
{
    vec4 worldPosition = model * vec4(aPos, 1.0);
    FragPos = worldPosition.xyz;
    Normal = mat3(normalMatrix) * aNormal;
    FragPosMainLight = mainLightSpaceMatrix * worldPosition;
    FragPosLampLight = lampLightSpaceMatrix * worldPosition;
    gl_Position = projection * view * worldPosition;
}
