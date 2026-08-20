import glfw
from OpenGL.GL import GL_RENDERER, GL_SHADING_LANGUAGE_VERSION, GL_VENDOR, GL_VERSION, glGetString
import numpy as np

from camera.camera import Camera
from config import settings
from core.input import InputManager
from core.window import Window
from lighting.directional_light import DirectionalLight
from lighting.point_light import PointLight
from lighting.spot_light import SpotLight
from objects.bed import Bed
from objects.lamp import Lamp
from objects.room import Room
from objects.table import Table
from rendering.mesh import Mesh
from rendering.renderer import Renderer
from scene.scene import Scene


def decode_gl_string(name):
    value = glGetString(name)
    if value is None:
        return "Unavailable"
    return value.decode("utf-8", errors="replace")


class Application:
    def __init__(self):
        self.show_triangle = False
        self.last_frame = 0.0

        glfw.set_error_callback(self._glfw_error_callback)
        if not glfw.init():
            print("Failed to initialize GLFW.")
            print("Make sure a desktop environment is available and GLFW can open a real window.")
            print("On WSL2, confirm WSLg is working. For software rendering, try LIBGL_ALWAYS_SOFTWARE=1.")
            raise RuntimeError("GLFW initialization failed.")

        self.window = Window().create()
        self.input = InputManager()
        self.input.attach(self.window.handle)
        self.camera = Camera()
        self.renderer = Renderer()
        self.cube_mesh = Mesh.create_cube()
        self.triangle_mesh = Mesh.create_triangle()
        self.scene = self._build_scene()

        self._print_banner()
        print("GL_VENDOR   :", decode_gl_string(GL_VENDOR))
        print("GL_RENDERER :", decode_gl_string(GL_RENDERER))
        print("GL_VERSION  :", decode_gl_string(GL_VERSION))
        print("GLSL        :", decode_gl_string(GL_SHADING_LANGUAGE_VERSION))

    def _build_scene(self):
        scene = Scene()
        scene.add(Room(self.cube_mesh))
        scene.add(Bed(self.cube_mesh))
        scene.add(Table(self.cube_mesh))

        scene.directional_light = DirectionalLight(
            settings.DIR_LIGHT_DIRECTION,
            settings.DIR_LIGHT_AMBIENT,
            settings.DIR_LIGHT_DIFFUSE,
            settings.DIR_LIGHT_SPECULAR,
        )
        scene.point_light = PointLight(
            settings.POINT_LIGHT_POSITION,
            *settings.POINT_LIGHT_ATTENUATION,
            settings.POINT_LIGHT_AMBIENT,
            settings.POINT_LIGHT_DIFFUSE,
            settings.POINT_LIGHT_SPECULAR,
        )
        scene.spot_light = SpotLight(
            tuple(float(v) for v in self.camera.position),
            tuple(float(v) for v in self.camera.front),
            settings.SPOT_LIGHT_CUTOFF,
            settings.SPOT_LIGHT_OUTER_CUTOFF,
            *settings.SPOT_LIGHT_ATTENUATION,
            settings.SPOT_LIGHT_AMBIENT,
            settings.SPOT_LIGHT_DIFFUSE,
            settings.SPOT_LIGHT_SPECULAR,
        )
        scene.lamp = Lamp(self.cube_mesh)
        return scene

    def run(self):
        while not self.window.should_close():
            current_frame = glfw.get_time()
            delta_time = current_frame - self.last_frame
            self.last_frame = current_frame

            self._process_input(delta_time)
            self.scene.update(delta_time)
            self.scene.spot_light.sync_from_camera(self.camera)
            self._render()

            self.window.swap_buffers()
            glfw.poll_events()
            self.input.end_frame()

        glfw.terminate()

    def _process_input(self, delta_time):
        if self.input.is_key_pressed(glfw.KEY_ESCAPE):
            self.window.set_should_close(True)

        if self.input.is_key_pressed(glfw.KEY_T):
            self.show_triangle = not self.show_triangle
            print(f"Mode: {'Hello Triangle' if self.show_triangle else 'Bedroom Scene'}")

        if self.input.is_key_down(glfw.KEY_W):
            self.camera.process_keyboard("FORWARD", delta_time)
        if self.input.is_key_down(glfw.KEY_S):
            self.camera.process_keyboard("BACKWARD", delta_time)
        if self.input.is_key_down(glfw.KEY_A):
            self.camera.process_keyboard("LEFT", delta_time)
        if self.input.is_key_down(glfw.KEY_D):
            self.camera.process_keyboard("RIGHT", delta_time)

        self._clamp_camera()

        if not self.show_triangle and self.input.is_mouse_button_pressed(glfw.MOUSE_BUTTON_LEFT):
            xpos, ypos = self.input.get_mouse_position(self.window.handle)
            self._handle_camera_button_click(xpos, ypos)

    def _render(self):
        self.renderer.clear()
        if self.show_triangle:
            self.renderer.render_triangle(self.triangle_mesh)
            return

        aspect_ratio = self.window.width / float(self.window.height)
        self.renderer.render_scene(self.scene, self.camera, aspect_ratio)
        self.renderer.render_camera_buttons(self._get_camera_button_rects(), (self.window.width, self.window.height))

    def _get_camera_button_rects(self):
        button_size = max(settings.BUTTON_MIN_SIZE, min(self.window.width, self.window.height) * settings.BUTTON_SIZE_RATIO)
        gap = button_size * settings.BUTTON_GAP_RATIO
        margin = button_size * settings.BUTTON_MARGIN_RATIO

        row_y = self.window.height - margin - button_size
        up_y = row_y - gap - button_size
        right_x = self.window.width - margin - button_size
        down_x = right_x - gap - button_size
        left_x = down_x - gap - button_size

        return {
            "UP": (down_x, up_y, button_size, button_size),
            "LEFT": (left_x, row_y, button_size, button_size),
            "DOWN": (down_x, row_y, button_size, button_size),
            "RIGHT": (right_x, row_y, button_size, button_size),
        }

    def _handle_camera_button_click(self, xpos, ypos):
        for name, rect in self._get_camera_button_rects().items():
            x, y, width, height = rect
            if not (x <= xpos <= x + width and y <= ypos <= y + height):
                continue

            if name == "UP":
                self.camera.process_look_step(pitch_offset=settings.CAMERA_LOOK_STEP)
            elif name == "DOWN":
                self.camera.process_look_step(pitch_offset=-settings.CAMERA_LOOK_STEP)
            elif name == "LEFT":
                self.camera.process_look_step(yaw_offset=-settings.CAMERA_LOOK_STEP)
            elif name == "RIGHT":
                self.camera.process_look_step(yaw_offset=settings.CAMERA_LOOK_STEP)
            break

    def _clamp_camera(self):
        self.camera.position[0] = np.clip(self.camera.position[0], -settings.CAMERA_CLAMP_XZ, settings.CAMERA_CLAMP_XZ)
        self.camera.position[1] = np.clip(self.camera.position[1], settings.CAMERA_CLAMP_Y_MIN, settings.CAMERA_CLAMP_Y_MAX)
        self.camera.position[2] = np.clip(self.camera.position[2], -settings.CAMERA_CLAMP_XZ, settings.CAMERA_CLAMP_XZ)

    def _print_banner(self):
        print(settings.WINDOW_TITLE)
        print("------------------------")
        print("Controls:")
        print("W A S D - Move")
        print("Mouse - Click Camera Buttons")
        print("On-screen UP/DOWN/LEFT/RIGHT - Look Around")
        print("ESC - Exit")
        print("T - Toggle Triangle Test")

    def _glfw_error_callback(self, error_code, description):
        if isinstance(description, bytes):
            description = description.decode("utf-8", errors="replace")
        print(f"GLFW error {error_code}: {description}")
