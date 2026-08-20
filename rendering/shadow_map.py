import numpy as np
from OpenGL.GL import (
    GL_CLAMP_TO_BORDER,
    GL_DEPTH_ATTACHMENT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_COMPONENT,
    GL_DEPTH_COMPONENT24,
    GL_FLOAT,
    GL_FRAMEBUFFER,
    GL_FRAMEBUFFER_COMPLETE,
    GL_LINEAR,
    GL_NONE,
    GL_TEXTURE_2D,
    GL_TEXTURE_BORDER_COLOR,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    glBindFramebuffer,
    glBindTexture,
    glCheckFramebufferStatus,
    glClear,
    glDrawBuffer,
    glFramebufferTexture2D,
    glGenFramebuffers,
    glGenTextures,
    glReadBuffer,
    glTexImage2D,
    glTexParameterfv,
    glTexParameteri,
    glViewport,
)

from scene.object3d import identity, look_at, perspective

DOWN_TARGET_OFFSET = np.array([0.0, -1.0, 0.0], dtype=np.float32)
DOWN_UP_VECTOR = (0.0, 0.0, -1.0)


class ShadowMap:
    """Depth-only render target for one downward-facing light."""

    def __init__(self, size, fov_degrees, near_plane, far_plane):
        self.size = int(size)
        self.projection = perspective(fov_degrees, 1.0, near_plane, far_plane)
        self.light_space_matrix = identity()

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, self.size, self.size, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, np.ones(4, dtype=np.float32))

        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.texture, 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)

        if status != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"Shadow map framebuffer incomplete (status {status}).")

    def begin(self, light_position):
        position = np.asarray(light_position, dtype=np.float32)
        self.light_space_matrix = self.projection @ look_at(position, position + DOWN_TARGET_OFFSET, DOWN_UP_VECTOR)

        glViewport(0, 0, self.size, self.size)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glClear(GL_DEPTH_BUFFER_BIT)

    def end(self, viewport_size):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, int(viewport_size[0]), int(viewport_size[1]))
