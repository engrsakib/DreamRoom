from dataclasses import dataclass


@dataclass
class Material:
    color: tuple[float, float, float]
    specular_strength: float = 0.3
    shininess: float = 32.0
    tiled: bool = False
    tile_size: float = 1.0
    alpha: float = 1.0
