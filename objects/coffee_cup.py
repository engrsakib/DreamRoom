from config import settings
from objects.tea_table import TEA_TABLE_SURFACE_Y, TEA_TABLE_X, TEA_TABLE_Z
from rendering.material import Material
from scene.object3d import Object3D


class CoffeeCup(Object3D):
    def __init__(self, cube_mesh, cylinder_mesh):
        super().__init__()
        saucer = Material(settings.SAUCER_COLOR, specular_strength=0.50, shininess=80.0)
        porcelain = Material(settings.CUP_COLOR, specular_strength=0.50, shininess=80.0)
        coffee = Material(settings.COFFEE_COLOR, specular_strength=0.60, shininess=96.0)

        cup_x = TEA_TABLE_X + 0.05
        cup_z = TEA_TABLE_Z + 0.05

        self.add_child(Object3D(position=(cup_x, TEA_TABLE_SURFACE_Y + 0.02, cup_z), scale_values=(0.50, 0.04, 0.50), mesh=cylinder_mesh, material=saucer))
        self.add_child(Object3D(position=(cup_x, TEA_TABLE_SURFACE_Y + 0.24, cup_z), scale_values=(0.34, 0.40, 0.34), mesh=cylinder_mesh, material=porcelain))
        self.add_child(Object3D(position=(cup_x, TEA_TABLE_SURFACE_Y + 0.38, cup_z), scale_values=(0.29, 0.02, 0.29), mesh=cylinder_mesh, material=coffee))

        self.add_child(Object3D(position=(cup_x + 0.20, TEA_TABLE_SURFACE_Y + 0.34, cup_z), scale_values=(0.12, 0.05, 0.05), mesh=cube_mesh, material=porcelain))
        self.add_child(Object3D(position=(cup_x + 0.25, TEA_TABLE_SURFACE_Y + 0.26, cup_z), scale_values=(0.05, 0.16, 0.05), mesh=cube_mesh, material=porcelain))
        self.add_child(Object3D(position=(cup_x + 0.20, TEA_TABLE_SURFACE_Y + 0.18, cup_z), scale_values=(0.12, 0.05, 0.05), mesh=cube_mesh, material=porcelain))
