import math

import numpy as np

from config import settings


def _normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0.0:
        return vector.astype(np.float32)
    return (vector / norm).astype(np.float32)


class Camera:
    def __init__(
        self,
        position=settings.CAMERA_START_POSITION,
        up=settings.CAMERA_WORLD_UP,
        yaw=settings.CAMERA_YAW,
        pitch=settings.CAMERA_PITCH,
        movement_speed=settings.CAMERA_SPEED,
        mouse_sensitivity=settings.CAMERA_MOUSE_SENSITIVITY,
        zoom=settings.CAMERA_ZOOM,
    ):
        self.position = np.array(position, dtype=np.float32)
        self.world_up = np.array(up, dtype=np.float32)
        self.yaw = float(yaw)
        self.pitch = float(pitch)
        self.movement_speed = float(movement_speed)
        self.mouse_sensitivity = float(mouse_sensitivity)
        self.zoom = float(zoom)

        self.front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.right = np.array([1.0, 0.0, 0.0], dtype=np.float32)

        self._update_camera_vectors()

    def get_view_matrix(self):
        return self._look_at(self.position, self.position + self.front, self.up)

    def process_keyboard(self, direction, delta_time):
        if direction == "FORWARD":
            self.move_analog(0.0, 1.0, delta_time)
        elif direction == "BACKWARD":
            self.move_analog(0.0, -1.0, delta_time)
        elif direction == "LEFT":
            self.move_analog(-1.0, 0.0, delta_time)
        elif direction == "RIGHT":
            self.move_analog(1.0, 0.0, delta_time)

    def move_analog(self, joystick_x, joystick_y, delta_time):
        horizontal_front = np.array([self.front[0], 0.0, self.front[2]], dtype=np.float32)
        horizontal_right = np.array([self.right[0], 0.0, self.right[2]], dtype=np.float32)

        horizontal_front = _normalize(horizontal_front)
        horizontal_right = _normalize(horizontal_right)

        movement = horizontal_right * joystick_x + horizontal_front * joystick_y
        magnitude = min(1.0, float(np.linalg.norm([joystick_x, joystick_y])))

        if np.linalg.norm(movement) == 0.0 or magnitude == 0.0:
            return

        movement = _normalize(movement)
        self.position += movement * self.movement_speed * delta_time * magnitude

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity
        self.rotate(xoffset, yoffset, constrain_pitch)

    def rotate(self, yaw_offset=0.0, pitch_offset=0.0, constrain_pitch=True):
        self.yaw += yaw_offset
        self.pitch += pitch_offset
        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))
        self._update_camera_vectors()

    def process_look_step(self, yaw_offset=0.0, pitch_offset=0.0, constrain_pitch=True):
        self.rotate(yaw_offset, pitch_offset, constrain_pitch)

    def adjust_zoom(self, zoom_delta):
        self.zoom += zoom_delta
        self.zoom = max(settings.CAMERA_MIN_FOV, min(settings.CAMERA_MAX_FOV, self.zoom))

    def _update_camera_vectors(self):
        yaw_radians = math.radians(self.yaw)
        pitch_radians = math.radians(self.pitch)
        front = np.array(
            [
                math.cos(yaw_radians) * math.cos(pitch_radians),
                math.sin(pitch_radians),
                math.sin(yaw_radians) * math.cos(pitch_radians),
            ],
            dtype=np.float32,
        )
        self.front = _normalize(front)
        self.right = _normalize(np.cross(self.front, self.world_up))
        self.up = _normalize(np.cross(self.right, self.front))

    def _look_at(self, position, target, up):
        forward = _normalize(target - position)
        right = _normalize(np.cross(forward, up))
        camera_up = _normalize(np.cross(right, forward))

        view = np.identity(4, dtype=np.float32)
        view[0, 0:3] = right
        view[1, 0:3] = camera_up
        view[2, 0:3] = -forward
        view[0, 3] = -np.dot(right, position)
        view[1, 3] = -np.dot(camera_up, position)
        view[2, 3] = np.dot(forward, position)
        return view.astype(np.float32)
