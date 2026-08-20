from dataclasses import dataclass


@dataclass
class SpotLight:
    position: tuple[float, float, float]
    direction: tuple[float, float, float]
    cutoff: float
    outer_cutoff: float
    constant: float
    linear: float
    quadratic: float
    ambient: tuple[float, float, float]
    diffuse: tuple[float, float, float]
    specular: tuple[float, float, float]

    def sync_from_camera(self, camera):
        self.position = tuple(float(value) for value in camera.position)
        self.direction = tuple(float(value) for value in camera.front)
