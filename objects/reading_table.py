from config import settings
from objects.book import Book
from rendering.material import Material
from scene.object3d import Object3D

DESK_CENTER_X = 3.4
DESK_WIDTH = 2.8
DESK_SURFACE_Y = 1.39
BACK_PANEL_Z = -7.83
SHELF_Z = -7.40
DESK_TOP_Z = -7.03
DESK_FRONT_Z = -6.28

SHELF_BOOKS = (
    (2.05, ((-1.10, 0.16, 0.50, 0.0), (-0.91, 0.13, 0.46, 0.0), (-0.73, 0.18, 0.52, 0.0), (-0.53, 0.12, 0.44, 0.0),
            (-0.37, 0.15, 0.48, 0.0), (-0.13, 0.14, 0.46, 14.0), (0.17, 0.17, 0.50, 0.0), (0.37, 0.13, 0.45, 0.0))),
    (2.75, ((-1.05, 0.15, 0.40, 0.0), (-0.87, 0.12, 0.36, 0.0), (-0.71, 0.16, 0.42, 0.0), (-0.52, 0.14, 0.38, 0.0),
            (-0.29, 0.13, 0.36, -12.0), (0.05, 0.16, 0.40, 0.0))),
)

DESK_STACK = (
    (1.44, (0.52, 0.10, 0.38), 8.0),
    (1.54, (0.48, 0.09, 0.36), -6.0),
    (1.63, (0.44, 0.08, 0.34), 3.0),
)


class ReadingTable(Object3D):
    def __init__(self, cube_mesh):
        super().__init__()
        desk = Material(settings.READING_TABLE_COLOR, specular_strength=0.35, shininess=48.0)
        shelf = Material(settings.BOOKSHELF_COLOR, specular_strength=0.22, shininess=20.0)

        self.add_child(Object3D(position=(DESK_CENTER_X, 1.30, DESK_TOP_Z), scale_values=(DESK_WIDTH, 0.18, 1.5), mesh=cube_mesh, material=desk))
        for leg_x in (DESK_CENTER_X - 1.25, DESK_CENTER_X + 1.25):
            for leg_z in (-7.63, -6.43):
                self.add_child(Object3D(position=(leg_x, 0.65, leg_z), scale_values=(0.18, 1.3, 0.18), mesh=cube_mesh, material=desk))

        self.add_child(Object3D(position=(DESK_CENTER_X, 2.35, BACK_PANEL_Z), scale_values=(DESK_WIDTH, 1.9, 0.1), mesh=cube_mesh, material=shelf))
        for panel_x in (DESK_CENTER_X - 1.34, DESK_CENTER_X + 1.34):
            self.add_child(Object3D(position=(panel_x, 2.35, SHELF_Z), scale_values=(0.12, 1.9, 0.75), mesh=cube_mesh, material=shelf))
        for shelf_y in (2.0, 2.7):
            self.add_child(Object3D(position=(DESK_CENTER_X, shelf_y, SHELF_Z), scale_values=(2.7, 0.1, 0.75), mesh=cube_mesh, material=shelf))
        self.add_child(Object3D(position=(DESK_CENTER_X, 3.25, SHELF_Z), scale_values=(2.7, 0.12, 0.75), mesh=cube_mesh, material=shelf))

        color_index = 0
        for surface_y, books in SHELF_BOOKS:
            for offset_x, width, height, lean in books:
                lift = 0.03 if lean != 0.0 else 0.0
                self.add_child(
                    Book(
                        cube_mesh,
                        position=(DESK_CENTER_X + offset_x, surface_y + height * 0.5 + lift, SHELF_Z),
                        size=(width, height, 0.40),
                        color=settings.BOOK_COLORS[color_index % len(settings.BOOK_COLORS)],
                        rotation=(0.0, 0.0, lean),
                    )
                )
                color_index += 1

        for stack_y, size, yaw in DESK_STACK:
            self.add_child(
                Book(
                    cube_mesh,
                    position=(DESK_CENTER_X - 0.9, stack_y, -6.65),
                    size=size,
                    color=settings.BOOK_COLORS[color_index % len(settings.BOOK_COLORS)],
                    rotation=(0.0, yaw, 0.0),
                )
            )
            color_index += 1
