import math

import numpy as np


def identity():
    return np.identity(4, dtype=np.float32)


def translate(matrix, offset):
    tx, ty, tz = offset
    translation = identity()
    translation[0, 3] = tx
    translation[1, 3] = ty
    translation[2, 3] = tz
    return matrix @ translation


def rotate_x(matrix, angle_degrees):
    angle = math.radians(angle_degrees)
    rotation = identity()
    rotation[1, 1] = math.cos(angle)
    rotation[1, 2] = -math.sin(angle)
    rotation[2, 1] = math.sin(angle)
    rotation[2, 2] = math.cos(angle)
    return matrix @ rotation


def rotate_y(matrix, angle_degrees):
    angle = math.radians(angle_degrees)
    rotation = identity()
    rotation[0, 0] = math.cos(angle)
    rotation[0, 2] = math.sin(angle)
    rotation[2, 0] = -math.sin(angle)
    rotation[2, 2] = math.cos(angle)
    return matrix @ rotation


def rotate_z(matrix, angle_degrees):
    angle = math.radians(angle_degrees)
    rotation = identity()
    rotation[0, 0] = math.cos(angle)
    rotation[0, 1] = -math.sin(angle)
    rotation[1, 0] = math.sin(angle)
    rotation[1, 1] = math.cos(angle)
    return matrix @ rotation


def scale(matrix, factors):
    sx, sy, sz = factors
    scaling = identity()
    scaling[0, 0] = sx
    scaling[1, 1] = sy
    scaling[2, 2] = sz
    return matrix @ scaling


def perspective(fov_degrees, aspect_ratio, near_plane, far_plane):
    f = 1.0 / math.tan(math.radians(fov_degrees) / 2.0)
    matrix = np.zeros((4, 4), dtype=np.float32)
    matrix[0, 0] = f / aspect_ratio
    matrix[1, 1] = f
    matrix[2, 2] = (far_plane + near_plane) / (near_plane - far_plane)
    matrix[2, 3] = (2.0 * far_plane * near_plane) / (near_plane - far_plane)
    matrix[3, 2] = -1.0
    return matrix


def look_at(position, target, up):
    position = np.asarray(position, dtype=np.float32)
    forward = _unit(np.asarray(target, dtype=np.float32) - position)
    right = _unit(np.cross(forward, np.asarray(up, dtype=np.float32)))
    camera_up = _unit(np.cross(right, forward))

    view = identity()
    view[0, 0:3] = right
    view[1, 0:3] = camera_up
    view[2, 0:3] = -forward
    view[0, 3] = -np.dot(right, position)
    view[1, 3] = -np.dot(camera_up, position)
    view[2, 3] = np.dot(forward, position)
    return view


def _unit(vector):
    norm = np.linalg.norm(vector)
    if norm == 0.0:
        return vector.astype(np.float32)
    return (vector / norm).astype(np.float32)


class Object3D:
    def __init__(self, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale_values=(1.0, 1.0, 1.0), mesh=None, material=None):
        self.position = position
        self.rotation = rotation
        self.scale_values = scale_values
        self.mesh = mesh
        self.material = material
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def get_local_matrix(self):
        model = identity()
        model = translate(model, self.position)
        model = rotate_x(model, self.rotation[0])
        model = rotate_y(model, self.rotation[1])
        model = rotate_z(model, self.rotation[2])
        model = scale(model, self.scale_values)
        return model

    def get_model_matrix(self, parent_matrix=None):
        local = self.get_local_matrix()
        if parent_matrix is None:
            return local
        return parent_matrix @ local

    def draw(self, renderer, parent_matrix=None):
        renderer.draw_object(self, parent_matrix)
