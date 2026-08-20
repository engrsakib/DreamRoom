import numpy as np
from OpenGL.GL import (
    GL_COMPILE_STATUS,
    GL_FALSE,
    GL_FRAGMENT_SHADER,
    GL_LINK_STATUS,
    GL_TRUE,
    GL_VERTEX_SHADER,
    glAttachShader,
    glCompileShader,
    glCreateProgram,
    glCreateShader,
    glDeleteShader,
    glGetProgramInfoLog,
    glGetProgramiv,
    glGetShaderInfoLog,
    glGetShaderiv,
    glGetUniformLocation,
    glLinkProgram,
    glShaderSource,
    glUniform1f,
    glUniform1i,
    glUniform2f,
    glUniform3f,
    glUniformMatrix4fv,
    glUseProgram,
)


class Shader:
    def __init__(self, vertex_source, fragment_source):
        self.id = glCreateProgram()
        self._uniform_locations = {}

        vertex_shader = self._compile(vertex_source, GL_VERTEX_SHADER)
        fragment_shader = self._compile(fragment_source, GL_FRAGMENT_SHADER)

        glAttachShader(self.id, vertex_shader)
        glAttachShader(self.id, fragment_shader)
        glLinkProgram(self.id)

        success = glGetProgramiv(self.id, GL_LINK_STATUS)
        if not success:
            log = glGetProgramInfoLog(self.id).decode("utf-8", errors="replace")
            print("Shader program linking failed:")
            print(log)
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)
            raise RuntimeError("Shader program linking failed.")

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

    def _compile(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        success = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not success:
            shader_name = "vertex" if shader_type == GL_VERTEX_SHADER else "fragment"
            log = glGetShaderInfoLog(shader).decode("utf-8", errors="replace")
            print(f"{shader_name.capitalize()} shader compilation failed:")
            print(log)
            raise RuntimeError(f"{shader_name.capitalize()} shader compilation failed.")

        return shader

    def use(self):
        glUseProgram(self.id)

    def _loc(self, name):
        if name not in self._uniform_locations:
            self._uniform_locations[name] = glGetUniformLocation(self.id, name)
        return self._uniform_locations[name]

    def set_bool(self, name, value):
        glUniform1i(self._loc(name), int(bool(value)))

    def set_int(self, name, value):
        glUniform1i(self._loc(name), value)

    def set_float(self, name, value):
        glUniform1f(self._loc(name), value)

    def set_vec2(self, name, x, y=None):
        if y is None:
            vector = np.asarray(x, dtype=np.float32).flatten()
            if vector.size != 2:
                raise ValueError(f"Uniform '{name}' expects 2 values.")
            glUniform2f(self._loc(name), float(vector[0]), float(vector[1]))
            return

        glUniform2f(self._loc(name), float(x), float(y))

    def set_vec3(self, name, x, y=None, z=None):
        if y is None and z is None:
            vector = np.asarray(x, dtype=np.float32).flatten()
            if vector.size != 3:
                raise ValueError(f"Uniform '{name}' expects 3 values.")
            glUniform3f(self._loc(name), float(vector[0]), float(vector[1]), float(vector[2]))
            return

        if y is None or z is None:
            raise ValueError(f"Uniform '{name}' requires 3 float values.")

        glUniform3f(self._loc(name), float(x), float(y), float(z))

    def set_mat4(self, name, matrix):
        matrix = np.asarray(matrix, dtype=np.float32)
        glUniformMatrix4fv(self._loc(name), 1, GL_FALSE, matrix.flatten(order="F"))
