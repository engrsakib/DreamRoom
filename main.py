import ctypes
import math
import sys

try:
    import glfw
    import numpy as np
    from OpenGL.GL import (
        GL_ARRAY_BUFFER,
        GL_COLOR_BUFFER_BIT,
        GL_DEPTH_BUFFER_BIT,
        GL_DEPTH_TEST,
        GL_DYNAMIC_DRAW,
        GL_FALSE,
        GL_FLOAT,
        GL_FRAGMENT_SHADER,
        GL_FRONT,
        GL_QUERY_RESULT,
        GL_RENDERER,
        GL_RGB,
        GL_SAMPLES_PASSED,
        GL_SHADING_LANGUAGE_VERSION,
        GL_STATIC_DRAW,
        GL_TRIANGLES,
        GL_UNSIGNED_BYTE,
        GL_VENDOR,
        GL_VERSION,
        glBindBuffer,
        glBindVertexArray,
        glBufferData,
        glClear,
        glClearColor,
        glDeleteBuffers,
        glDeleteQueries,
        glDeleteVertexArrays,
        glDrawArrays,
        glDisable,
        glEnable,
        glEnableVertexAttribArray,
        glBeginQuery,
        glEndQuery,
        glFinish,
        glGenBuffers,
        glGenQueries,
        glGenVertexArrays,
        glGetQueryObjectuiv,
        glGetString,
        glReadPixels,
        glReadBuffer,
        glVertexAttribPointer,
        glViewport,
    )
except ImportError as exc:
    print("Missing required package:", exc)
    print("Install the required packages with:")
    print("pip install PyOpenGL glfw numpy")
    raise SystemExit(1)

from camera import Camera
from shader import Shader


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "OpenGL Bedroom Lab Final"
ISOLATED_CUBE_TEST = False
ANGLE_STEP = 5.0

camera = Camera(position=(0.0, 2.0, 8.0))
window_width = WINDOW_WIDTH
window_height = WINDOW_HEIGHT
last_x = WINDOW_WIDTH / 2.0
last_y = WINDOW_HEIGHT / 2.0
first_mouse = True
show_triangle = False
frame_diagnostics_printed = False
frames_rendered = 0
last_samples_passed = None

POINT_LIGHT_POSITION = np.array([-3.0, 4.5, -2.0], dtype=np.float32)


TRIANGLE_VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

out vec3 vertexColor;

void main()
{
    gl_Position = vec4(aPos, 1.0);
    vertexColor = aColor;
}
"""


TRIANGLE_FRAGMENT_SHADER = """
#version 330 core
in vec3 vertexColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(vertexColor, 1.0);
}
"""


LIGHTING_VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

out vec3 FragPos;
out vec3 Normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 normalMatrix;

void main()
{
    vec4 worldPosition = model * vec4(aPos, 1.0);
    FragPos = worldPosition.xyz;
    Normal = mat3(normalMatrix) * aNormal;
    gl_Position = projection * view * worldPosition;
}
"""


LIGHTING_FRAGMENT_SHADER = """
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

in vec3 FragPos;
in vec3 Normal;

out vec4 FragColor;

uniform vec3 objectColor;
uniform vec3 viewPos;
uniform float specularStrength;
uniform float shininess;
uniform DirLight dirLight;
uniform PointLight pointLight;
uniform SpotLight spotLight;

vec3 calculateDirectionalLight(DirLight light, vec3 normal, vec3 viewDir, vec3 materialSpecular)
{
    vec3 lightDir = normalize(-light.direction);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);

    vec3 ambient = light.ambient * objectColor;
    vec3 diffuse = light.diffuse * diff * objectColor;
    vec3 specular = light.specular * spec * materialSpecular;
    return ambient + diffuse + specular;
}

vec3 calculatePointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir, vec3 materialSpecular)
{
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);

    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * distance * distance);

    vec3 ambient = light.ambient * objectColor;
    vec3 diffuse = light.diffuse * diff * objectColor;
    vec3 specular = light.specular * spec * materialSpecular;

    ambient *= attenuation;
    diffuse *= attenuation;
    specular *= attenuation;
    return ambient + diffuse + specular;
}

vec3 calculateSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir, vec3 materialSpecular)
{
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);

    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * distance * distance);

    float theta = dot(lightDir, normalize(-light.direction));
    float epsilon = light.cutOff - light.outerCutOff;
    float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);

    vec3 ambient = light.ambient * objectColor;
    vec3 diffuse = light.diffuse * diff * objectColor;
    vec3 specular = light.specular * spec * materialSpecular;

    ambient *= attenuation * intensity;
    diffuse *= attenuation * intensity;
    specular *= attenuation * intensity;
    return ambient + diffuse + specular;
}

void main()
{
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 materialSpecular = vec3(specularStrength);

    vec3 result = calculateDirectionalLight(dirLight, norm, viewDir, materialSpecular);
    result += calculatePointLight(pointLight, norm, FragPos, viewDir, materialSpecular);
    result += calculateSpotLight(spotLight, norm, FragPos, viewDir, materialSpecular);

    FragColor = vec4(result, 1.0);
}
"""


LIGHT_CUBE_VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
}
"""


LIGHT_CUBE_FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(1.0);
}
"""


DEBUG_CUBE_FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(0.7, 0.4, 0.2, 1.0);
}
"""


UI_VERTEX_SHADER = """
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
"""


UI_FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

uniform vec3 uiColor;

void main()
{
    FragColor = vec4(uiColor, 1.0);
}
"""


TRIANGLE_VERTICES = np.array(
    [
        -0.6,
        -0.4,
        0.0,
        1.0,
        0.2,
        0.2,
        0.6,
        -0.4,
        0.0,
        0.2,
        1.0,
        0.2,
        0.0,
        0.6,
        0.0,
        0.2,
        0.4,
        1.0,
    ],
    dtype=np.float32,
)


CUBE_VERTICES = np.array(
    [
        -0.5, -0.5, -0.5, 0.0, 0.0, -1.0,
        0.5, 0.5, -0.5, 0.0, 0.0, -1.0,
        0.5, -0.5, -0.5, 0.0, 0.0, -1.0,
        0.5, 0.5, -0.5, 0.0, 0.0, -1.0,
        -0.5, -0.5, -0.5, 0.0, 0.0, -1.0,
        -0.5, 0.5, -0.5, 0.0, 0.0, -1.0,

        -0.5, -0.5, 0.5, 0.0, 0.0, 1.0,
        0.5, -0.5, 0.5, 0.0, 0.0, 1.0,
        0.5, 0.5, 0.5, 0.0, 0.0, 1.0,
        0.5, 0.5, 0.5, 0.0, 0.0, 1.0,
        -0.5, 0.5, 0.5, 0.0, 0.0, 1.0,
        -0.5, -0.5, 0.5, 0.0, 0.0, 1.0,

        -0.5, 0.5, 0.5, -1.0, 0.0, 0.0,
        -0.5, 0.5, -0.5, -1.0, 0.0, 0.0,
        -0.5, -0.5, -0.5, -1.0, 0.0, 0.0,
        -0.5, -0.5, -0.5, -1.0, 0.0, 0.0,
        -0.5, -0.5, 0.5, -1.0, 0.0, 0.0,
        -0.5, 0.5, 0.5, -1.0, 0.0, 0.0,

        0.5, 0.5, 0.5, 1.0, 0.0, 0.0,
        0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
        0.5, 0.5, -0.5, 1.0, 0.0, 0.0,
        0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
        0.5, 0.5, 0.5, 1.0, 0.0, 0.0,
        0.5, -0.5, 0.5, 1.0, 0.0, 0.0,

        -0.5, -0.5, -0.5, 0.0, -1.0, 0.0,
        0.5, -0.5, -0.5, 0.0, -1.0, 0.0,
        0.5, -0.5, 0.5, 0.0, -1.0, 0.0,
        0.5, -0.5, 0.5, 0.0, -1.0, 0.0,
        -0.5, -0.5, 0.5, 0.0, -1.0, 0.0,
        -0.5, -0.5, -0.5, 0.0, -1.0, 0.0,

        -0.5, 0.5, -0.5, 0.0, 1.0, 0.0,
        0.5, 0.5, 0.5, 0.0, 1.0, 0.0,
        0.5, 0.5, -0.5, 0.0, 1.0, 0.0,
        0.5, 0.5, 0.5, 0.0, 1.0, 0.0,
        -0.5, 0.5, -0.5, 0.0, 1.0, 0.0,
        -0.5, 0.5, 0.5, 0.0, 1.0, 0.0,
    ],
    dtype=np.float32,
)


def print_banner():
    print(WINDOW_TITLE)
    print("------------------------")
    print("Controls:")
    print("W A S D - Move")
    print("Mouse - Click Camera Buttons")
    print("On-screen UP/DOWN/LEFT/RIGHT - Look Around")
    print("ESC - Exit")
    print("T - Toggle Triangle Test")


def decode_gl_string(name):
    value = glGetString(name)
    if value is None:
        return "Unavailable"
    return value.decode("utf-8", errors="replace")


def glfw_error_callback(error_code, description):
    if isinstance(description, bytes):
        description = description.decode("utf-8", errors="replace")
    print(f"GLFW error {error_code}: {description}")


def framebuffer_size_callback(window, width, height):
    global window_width, window_height
    window_width = max(width, 1)
    window_height = max(height, 1)
    glViewport(0, 0, window_width, window_height)


def get_camera_button_rects():
    button_size = max(58.0, min(window_width, window_height) * 0.10)
    gap = button_size * 0.18
    margin = button_size * 0.30

    row_y = window_height - margin - button_size
    up_y = row_y - gap - button_size
    right_x = window_width - margin - button_size
    down_x = right_x - gap - button_size
    left_x = down_x - gap - button_size

    return {
        "UP": (down_x, up_y, button_size, button_size),
        "LEFT": (left_x, row_y, button_size, button_size),
        "DOWN": (down_x, row_y, button_size, button_size),
        "RIGHT": (right_x, row_y, button_size, button_size),
    }


def point_in_rect(xpos, ypos, rect):
    x, y, width, height = rect
    return x <= xpos <= x + width and y <= ypos <= y + height


def handle_camera_button_click(xpos, ypos):
    if show_triangle:
        return None

    button_rects = get_camera_button_rects()
    for name, rect in button_rects.items():
        if not point_in_rect(xpos, ypos, rect):
            continue

        if name == "UP":
            camera.process_look_step(pitch_offset=ANGLE_STEP)
        elif name == "DOWN":
            camera.process_look_step(pitch_offset=-ANGLE_STEP)
        elif name == "LEFT":
            camera.process_look_step(yaw_offset=-ANGLE_STEP)
        elif name == "RIGHT":
            camera.process_look_step(yaw_offset=ANGLE_STEP)

        print(f"Camera look: {name}")
        return name

    return None


def mouse_button_callback(window, button, action, mods):
    if button != glfw.MOUSE_BUTTON_LEFT or action != glfw.PRESS:
        return

    xpos, ypos = glfw.get_cursor_pos(window)
    handle_camera_button_click(xpos, ypos)


def key_callback(window, key, scancode, action, mods):
    global show_triangle

    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if key == glfw.KEY_T and action == glfw.PRESS:
        show_triangle = not show_triangle
        mode_name = "Hello Triangle" if show_triangle else "Bedroom Scene"
        print(f"Mode: {mode_name}")


def create_window(core_profile=True):
    glfw.default_window_hints()
    glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)

    if core_profile:
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        if sys.platform == "darwin":
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

    return glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, None, None)


def normalize(vector):
    vector = np.array(vector, dtype=np.float32)
    length = np.linalg.norm(vector)
    if length == 0.0:
        return vector
    return vector / length


def identity():
    return np.identity(4, dtype=np.float32)


def perspective(fov_degrees, aspect_ratio, near_plane, far_plane):
    f = 1.0 / math.tan(math.radians(fov_degrees) / 2.0)
    matrix = np.zeros((4, 4), dtype=np.float32)
    matrix[0, 0] = f / aspect_ratio
    matrix[1, 1] = f
    matrix[2, 2] = (far_plane + near_plane) / (near_plane - far_plane)
    matrix[2, 3] = (2.0 * far_plane * near_plane) / (near_plane - far_plane)
    matrix[3, 2] = -1.0
    return matrix


def translate(matrix, offset):
    tx, ty, tz = offset
    translation = identity()
    translation[0, 3] = tx
    translation[1, 3] = ty
    translation[2, 3] = tz
    return matrix @ translation


def scale(matrix, size):
    sx, sy, sz = size
    scaling = identity()
    scaling[0, 0] = sx
    scaling[1, 1] = sy
    scaling[2, 2] = sz
    return matrix @ scaling


def build_model_matrix(position, size):
    model = identity()
    model = translate(model, position)
    model = scale(model, size)
    return model


def build_normal_matrix(model_matrix):
    normal_matrix = identity()
    normal_matrix[0:3, 0:3] = np.linalg.inv(model_matrix[0:3, 0:3]).T
    return normal_matrix.astype(np.float32)


def setup_triangle_geometry():
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, TRIANGLE_VERTICES.nbytes, TRIANGLE_VERTICES, GL_STATIC_DRAW)

    stride = 6 * TRIANGLE_VERTICES.itemsize
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * TRIANGLE_VERTICES.itemsize))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return vao, vbo


def setup_cube_geometry():
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, CUBE_VERTICES.nbytes, CUBE_VERTICES, GL_STATIC_DRAW)

    stride = 6 * CUBE_VERTICES.itemsize
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * CUBE_VERTICES.itemsize))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return vao, vbo


def setup_ui_geometry():
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, 0, None, GL_DYNAMIC_DRAW)

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * np.dtype(np.float32).itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return vao, vbo


def build_rect_vertices(x, y, width, height):
    return [
        x, y,
        x + width, y,
        x + width, y + height,
        x, y,
        x + width, y + height,
        x, y + height,
    ]


def build_arrow_vertices(direction, rect):
    x, y, width, height = rect
    center_x = x + width * 0.5
    center_y = y + height * 0.5

    if direction == "UP":
        points = [
            (center_x, y + height * 0.24),
            (x + width * 0.28, y + height * 0.64),
            (x + width * 0.72, y + height * 0.64),
        ]
    elif direction == "DOWN":
        points = [
            (center_x, y + height * 0.76),
            (x + width * 0.28, y + height * 0.36),
            (x + width * 0.72, y + height * 0.36),
        ]
    elif direction == "LEFT":
        points = [
            (x + width * 0.24, center_y),
            (x + width * 0.64, y + height * 0.28),
            (x + width * 0.64, y + height * 0.72),
        ]
    else:
        points = [
            (x + width * 0.76, center_y),
            (x + width * 0.36, y + height * 0.28),
            (x + width * 0.36, y + height * 0.72),
        ]

    vertices = []
    for px, py in points:
        vertices.extend([px, py])
    return vertices


def draw_ui_shape(shader, ui_vao, ui_vbo, vertices, color):
    vertex_data = np.array(vertices, dtype=np.float32)

    shader.use()
    shader.set_vec2("screenSize", (window_width, window_height))
    shader.set_vec3("uiColor", color)

    glBindVertexArray(ui_vao)
    glBindBuffer(GL_ARRAY_BUFFER, ui_vbo)
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_DYNAMIC_DRAW)
    glDrawArrays(GL_TRIANGLES, 0, len(vertex_data) // 2)


def render_camera_buttons(ui_shader, ui_vao, ui_vbo):
    button_rects = get_camera_button_rects()
    border_color = (0.10, 0.10, 0.12)
    fill_color = (0.22, 0.30, 0.42)
    arrow_color = (0.92, 0.94, 0.98)

    glDisable(GL_DEPTH_TEST)

    for name, rect in button_rects.items():
        x, y, width, height = rect
        outer_vertices = build_rect_vertices(x, y, width, height)
        inner_vertices = build_rect_vertices(x + 4.0, y + 4.0, width - 8.0, height - 8.0)
        arrow_vertices = build_arrow_vertices(name, rect)

        draw_ui_shape(ui_shader, ui_vao, ui_vbo, outer_vertices, border_color)
        draw_ui_shape(ui_shader, ui_vao, ui_vbo, inner_vertices, fill_color)
        draw_ui_shape(ui_shader, ui_vao, ui_vbo, arrow_vertices, arrow_color)

    glEnable(GL_DEPTH_TEST)


def clamp_camera_position():
    if ISOLATED_CUBE_TEST:
        return
    camera.position[0] = np.clip(camera.position[0], -7.3, 7.3)
    camera.position[1] = np.clip(camera.position[1], 0.5, 5.5)
    camera.position[2] = np.clip(camera.position[2], -7.3, 7.3)


def process_input(window, delta_time):
    if ISOLATED_CUBE_TEST:
        return
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera.process_keyboard("FORWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera.process_keyboard("BACKWARD", delta_time)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.process_keyboard("LEFT", delta_time)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.process_keyboard("RIGHT", delta_time)

    clamp_camera_position()


def draw_cube(shader, cube_vao, position, size, color, specular=0.3, shininess=32.0):
    model = build_model_matrix(position, size)
    normal_matrix = build_normal_matrix(model)

    shader.set_mat4("model", model)
    shader.set_mat4("normalMatrix", normal_matrix)
    shader.set_vec3("objectColor", color)
    shader.set_float("specularStrength", specular)
    shader.set_float("shininess", shininess)

    glBindVertexArray(cube_vao)
    glDrawArrays(GL_TRIANGLES, 0, 36)


def render_triangle(shader, triangle_vao):
    shader.use()
    glBindVertexArray(triangle_vao)
    glDrawArrays(GL_TRIANGLES, 0, 3)


def set_lighting_uniforms(shader):
    shader.use()
    shader.set_vec3("viewPos", camera.position)

    shader.set_vec3("dirLight.direction", (-0.2, -1.0, -0.3))
    shader.set_vec3("dirLight.ambient", (0.15, 0.15, 0.15))
    shader.set_vec3("dirLight.diffuse", (0.35, 0.35, 0.35))
    shader.set_vec3("dirLight.specular", (0.45, 0.45, 0.45))

    shader.set_vec3("pointLight.position", POINT_LIGHT_POSITION)
    shader.set_float("pointLight.constant", 1.0)
    shader.set_float("pointLight.linear", 0.09)
    shader.set_float("pointLight.quadratic", 0.032)
    shader.set_vec3("pointLight.ambient", (0.2, 0.16, 0.14))
    shader.set_vec3("pointLight.diffuse", (0.9, 0.78, 0.68))
    shader.set_vec3("pointLight.specular", (1.0, 0.95, 0.85))

    shader.set_vec3("spotLight.position", camera.position)
    shader.set_vec3("spotLight.direction", camera.front)
    shader.set_float("spotLight.cutOff", math.cos(math.radians(12.5)))
    shader.set_float("spotLight.outerCutOff", math.cos(math.radians(17.5)))
    shader.set_float("spotLight.constant", 1.0)
    shader.set_float("spotLight.linear", 0.09)
    shader.set_float("spotLight.quadratic", 0.032)
    shader.set_vec3("spotLight.ambient", (0.0, 0.0, 0.0))
    shader.set_vec3("spotLight.diffuse", (0.9, 0.9, 0.85))
    shader.set_vec3("spotLight.specular", (1.0, 1.0, 0.95))


def render_bedroom(lighting_shader, light_cube_shader, cube_vao):
    aspect_ratio = window_width / float(window_height)
    projection = perspective(camera.zoom, aspect_ratio, 0.1, 100.0)
    view = camera.get_view_matrix()

    lighting_shader.use()
    lighting_shader.set_mat4("projection", projection)
    lighting_shader.set_mat4("view", view)
    set_lighting_uniforms(lighting_shader)

    floor_color = (0.45, 0.30, 0.18)
    wall_color = (0.78, 0.78, 0.82)
    bed_frame_color = (0.30, 0.17, 0.10)
    mattress_color = (0.90, 0.90, 0.86)
    pillow_color = (0.72, 0.82, 0.92)
    table_color = (0.62, 0.45, 0.26)

    draw_cube(lighting_shader, cube_vao, (0.0, -0.05, 0.0), (16.0, 0.1, 16.0), floor_color, specular=0.15, shininess=8.0)
    draw_cube(lighting_shader, cube_vao, (0.0, 3.0, -8.0), (16.0, 6.0, 0.2), wall_color, specular=0.1, shininess=8.0)
    draw_cube(lighting_shader, cube_vao, (-8.0, 3.0, 0.0), (0.2, 6.0, 16.0), wall_color, specular=0.1, shininess=8.0)
    draw_cube(lighting_shader, cube_vao, (8.0, 3.0, 0.0), (0.2, 6.0, 16.0), wall_color, specular=0.1, shininess=8.0)

    draw_cube(lighting_shader, cube_vao, (-4.8, 0.55, -5.0), (3.6, 0.6, 5.0), bed_frame_color, specular=0.22, shininess=18.0)
    draw_cube(lighting_shader, cube_vao, (-4.8, 1.05, -5.0), (3.2, 0.45, 4.4), mattress_color, specular=0.2, shininess=20.0)
    draw_cube(lighting_shader, cube_vao, (-4.8, 1.65, -7.1), (3.4, 1.5, 0.25), bed_frame_color, specular=0.22, shininess=18.0)
    draw_cube(lighting_shader, cube_vao, (-4.8, 1.45, -6.2), (1.5, 0.25, 1.2), pillow_color, specular=0.25, shininess=24.0)

    draw_cube(lighting_shader, cube_vao, (4.7, 1.30, -1.5), (2.2, 0.2, 1.3), table_color, specular=0.24, shininess=24.0)
    draw_cube(lighting_shader, cube_vao, (3.8, 0.65, -0.95), (0.18, 1.1, 0.18), table_color, specular=0.24, shininess=24.0)
    draw_cube(lighting_shader, cube_vao, (5.6, 0.65, -0.95), (0.18, 1.1, 0.18), table_color, specular=0.24, shininess=24.0)
    draw_cube(lighting_shader, cube_vao, (3.8, 0.65, -2.05), (0.18, 1.1, 0.18), table_color, specular=0.24, shininess=24.0)
    draw_cube(lighting_shader, cube_vao, (5.6, 0.65, -2.05), (0.18, 1.1, 0.18), table_color, specular=0.24, shininess=24.0)

    light_cube_shader.use()
    light_cube_shader.set_mat4("projection", projection)
    light_cube_shader.set_mat4("view", view)
    light_cube_shader.set_mat4("model", build_model_matrix(POINT_LIGHT_POSITION, (0.3, 0.3, 0.3)))
    glBindVertexArray(cube_vao)
    glDrawArrays(GL_TRIANGLES, 0, 36)


def render_isolated_cube(cube_shader, cube_vao):
    aspect_ratio = window_width / float(window_height)
    projection = perspective(camera.zoom, aspect_ratio, 0.1, 100.0)
    view = camera.get_view_matrix()
    model = build_model_matrix((0.0, 0.0, 0.0), (2.0, 2.0, 2.0))

    cube_shader.use()
    cube_shader.set_mat4("projection", projection)
    cube_shader.set_mat4("view", view)
    cube_shader.set_mat4("model", model)
    glBindVertexArray(cube_vao)
    query = int(np.asarray(glGenQueries(1)).item())
    glBeginQuery(GL_SAMPLES_PASSED, query)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    glEndQuery(GL_SAMPLES_PASSED)
    samples_passed = glGetQueryObjectuiv(query, GL_QUERY_RESULT)
    glDeleteQueries(1, [query])
    return int(samples_passed)


def print_isolated_cube_diagnostics():
    model = build_model_matrix((0.0, 0.0, 0.0), (2.0, 2.0, 2.0))
    view = camera.get_view_matrix()
    projection = perspective(45.0, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100.0)
    cube_vertices = CUBE_VERTICES.reshape(-1, 6)

    print("Diagnostic Mode: Isolated Cube")
    print("Camera position:", camera.position)
    print("Camera front   :", camera.front)
    print("Model matrix:\n", model)
    print("View matrix:\n", view)
    print("Projection matrix:\n", projection)
    print("Cube vertex count:", len(cube_vertices))
    print("Cube stride bytes:", 6 * CUBE_VERTICES.itemsize)
    print("Normal offset bytes:", 3 * CUBE_VERTICES.itemsize)
    print("First 4 cube vertices:")
    for index, vertex in enumerate(cube_vertices[:4]):
        print(f"  v{index}: {vertex}")


def print_frame_diagnostics_once(window):
    global frame_diagnostics_printed, frames_rendered, last_samples_passed

    if not ISOLATED_CUBE_TEST or show_triangle or frame_diagnostics_printed:
        return

    if frames_rendered < 3:
        return

    glFinish()
    glReadBuffer(GL_FRONT)

    background_rgb = np.array([20, 20, 26], dtype=np.int16)
    pixel_bytes = glReadPixels(0, 0, window_width, window_height, GL_RGB, GL_UNSIGNED_BYTE)
    pixel_array = np.frombuffer(pixel_bytes, dtype=np.uint8).reshape((window_height, window_width, 3))
    difference = np.abs(pixel_array.astype(np.int16) - background_rgb)
    visible_mask = np.any(difference > 12, axis=2)
    visible_pixels = int(np.count_nonzero(visible_mask))
    total_pixels = window_width * window_height

    print("Frame diagnostics:")
    print(f"  Occlusion query samples passed: {last_samples_passed}")
    print(f"  Visible non-background pixels: {visible_pixels} / {total_pixels}")

    if visible_pixels > 0:
        ys, xs = np.where(visible_mask)
        print(f"  Bounding box: x=[{xs.min()}, {xs.max()}], y=[{ys.min()}, {ys.max()}]")
        print(f"  Screen coverage: {visible_pixels / total_pixels:.4f}")
    else:
        print("  Bounding box: none")
        print("  Screen coverage: 0.0000")

    frame_diagnostics_printed = True
    glfw.set_window_should_close(window, True)


def cleanup(vertex_arrays, buffers):
    if vertex_arrays:
        glDeleteVertexArrays(len(vertex_arrays), vertex_arrays)
    if buffers:
        glDeleteBuffers(len(buffers), buffers)


def main():
    global frames_rendered, last_samples_passed
    glfw.set_error_callback(glfw_error_callback)

    if not glfw.init():
        print("Failed to initialize GLFW.")
        print("Make sure a desktop environment is available and GLFW can open a real window.")
        print("On WSL2, confirm WSLg is working. For software rendering, try LIBGL_ALWAYS_SOFTWARE=1.")
        return 1

    window = create_window(core_profile=True)
    if window is None:
        print("OpenGL 3.3 Core window creation failed. Retrying with default context hints...")
        window = create_window(core_profile=False)

    if window is None:
        print("Failed to create an OpenGL context and window.")
        print("Check your driver, WSLg setup, or software rendering support.")
        print("If needed in WSL2, try: LIBGL_ALWAYS_SOFTWARE=1 python3 main.py")
        glfw.terminate()
        return 1

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glEnable(GL_DEPTH_TEST)

    print_banner()
    print("GL_VENDOR   :", decode_gl_string(GL_VENDOR))
    print("GL_RENDERER :", decode_gl_string(GL_RENDERER))
    print("GL_VERSION  :", decode_gl_string(GL_VERSION))
    print("GLSL        :", decode_gl_string(GL_SHADING_LANGUAGE_VERSION))

    try:
        triangle_shader = Shader(TRIANGLE_VERTEX_SHADER, TRIANGLE_FRAGMENT_SHADER)
        ui_shader = Shader(UI_VERTEX_SHADER, UI_FRAGMENT_SHADER)
        if ISOLATED_CUBE_TEST:
            cube_shader = Shader(LIGHT_CUBE_VERTEX_SHADER, DEBUG_CUBE_FRAGMENT_SHADER)
            lighting_shader = None
            light_cube_shader = None
        else:
            cube_shader = None
            lighting_shader = Shader(LIGHTING_VERTEX_SHADER, LIGHTING_FRAGMENT_SHADER)
            light_cube_shader = Shader(LIGHT_CUBE_VERTEX_SHADER, LIGHT_CUBE_FRAGMENT_SHADER)
    except RuntimeError:
        glfw.terminate()
        return 1

    triangle_vao, triangle_vbo = setup_triangle_geometry()
    cube_vao, cube_vbo = setup_cube_geometry()
    ui_vao, ui_vbo = setup_ui_geometry()

    if ISOLATED_CUBE_TEST:
        print_isolated_cube_diagnostics()

    last_frame = 0.0

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        process_input(window, delta_time)

        glClearColor(0.08, 0.08, 0.10, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if show_triangle:
            render_triangle(triangle_shader, triangle_vao)
        elif ISOLATED_CUBE_TEST:
            last_samples_passed = render_isolated_cube(cube_shader, cube_vao)
        else:
            render_bedroom(lighting_shader, light_cube_shader, cube_vao)
            render_camera_buttons(ui_shader, ui_vao, ui_vbo)

        glfw.swap_buffers(window)
        if ISOLATED_CUBE_TEST:
            frames_rendered += 1
            print_frame_diagnostics_once(window)
        glfw.poll_events()

    cleanup([triangle_vao, cube_vao, ui_vao], [triangle_vbo, cube_vbo, ui_vbo])
    glfw.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
