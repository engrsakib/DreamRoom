import sys

import glfw
from OpenGL.GL import glViewport

from config import settings


class Window:
    def __init__(self, width=settings.WINDOW_WIDTH, height=settings.WINDOW_HEIGHT, title=settings.WINDOW_TITLE):
        self.width = width
        self.height = height
        self.title = title
        self.handle = None

    def create(self):
        self.handle = self._create_window(core_profile=True)
        if self.handle is None:
            print("OpenGL 3.3 Core window creation failed. Retrying with default context hints...")
            self.handle = self._create_window(core_profile=False)
        if self.handle is None:
            print("Failed to create an OpenGL context and window.")
            print("Check your driver, WSLg setup, or software rendering support.")
            print("If needed in WSL2, try: LIBGL_ALWAYS_SOFTWARE=1 python3 main.py")
            raise RuntimeError("Failed to create window.")

        glfw.make_context_current(self.handle)
        glfw.swap_interval(1)
        glfw.set_framebuffer_size_callback(self.handle, self._on_resize)
        glViewport(0, 0, self.width, self.height)
        return self

    def _create_window(self, core_profile=True):
        glfw.default_window_hints()
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
        if core_profile:
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
            if sys.platform == "darwin":
                glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        return glfw.create_window(self.width, self.height, self.title, None, None)

    def _on_resize(self, window, width, height):
        self.width = max(width, 1)
        self.height = max(height, 1)
        glViewport(0, 0, self.width, self.height)

    def should_close(self):
        return glfw.window_should_close(self.handle)

    def set_should_close(self, value):
        glfw.set_window_should_close(self.handle, value)

    def swap_buffers(self):
        glfw.swap_buffers(self.handle)
