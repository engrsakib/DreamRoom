from config import settings
from rendering.material import Material
from scene.object3d import Object3D

LAMP_X = settings.LAMP_LIGHT_POSITION[0]
LAMP_Z = settings.LAMP_LIGHT_POSITION[2]


class TableLamp(Object3D):
    def __init__(self, cylinder_mesh, frustum_mesh):
        super().__init__()
        base = Material(settings.LAMP_BASE_COLOR, specular_strength=0.45, shininess=64.0)
        pole = Material(settings.LAMP_POLE_COLOR, specular_strength=0.50, shininess=72.0)
        shade = Material(settings.LAMP_SHADE_COLOR, specular_strength=0.35, shininess=48.0)

        self.add_child(Object3D(position=(LAMP_X, 1.42, LAMP_Z), scale_values=(0.50, 0.06, 0.50), mesh=cylinder_mesh, material=base))
        self.add_child(Object3D(position=(LAMP_X, 1.875, LAMP_Z), scale_values=(0.07, 0.85, 0.07), mesh=cylinder_mesh, material=pole))
        self.add_child(Object3D(position=(LAMP_X, 2.42, LAMP_Z), scale_values=(0.62, 0.42, 0.62), mesh=frustum_mesh, material=shade))

        self.bulb = Object3D(
            position=settings.LAMP_LIGHT_POSITION,
            scale_values=(0.14, 0.16, 0.14),
            mesh=cylinder_mesh,
            material=Material(settings.LAMP_GLOW_COLOR),
        )
