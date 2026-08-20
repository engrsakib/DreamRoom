import math

import numpy as np


def _normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0.0:
        return vector.astype(np.float32)
    return (vector / norm).astype(np.float32)


class Camera:
    def __init__(
        self,
        position=(0.0, 0.0, 3.0),
        up=(0.0, 1.0, 0.0),
        yaw=-90.0,
        pitch=0.0,
        movement_speed=4.0,
        mouse_sensitivity=0.1,
        zoom=45.0,
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
        velocity = self.movement_speed * delta_time

        if direction == "FORWARD":
            self.position += self.front * velocity
        elif direction == "BACKWARD":
            self.position -= self.front * velocity
        elif direction == "LEFT":
            self.position -= self.right * velocity
        elif direction == "RIGHT":
            self.position += self.right * velocity

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity

        self.process_look_step(xoffset, yoffset, constrain_pitch)

    def process_look_step(self, yaw_offset=0.0, pitch_offset=0.0, constrain_pitch=True):
        self.yaw += yaw_offset
        self.pitch += pitch_offset

        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))

        self._update_camera_vectors()

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
