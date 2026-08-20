from dataclasses import dataclass


@dataclass
class DirectionalLight:
    direction: tuple[float, float, float]
    ambient: tuple[float, float, float]
    diffuse: tuple[float, float, float]
    specular: tuple[float, float, float]
