from dataclasses import dataclass


@dataclass
class PointLight:
    position: tuple[float, float, float]
    constant: float
    linear: float
    quadratic: float
    ambient: tuple[float, float, float]
    diffuse: tuple[float, float, float]
    specular: tuple[float, float, float]
