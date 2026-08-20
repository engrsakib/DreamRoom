import ctypes

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
    def create_triangle():
        return Mesh(
            [
                -0.6, -0.4, 0.0, 1.0, 0.2, 0.2,
                0.6, -0.4, 0.0, 0.2, 1.0, 0.2,
                0.0, 0.6, 0.0, 0.2, 0.4, 1.0,
            ],
            [3, 3],
        )
