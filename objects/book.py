from config import settings
from rendering.material import Material
from scene.object3d import Object3D


class Book(Object3D):
    def __init__(self, cube_mesh, position, size, color, rotation=(0.0, 0.0, 0.0)):
        super().__init__(position=position, rotation=rotation)
        width, height, depth = size
        cover = Material(color, specular_strength=0.30, shininess=32.0)
        pages = Material(settings.BOOK_PAGES_COLOR, specular_strength=0.12, shininess=12.0)

        self.add_child(Object3D(scale_values=size, mesh=cube_mesh, material=cover))
        self.add_child(
            Object3D(
                position=(width * 0.12, 0.0, 0.0),
                scale_values=(width * 0.78, height * 0.9, depth * 0.88),
                mesh=cube_mesh,
                material=pages,
            )
        )
