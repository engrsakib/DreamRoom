from pathlib import Path
import math

import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_DYNAMIC_DRAW,
    GL_FALSE,
    GL_FLOAT,
    GL_TRIANGLES,
    glBindBuffer,
    glBindVertexArray,
    glBufferData,
    glClear,
    glClearColor,
    glDisable,
    glDrawArrays,
    glEnable,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenVertexArrays,
    glVertexAttribPointer,
)

from config import settings
from rendering.shader import Shader
from scene.object3d import identity

class Renderer:
    def __init__(self):
        shader_dir = Path(__file__).resolve().parent.parent / "shaders"
        self.lighting_shader = Shader(shader_dir / "lighting.vert", shader_dir / "lighting.frag")
        self.lamp_shader = Shader(shader_dir / "lamp.vert", shader_dir / "lamp.frag")
        self.ui_shader = Shader(shader_dir / "ui.vert", shader_dir / "ui.frag")
        self.triangle_shader = Shader(shader_dir / "triangle.vert", shader_dir / "triangle.frag")

        glEnable(GL_DEPTH_TEST)

        self.ui_vao = glGenVertexArrays(1)
        self.ui_vbo = glGenBuffers(1)
        glBindVertexArray(self.ui_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.ui_vbo)
        glBufferData(GL_ARRAY_BUFFER, 0, None, GL_DYNAMIC_DRAW)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * np.dtype(np.float32).itemsize, None)
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def clear(self):
        glClearColor(*settings.CLEAR_COLOR)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def render_triangle(self, triangle_mesh):
        self.triangle_shader.use()
        triangle_mesh.draw()

    def render_scene(self, scene, camera, aspect_ratio):
        projection = self._perspective(camera.zoom, aspect_ratio, 0.1, 100.0)
        view = camera.get_view_matrix()

        self.lighting_shader.use()
        self.lighting_shader.set_mat4("projection", projection)
        self.lighting_shader.set_mat4("view", view)
        self._apply_lights(scene, camera)

        for obj in scene.iter_objects():
            self._draw_recursive(obj, None)

        if scene.emissive_objects:
            self.lamp_shader.use()
            self.lamp_shader.set_mat4("projection", projection)
            self.lamp_shader.set_mat4("view", view)
            for emissive in scene.emissive_objects:
                self.lamp_shader.set_vec3("color", emissive.material.color)
                self.lamp_shader.set_mat4("model", emissive.get_model_matrix())
                emissive.mesh.draw()

    def render_ui_elements(self, elements, screen_size):
        glDisable(GL_DEPTH_TEST)
        for element in elements:
            self._draw_ui_shape(element["vertices"], element["color"], screen_size)
        glEnable(GL_DEPTH_TEST)

    def draw_object(self, obj, parent_matrix=None):
        if obj.mesh is not None and obj.material is not None:
            model = obj.get_model_matrix(parent_matrix)
            normal_matrix = identity()
            normal_matrix[0:3, 0:3] = np.linalg.inv(model[0:3, 0:3]).T

            self.lighting_shader.set_mat4("model", model)
            self.lighting_shader.set_mat4("normalMatrix", normal_matrix)
            self.lighting_shader.set_vec3("objectColor", obj.material.color)
            self.lighting_shader.set_float("specularStrength", obj.material.specular_strength)
            self.lighting_shader.set_float("shininess", obj.material.shininess)
            obj.mesh.draw()

        for child in obj.children:
            self.draw_object(child, obj.get_model_matrix(parent_matrix))

    def _draw_recursive(self, obj, parent_matrix):
        self.draw_object(obj, parent_matrix)

    def _apply_lights(self, scene, camera):
        self.lighting_shader.set_vec3("viewPos", camera.position)

        d = scene.directional_light
        self.lighting_shader.set_vec3("dirLight.direction", d.direction)
        self.lighting_shader.set_vec3("dirLight.ambient", d.ambient)
        self.lighting_shader.set_vec3("dirLight.diffuse", d.diffuse)
        self.lighting_shader.set_vec3("dirLight.specular", d.specular)

        p = scene.point_light
        self.lighting_shader.set_vec3("pointLight.position", p.position)
        self.lighting_shader.set_float("pointLight.constant", p.constant)
        self.lighting_shader.set_float("pointLight.linear", p.linear)
        self.lighting_shader.set_float("pointLight.quadratic", p.quadratic)
        self.lighting_shader.set_vec3("pointLight.ambient", p.ambient)
        self.lighting_shader.set_vec3("pointLight.diffuse", p.diffuse)
        self.lighting_shader.set_vec3("pointLight.specular", p.specular)

        l = scene.lamp_light
        self.lighting_shader.set_vec3("lampLight.position", l.position)
        self.lighting_shader.set_float("lampLight.constant", l.constant)
        self.lighting_shader.set_float("lampLight.linear", l.linear)
        self.lighting_shader.set_float("lampLight.quadratic", l.quadratic)
        self.lighting_shader.set_vec3("lampLight.ambient", l.ambient)
        self.lighting_shader.set_vec3("lampLight.diffuse", l.diffuse)
        self.lighting_shader.set_vec3("lampLight.specular", l.specular)

        s = scene.spot_light
        self.lighting_shader.set_vec3("spotLight.position", s.position)
        self.lighting_shader.set_vec3("spotLight.direction", s.direction)
        self.lighting_shader.set_float("spotLight.cutOff", math.cos(math.radians(s.cutoff)))
        self.lighting_shader.set_float("spotLight.outerCutOff", math.cos(math.radians(s.outer_cutoff)))
        self.lighting_shader.set_float("spotLight.constant", s.constant)
        self.lighting_shader.set_float("spotLight.linear", s.linear)
        self.lighting_shader.set_float("spotLight.quadratic", s.quadratic)
        self.lighting_shader.set_vec3("spotLight.ambient", s.ambient)
        self.lighting_shader.set_vec3("spotLight.diffuse", s.diffuse)
        self.lighting_shader.set_vec3("spotLight.specular", s.specular)

    def _perspective(self, fov_degrees, aspect_ratio, near_plane, far_plane):
        f = 1.0 / math.tan(math.radians(fov_degrees) / 2.0)
        matrix = np.zeros((4, 4), dtype=np.float32)
        matrix[0, 0] = f / aspect_ratio
        matrix[1, 1] = f
        matrix[2, 2] = (far_plane + near_plane) / (near_plane - far_plane)
        matrix[2, 3] = (2.0 * far_plane * near_plane) / (near_plane - far_plane)
        matrix[3, 2] = -1.0
        return matrix

    def _draw_ui_shape(self, vertices, color, screen_size):
        data = np.array(vertices, dtype=np.float32)
        self.ui_shader.use()
        self.ui_shader.set_vec2("screenSize", screen_size)
        self.ui_shader.set_vec3("uiColor", color)
        glBindVertexArray(self.ui_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.ui_vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)
        glDrawArrays(GL_TRIANGLES, 0, len(data) // 2)

