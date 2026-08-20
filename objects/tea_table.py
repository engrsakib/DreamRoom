from config import settings
from rendering.material import Material
from scene.object3d import Object3D

TEA_TABLE_X = -2.25
TEA_TABLE_Z = -6.6
TEA_TABLE_SURFACE_Y = 0.82


class TeaTable(Object3D):
    def __init__(self, cube_mesh):
        super().__init__()
        wood = Material(settings.TEA_TABLE_COLOR, specular_strength=0.28, shininess=32.0)

        self.add_child(Object3D(position=(TEA_TABLE_X, 0.75, TEA_TABLE_Z), scale_values=(1.2, 0.14, 1.2), mesh=cube_mesh, material=wood))
        self.add_child(Object3D(position=(TEA_TABLE_X, 0.40, TEA_TABLE_Z), scale_values=(1.0, 0.12, 1.0), mesh=cube_mesh, material=wood))
        for leg_x in (TEA_TABLE_X - 0.5, TEA_TABLE_X + 0.5):
            for leg_z in (TEA_TABLE_Z - 0.5, TEA_TABLE_Z + 0.5):
                self.add_child(Object3D(position=(leg_x, 0.34, leg_z), scale_values=(0.11, 0.68, 0.11), mesh=cube_mesh, material=wood))
