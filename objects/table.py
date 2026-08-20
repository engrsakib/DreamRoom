from config import settings
from rendering.material import Material
from scene.object3d import Object3D


class Table(Object3D):
    def __init__(self, cube_mesh):
        super().__init__()
        material = Material(settings.TABLE_COLOR, specular_strength=0.24, shininess=24.0)

        self.add_child(Object3D(position=(4.7, 1.30, -1.5), scale_values=(2.2, 0.2, 1.3), mesh=cube_mesh, material=material))
        self.add_child(Object3D(position=(3.8, 0.65, -0.95), scale_values=(0.18, 1.1, 0.18), mesh=cube_mesh, material=material))
        self.add_child(Object3D(position=(5.6, 0.65, -0.95), scale_values=(0.18, 1.1, 0.18), mesh=cube_mesh, material=material))
        self.add_child(Object3D(position=(3.8, 0.65, -2.05), scale_values=(0.18, 1.1, 0.18), mesh=cube_mesh, material=material))
        self.add_child(Object3D(position=(5.6, 0.65, -2.05), scale_values=(0.18, 1.1, 0.18), mesh=cube_mesh, material=material))
