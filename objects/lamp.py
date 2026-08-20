from config import settings
from rendering.material import Material
from scene.object3d import Object3D


class Lamp(Object3D):
    """Emissive ceiling fixture marking the main room light."""

    def __init__(self, cylinder_mesh):
        super().__init__(
            position=settings.POINT_LIGHT_POSITION,
            scale_values=settings.POINT_LIGHT_MARKER_SCALE,
            mesh=cylinder_mesh,
            material=Material(settings.LAMP_COLOR),
        )
