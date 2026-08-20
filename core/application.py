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
from objects.chair import Chair
from objects.coffee_cup import CoffeeCup
from objects.glass_window import GlassWindow
from objects.lamp import Lamp
from objects.reading_table import ReadingTable
from objects.room import Room
from objects.table_lamp import TableLamp
from objects.tea_table import TeaTable
from rendering.mesh import Mesh
from rendering.renderer import Renderer
from scene.scene import Scene
from ui.camera_controller import CameraControllerUI

def decode_gl_string(name):
    value = glGetString(name)
    if value is None:
        return "Unavailable"
    return value.decode("utf-8", errors="replace")


class Application:
    def __init__(self):
        self.show_triangle = False
        self.last_frame = 0.0
        self.drag_start_position = None

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
        self.camera_controller = CameraControllerUI()
        self.renderer = Renderer()
        self.cube_mesh = Mesh.create_cube()
        self.cylinder_mesh = Mesh.create_cylinder()
        self.frustum_mesh = Mesh.create_frustum()
        self.triangle_mesh = Mesh.create_triangle()
        self.scene = self._build_scene()

        self._print_banner()
        print("GL_VENDOR   :", decode_gl_string(GL_VENDOR))
        print("GL_RENDERER :", decode_gl_string(GL_RENDERER))
        print("GL_VERSION  :", decode_gl_string(GL_VERSION))
        print("GLSL        :", decode_gl_string(GL_SHADING_LANGUAGE_VERSION))

    def _build_scene(self):
        scene = Scene()
        table_lamp = TableLamp(self.cylinder_mesh, self.frustum_mesh)
        glass_window = GlassWindow(self.cube_mesh)

        scene.add(Room(self.cube_mesh))
        scene.add(glass_window)
        scene.add(Bed(self.cube_mesh))
        scene.add(ReadingTable(self.cube_mesh))
        scene.add(Chair(self.cube_mesh))
        scene.add(table_lamp)
        scene.add(TeaTable(self.cube_mesh))
        scene.add(CoffeeCup(self.cube_mesh, self.cylinder_mesh))

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
        scene.lamp_light = PointLight(
            settings.LAMP_LIGHT_POSITION,
            *settings.LAMP_LIGHT_ATTENUATION,
            settings.LAMP_LIGHT_AMBIENT,
            settings.LAMP_LIGHT_DIFFUSE,
            settings.LAMP_LIGHT_SPECULAR,
        )
        scene.window_light = PointLight(
            settings.WINDOW_LIGHT_POSITION,
            *settings.WINDOW_LIGHT_ATTENUATION,
            settings.WINDOW_LIGHT_AMBIENT,
            settings.WINDOW_LIGHT_DIFFUSE,
            settings.WINDOW_LIGHT_SPECULAR,
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
        scene.lamp_fixture = table_lamp
        scene.add_emissive(Lamp(self.cylinder_mesh))
        scene.add_emissive(table_lamp.bulb)
        for panel in glass_window.exterior_panels:
            scene.add_emissive(panel)
        scene.add_transparent(glass_window.glass)
        return scene

    def run(self):
        while not self.window.should_close():
            glfw.poll_events()

            current_frame = glfw.get_time()
            delta_time = current_frame - self.last_frame
            self.last_frame = current_frame

            self._process_input(delta_time)
            self.scene.update(delta_time)
            self.scene.spot_light.sync_from_camera(self.camera)
            self._render()

            self.window.swap_buffers()
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

        if self.show_triangle:
            self.camera_controller.end_movement_drag()
            self.camera_controller.end_look()
            return

        xpos, ypos = self.input.get_mouse_position(self.window.handle)
        width, height = self.window.width, self.window.height
        left_down = self.input.is_mouse_button_down(glfw.MOUSE_BUTTON_LEFT)
        right_down = self.input.is_mouse_button_down(glfw.MOUSE_BUTTON_RIGHT)

        if self.input.is_mouse_button_pressed(glfw.MOUSE_BUTTON_LEFT):
            if self.camera_controller.begin_movement_drag(xpos, ypos, width, height):
                self.drag_start_position = self.camera.position.copy()
            else:
                action = self.camera_controller.hit_test_zoom_controls(xpos, ypos, width, height)
                if action is not None:
                    self._handle_zoom_action(action)
                else:
                    self.camera_controller.begin_look(xpos, ypos, width, height)

        # The right button looks from anywhere, including on top of the joystick.
        if self.input.is_mouse_button_pressed(glfw.MOUSE_BUTTON_RIGHT):
            self.camera_controller.begin_look(xpos, ypos, width, height, over_controls=True)

        if left_down and self.camera_controller.movement_active:
            joystick_x, joystick_y = self.camera_controller.update_movement_drag(xpos, ypos, width, height)
            if joystick_x != 0.0 or joystick_y != 0.0:
                self.camera.move_analog(joystick_x, joystick_y, delta_time)
                self._clamp_camera()

        if self.camera_controller.look_active:
            look_x, look_y = self.camera_controller.update_look(xpos, ypos)
            if look_x != 0.0 or look_y != 0.0:
                self.camera.process_mouse_movement(look_x, look_y)

        if self.input.is_mouse_button_released(glfw.MOUSE_BUTTON_LEFT):
            if self.camera_controller.movement_active and self.drag_start_position is not None:
                print(f"Joystick move: {self.drag_start_position} -> {self.camera.position}")
            self.drag_start_position = None
            self.camera_controller.end_movement_drag()

        if not left_down and not right_down:
            self.camera_controller.end_look()

    def _render(self):
        if self.show_triangle:
            self.renderer.clear()
            self.renderer.render_triangle(self.triangle_mesh)
            return

        self.renderer.render_shadow_maps(self.scene, (self.window.width, self.window.height))
        self.renderer.clear()

        aspect_ratio = self.window.width / float(self.window.height)
        self.renderer.render_scene(self.scene, self.camera, aspect_ratio)
        layout = self.camera_controller.get_layout(self.window.width, self.window.height)
        self.renderer.render_ui_elements(layout["elements"], (self.window.width, self.window.height))

    def _handle_zoom_action(self, action):
        old_zoom = self.camera.zoom
        if action == "ZOOM_IN":
            self.camera.adjust_zoom(-settings.CAMERA_ZOOM_STEP)
        elif action == "ZOOM_OUT":
            self.camera.adjust_zoom(settings.CAMERA_ZOOM_STEP)
        print(f"{action}: Zoom {old_zoom:.1f} -> {self.camera.zoom:.1f}")

    def _clamp_camera(self):
        self.camera.position[0] = np.clip(self.camera.position[0], -settings.CAMERA_CLAMP_XZ, settings.CAMERA_CLAMP_XZ)
        self.camera.position[1] = np.clip(self.camera.position[1], settings.CAMERA_CLAMP_Y_MIN, settings.CAMERA_CLAMP_Y_MAX)
        self.camera.position[2] = np.clip(self.camera.position[2], -settings.CAMERA_CLAMP_XZ, settings.CAMERA_CLAMP_XZ)

    def _print_banner(self):
        print(settings.WINDOW_TITLE)
        print("------------------------")
        print("Controls:")
        print("W A S D - Move")
        print("Left Drag Joystick - Walk Around")
        print("Left Drag Anywhere Else - Look Around (full 360)")
        print("Right Drag - Look Around (works over the joystick too)")
        print("[-] [+] - Zoom Out / Zoom In")
        print("ESC - Exit")
        print("T - Toggle Triangle Test")

    def _glfw_error_callback(self, error_code, description):
        if isinstance(description, bytes):
            description = description.decode("utf-8", errors="replace")
        print(f"GLFW error {error_code}: {description}")
