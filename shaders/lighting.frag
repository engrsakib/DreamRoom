#version 330 core
struct DirLight
{
    vec3 direction;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct PointLight
{
    vec3 position;
    float constant;
    float linear;
    float quadratic;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct SpotLight
{
    vec3 position;
    vec3 direction;
    float cutOff;
    float outerCutOff;
    float constant;
    float linear;
    float quadratic;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct Surface
{
    vec3 color;
    float specular;
    float shininess;
};

in vec3 FragPos;
in vec3 Normal;
in vec4 FragPosMainLight;
in vec4 FragPosLampLight;

out vec4 FragColor;

uniform vec3 objectColor;
uniform vec3 viewPos;
uniform float specularStrength;
uniform float shininess;

uniform int useTiles;
uniform float tileSize;
uniform float groutWidth;
uniform float tileBevel;
uniform vec3 groutColor;

uniform sampler2D mainShadowMap;
uniform sampler2D lampShadowMap;

uniform DirLight dirLight;
uniform PointLight pointLight;
uniform PointLight lampLight;
uniform SpotLight spotLight;

// Derives tile coordinates from world position by projecting along the dominant
// surface axis, so no extra vertex attributes are needed.
void applyTiles(inout vec3 color, inout vec3 normal, inout float specular, inout float gloss)
{
    vec3 axis = abs(normal);
    vec2 uv;
    vec3 tangent;
    vec3 bitangent;

    if (axis.y >= axis.x && axis.y >= axis.z)
    {
        uv = FragPos.xz;
        tangent = vec3(1.0, 0.0, 0.0);
        bitangent = vec3(0.0, 0.0, 1.0);
    }
    else if (axis.x >= axis.z)
    {
        uv = FragPos.zy;
        tangent = vec3(0.0, 0.0, 1.0);
        bitangent = vec3(0.0, 1.0, 0.0);
    }
    else
    {
        uv = FragPos.xy;
        tangent = vec3(1.0, 0.0, 0.0);
        bitangent = vec3(0.0, 1.0, 0.0);
    }

    uv /= tileSize;
    vec2 cell = fract(uv) - 0.5;
    float edge = max(abs(cell.x), abs(cell.y));
    float grout = smoothstep(0.5 - groutWidth - 0.012, 0.5 - groutWidth, edge);

    float variation = fract(sin(dot(floor(uv), vec2(12.9898, 78.233))) * 43758.5453);
    vec3 faceColor = color * (0.94 + 0.12 * variation);

    color = mix(faceColor, groutColor, grout);
    specular = mix(specular, specular * 0.12, grout);
    gloss = mix(gloss, max(gloss * 0.25, 4.0), grout);
    normal = normalize(normal - (tangent * cell.x + bitangent * cell.y) * grout * tileBevel);
}

float shadowFactor(sampler2D shadowMap, vec4 fragPosLightSpace, vec3 normal, vec3 lightDir)
{
    if (fragPosLightSpace.w <= 0.0)
    {
        return 0.0;
    }

    vec3 projected = fragPosLightSpace.xyz / fragPosLightSpace.w;
    projected = projected * 0.5 + 0.5;

    if (projected.z > 1.0 || any(lessThan(projected.xy, vec2(0.0))) || any(greaterThan(projected.xy, vec2(1.0))))
    {
        return 0.0;
    }

    float bias = max(0.0040 * (1.0 - dot(normal, lightDir)), 0.0012);
    vec2 texelSize = 1.0 / vec2(textureSize(shadowMap, 0));
    float shadow = 0.0;

    for (int x = -1; x <= 1; ++x)
    {
        for (int y = -1; y <= 1; ++y)
        {
            float closest = texture(shadowMap, projected.xy + vec2(x, y) * texelSize).r;
            shadow += projected.z - bias > closest ? 1.0 : 0.0;
        }
    }

    return shadow / 9.0;
}

vec3 calculateDirectionalLight(DirLight light, vec3 normal, vec3 viewDir, Surface surface)
{
    vec3 lightDir = normalize(-light.direction);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), surface.shininess);

    vec3 ambient = light.ambient * surface.color;
    vec3 diffuse = light.diffuse * diff * surface.color;
    vec3 specular = light.specular * spec * vec3(surface.specular);
    return ambient + diffuse + specular;
}

vec3 calculatePointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir, Surface surface, float shadow)
{
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), surface.shininess);

    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * distance * distance);

    vec3 ambient = light.ambient * surface.color;
    vec3 diffuse = light.diffuse * diff * surface.color;
    vec3 specular = light.specular * spec * vec3(surface.specular);

    float visibility = 1.0 - shadow;
    ambient *= attenuation;
    diffuse *= attenuation * visibility;
    specular *= attenuation * visibility;
    return ambient + diffuse + specular;
}

vec3 calculateSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir, Surface surface)
{
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), surface.shininess);

    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * distance * distance);

    float theta = dot(lightDir, normalize(-light.direction));
    float epsilon = light.cutOff - light.outerCutOff;
    float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);

    vec3 ambient = light.ambient * surface.color;
    vec3 diffuse = light.diffuse * diff * surface.color;
    vec3 specular = light.specular * spec * vec3(surface.specular);

    ambient *= attenuation * intensity;
    diffuse *= attenuation * intensity;
    specular *= attenuation * intensity;
    return ambient + diffuse + specular;
}

void main()
{
    vec3 norm = normalize(Normal);
    vec3 surfaceColor = objectColor;
    float surfaceSpecular = specularStrength;
    float surfaceGloss = shininess;

    if (useTiles == 1)
    {
        applyTiles(surfaceColor, norm, surfaceSpecular, surfaceGloss);
    }

    Surface surface = Surface(surfaceColor, surfaceSpecular, surfaceGloss);
    vec3 viewDir = normalize(viewPos - FragPos);

    float mainShadow = shadowFactor(mainShadowMap, FragPosMainLight, norm, normalize(pointLight.position - FragPos));
    float lampShadow = shadowFactor(lampShadowMap, FragPosLampLight, norm, normalize(lampLight.position - FragPos));

    vec3 result = calculateDirectionalLight(dirLight, norm, viewDir, surface);
    result += calculatePointLight(pointLight, norm, FragPos, viewDir, surface, mainShadow);
    result += calculatePointLight(lampLight, norm, FragPos, viewDir, surface, lampShadow);
    result += calculateSpotLight(spotLight, norm, FragPos, viewDir, surface);

    FragColor = vec4(result, 1.0);
}
