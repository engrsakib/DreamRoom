import ctypes
import math

import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_FALSE,
    GL_FLOAT,
    GL_STATIC_DRAW,
    GL_TRIANGLES,
    glBindBuffer,
    glBindVertexArray,
    glBufferData,
    glDrawArrays,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenVertexArrays,
    glVertexAttribPointer,
)


class Mesh:
    def __init__(self, vertices, attribute_sizes):
        self.vertices = np.array(vertices, dtype=np.float32)
        self.attribute_sizes = attribute_sizes
        self.vertex_stride = sum(attribute_sizes)
        self.vertex_count = len(self.vertices) // self.vertex_stride
        self.draw_mode = GL_TRIANGLES

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        stride_bytes = self.vertex_stride * self.vertices.itemsize
        offset_floats = 0
        for index, size in enumerate(attribute_sizes):
            glVertexAttribPointer(
                index,
                size,
                GL_FLOAT,
                GL_FALSE,
                stride_bytes,
                ctypes.c_void_p(offset_floats * self.vertices.itemsize),
            )
            glEnableVertexAttribArray(index)
            offset_floats += size

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(self.draw_mode, 0, self.vertex_count)

    @staticmethod
    def create_cube():
        return Mesh(
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
            [3, 3],
        )

    @staticmethod
    def create_cylinder(segments=24):
        return Mesh(Mesh._tapered_vertices(0.5, 0.5, segments), [3, 3])

    @staticmethod
    def create_cone(segments=24):
        return Mesh(Mesh._tapered_vertices(0.0, 0.5, segments), [3, 3])

    @staticmethod
    def create_frustum(top_radius=0.30, segments=24):
        return Mesh(Mesh._tapered_vertices(top_radius, 0.5, segments), [3, 3])

    @staticmethod
    def _tapered_vertices(top_radius, bottom_radius, segments):
        height = 1.0
        top_y = height * 0.5
        bottom_y = -height * 0.5
        slope = bottom_radius - top_radius

        vertices = []
        for index in range(segments):
            angle_a = (2.0 * math.pi * index) / segments
            angle_b = (2.0 * math.pi * (index + 1)) / segments
            cos_a, sin_a = math.cos(angle_a), math.sin(angle_a)
            cos_b, sin_b = math.cos(angle_b), math.sin(angle_b)

            normal_a = Mesh._normalized(cos_a * height, slope, sin_a * height)
            normal_b = Mesh._normalized(cos_b * height, slope, sin_b * height)

            bottom_a = (bottom_radius * cos_a, bottom_y, bottom_radius * sin_a)
            bottom_b = (bottom_radius * cos_b, bottom_y, bottom_radius * sin_b)
            top_a = (top_radius * cos_a, top_y, top_radius * sin_a)
            top_b = (top_radius * cos_b, top_y, top_radius * sin_b)

            vertices.extend([*bottom_a, *normal_a, *bottom_b, *normal_b, *top_b, *normal_b])
            if top_radius > 0.0:
                vertices.extend([*bottom_a, *normal_a, *top_b, *normal_b, *top_a, *normal_a])

            vertices.extend([0.0, bottom_y, 0.0, 0.0, -1.0, 0.0, *bottom_b, 0.0, -1.0, 0.0, *bottom_a, 0.0, -1.0, 0.0])
            if top_radius > 0.0:
                vertices.extend([0.0, top_y, 0.0, 0.0, 1.0, 0.0, *top_a, 0.0, 1.0, 0.0, *top_b, 0.0, 1.0, 0.0])

        return vertices

    @staticmethod
    def _normalized(x, y, z):
        length = math.sqrt(x * x + y * y + z * z)
        if length == 0.0:
            return (0.0, 1.0, 0.0)
        return (x / length, y / length, z / length)

    @staticmethod
    def create_triangle():
        return Mesh(
            [
                -0.6, -0.4, 0.0, 1.0, 0.2, 0.2,
                0.6, -0.4, 0.0, 0.2, 1.0, 0.2,
                0.0, 0.6, 0.0, 0.2, 0.4, 1.0,
            ],
            [3, 3],
        )
