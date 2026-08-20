from config import settings
from rendering.material import Material
from scene.object3d import Object3D

FRAME_DEPTH = 0.18
# Rails and jambs lap a hair over the opening so their faces never land exactly
# on the wall reveal planes.
FRAME_INSET = 0.012
FRAME_X = settings.LEFT_WALL_X + 0.12
MULLION_DEPTH = 0.14
MULLION_WIDTH = 0.10
GLASS_X = settings.LEFT_WALL_X + 0.01
GLASS_THICKNESS = 0.03
# The pane runs slightly past the opening so its edges end up buried in the
# wall instead of sitting coplanar with the reveal faces and z-fighting.
GLASS_OVERLAP = 0.03


class GlassWindow(Object3D):
    """Glass window set into the left wall.

    The opaque frame lives in the normal object tree, while the glass pane and
    the exterior backdrop are exposed separately so the renderer can draw them
    in the blended and unlit passes respectively.
    """

    def __init__(self, cube_mesh):
        super().__init__()

        y_min, y_max = settings.WINDOW_Y_MIN, settings.WINDOW_Y_MAX
        z_min, z_max = settings.WINDOW_Z_MIN, settings.WINDOW_Z_MAX
        center_y = (y_min + y_max) / 2.0
        center_z = (z_min + z_max) / 2.0
        opening_height = y_max - y_min
        opening_width = z_max - z_min
        rail_width = opening_width + 2.0 * FRAME_DEPTH

        metal = Material(settings.WINDOW_FRAME_COLOR, specular_strength=0.70, shininess=96.0)
        wood = Material(settings.WINDOW_SILL_COLOR, specular_strength=0.30, shininess=36.0)
        glass = Material(
            settings.GLASS_COLOR,
            specular_strength=0.95,
            shininess=160.0,
            alpha=settings.GLASS_ALPHA,
        )

        rail_offset = FRAME_DEPTH / 2.0 - FRAME_INSET
        self.add_child(Object3D(position=(FRAME_X, y_min - rail_offset, center_z), scale_values=(FRAME_DEPTH, FRAME_DEPTH, rail_width), mesh=cube_mesh, material=metal))
        self.add_child(Object3D(position=(FRAME_X, y_max + rail_offset, center_z), scale_values=(FRAME_DEPTH, FRAME_DEPTH, rail_width), mesh=cube_mesh, material=metal))
        for jamb_z in (z_min - rail_offset, z_max + rail_offset):
            self.add_child(Object3D(position=(FRAME_X, center_y, jamb_z), scale_values=(FRAME_DEPTH, opening_height, FRAME_DEPTH), mesh=cube_mesh, material=metal))

        # Mullion cross splits the opening into four panes.
        self.add_child(Object3D(position=(FRAME_X, center_y, center_z), scale_values=(MULLION_DEPTH, opening_height, MULLION_WIDTH), mesh=cube_mesh, material=metal))
        self.add_child(Object3D(position=(FRAME_X, center_y, center_z), scale_values=(MULLION_DEPTH, MULLION_WIDTH, opening_width), mesh=cube_mesh, material=metal))

        self.add_child(Object3D(position=(settings.LEFT_WALL_X + 0.30, y_min - FRAME_DEPTH - 0.04, center_z), scale_values=(0.62, 0.08, rail_width + 0.14), mesh=cube_mesh, material=wood))

        self.glass = Object3D(
            position=(GLASS_X, center_y, center_z),
            scale_values=(GLASS_THICKNESS, opening_height + 2.0 * GLASS_OVERLAP, opening_width + 2.0 * GLASS_OVERLAP),
            mesh=cube_mesh,
            material=glass,
        )

        # Bright panels behind the wall so the opening reads as daylight and a
        # distant horizon rather than empty background.
        sky = Material(settings.SKY_COLOR)
        ground = Material(settings.EXTERIOR_GROUND_COLOR)
        self.exterior_panels = [
            Object3D(position=(settings.LEFT_WALL_X - 0.75, center_y, center_z), scale_values=(0.12, 7.0, 11.0), mesh=cube_mesh, material=sky),
            Object3D(position=(settings.LEFT_WALL_X - 0.68, 0.30, center_z), scale_values=(0.10, 3.4, 11.0), mesh=cube_mesh, material=ground),
        ]
