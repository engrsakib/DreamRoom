from config import settings
from rendering.material import Material
from scene.object3d import Object3D


class Bed(Object3D):
    def __init__(self, cube_mesh):
        super().__init__()
        frame = Material(settings.BED_FRAME_COLOR, specular_strength=0.22, shininess=18.0)
        mattress = Material(settings.MATTRESS_COLOR, specular_strength=0.2, shininess=20.0)
        pillow = Material(settings.PILLOW_COLOR, specular_strength=0.25, shininess=24.0)

        self.add_child(Object3D(position=(-4.8, 0.55, -5.0), scale_values=(3.6, 0.6, 5.0), mesh=cube_mesh, material=frame))
        self.add_child(Object3D(position=(-4.8, 1.05, -5.0), scale_values=(3.2, 0.45, 4.4), mesh=cube_mesh, material=mattress))
        self.add_child(Object3D(position=(-4.8, 1.65, -7.1), scale_values=(3.4, 1.5, 0.25), mesh=cube_mesh, material=frame))
        self.add_child(Object3D(position=(-4.8, 1.45, -6.2), scale_values=(1.5, 0.25, 1.2), mesh=cube_mesh, material=pillow))
