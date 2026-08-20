from config import settings
from rendering.material import Material
from scene.object3d import Object3D


class Room(Object3D):
    def __init__(self, cube_mesh):
        super().__init__()
        material = Material(
            settings.WALL_COLOR,
            specular_strength=0.45,
            shininess=64.0,
            tiled=True,
            tile_size=settings.WALL_TILE_SIZE,
        )
        floor_material = Material(
            settings.FLOOR_COLOR,
            specular_strength=0.30,
            shininess=40.0,
            tiled=True,
            tile_size=settings.FLOOR_TILE_SIZE,
        )

        self.add_child(Object3D(position=(0.0, -0.05, 0.0), scale_values=(16.0, 0.1, 16.0), mesh=cube_mesh, material=floor_material))
        self.add_child(Object3D(position=(0.0, 3.0, -8.0), scale_values=(16.0, 6.0, 0.2), mesh=cube_mesh, material=material))
        self.add_child(Object3D(position=(-8.0, 3.0, 0.0), scale_values=(0.2, 6.0, 16.0), mesh=cube_mesh, material=material))
        self.add_child(Object3D(position=(8.0, 3.0, 0.0), scale_values=(0.2, 6.0, 16.0), mesh=cube_mesh, material=material))
