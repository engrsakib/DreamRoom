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
        ceiling_material = Material(settings.CEILING_COLOR, specular_strength=0.12, shininess=18.0)

        self.add_child(Object3D(position=(0.0, -0.05, 0.0), scale_values=(16.0, 0.1, 16.0), mesh=cube_mesh, material=floor_material))
        self.add_child(Object3D(position=(0.0, 6.05, 0.0), scale_values=(16.0, 0.1, 16.0), mesh=cube_mesh, material=ceiling_material))
        self.add_child(Object3D(position=(0.0, 3.0, -8.0), scale_values=(16.0, 6.0, 0.2), mesh=cube_mesh, material=material))
        self.add_child(Object3D(position=(0.0, 3.0, 8.0), scale_values=(16.0, 6.0, 0.2), mesh=cube_mesh, material=material))
        self.add_child(Object3D(position=(8.0, 3.0, 0.0), scale_values=(0.2, 6.0, 16.0), mesh=cube_mesh, material=material))

        for position, scale in self._left_wall_segments():
            self.add_child(Object3D(position=position, scale_values=scale, mesh=cube_mesh, material=material))

    @staticmethod
    def _left_wall_segments():
        """Left wall split into four pieces so the window opening stays hollow.

        The pieces still cover the exact same plane and extents as the original
        solid wall, so the room bounds are unchanged.
        """
        x = settings.LEFT_WALL_X
        thickness = settings.WALL_THICKNESS
        height = settings.ROOM_HEIGHT
        half_depth = settings.ROOM_DEPTH / 2.0
        y_min, y_max = settings.WINDOW_Y_MIN, settings.WINDOW_Y_MAX
        z_min, z_max = settings.WINDOW_Z_MIN, settings.WINDOW_Z_MAX

        band_height = y_max - y_min
        band_y = (y_min + y_max) / 2.0
        back_depth = z_min + half_depth
        front_depth = half_depth - z_max

        return [
            ((x, y_min / 2.0, 0.0), (thickness, y_min, settings.ROOM_DEPTH)),
            ((x, (y_max + height) / 2.0, 0.0), (thickness, height - y_max, settings.ROOM_DEPTH)),
            ((x, band_y, (z_min - half_depth) / 2.0), (thickness, band_height, back_depth)),
            ((x, band_y, (z_max + half_depth) / 2.0), (thickness, band_height, front_depth)),
        ]
