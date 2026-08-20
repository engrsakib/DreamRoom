from config import settings
from objects.reading_table import DESK_CENTER_X
from rendering.material import Material
from scene.object3d import Object3D

CHAIR_X = DESK_CENTER_X
CHAIR_Z = -6.05
BACKREST_Z = CHAIR_Z + 0.40


class Chair(Object3D):
    def __init__(self, cube_mesh):
        super().__init__()
        frame = Material(settings.CHAIR_FRAME_COLOR, specular_strength=0.32, shininess=40.0)
        cushion = Material(settings.CHAIR_CUSHION_COLOR, specular_strength=0.18, shininess=16.0)

        for leg_x in (CHAIR_X - 0.38, CHAIR_X + 0.38):
            for leg_z in (CHAIR_Z - 0.38, CHAIR_Z + 0.38):
                self.add_child(Object3D(position=(leg_x, 0.275, leg_z), scale_values=(0.09, 0.55, 0.09), mesh=cube_mesh, material=frame))

        self.add_child(Object3D(position=(CHAIR_X, 0.60, CHAIR_Z), scale_values=(0.92, 0.10, 0.92), mesh=cube_mesh, material=frame))
        self.add_child(Object3D(position=(CHAIR_X, 0.68, CHAIR_Z), scale_values=(0.82, 0.06, 0.82), mesh=cube_mesh, material=cushion))

        for post_x in (CHAIR_X - 0.415, CHAIR_X + 0.415):
            self.add_child(Object3D(position=(post_x, 1.05, BACKREST_Z), scale_values=(0.09, 0.80, 0.09), mesh=cube_mesh, material=frame))
        self.add_child(Object3D(position=(CHAIR_X, 1.20, BACKREST_Z), scale_values=(0.92, 0.40, 0.07), mesh=cube_mesh, material=cushion))
        self.add_child(Object3D(position=(CHAIR_X, 1.45, BACKREST_Z), scale_values=(0.92, 0.10, 0.09), mesh=cube_mesh, material=frame))
