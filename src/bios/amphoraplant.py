from typing import Any
from src.modules.core import Bodies, BodyAttribute
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, StarType#, PlanetType

class Amphora(Genus):
    name: str = "Amphora"
    code: str = "AMP"
    colony_range = 100
    species: list[Species] = []

    def __init__(self):
        self.species.append(AmphoraPlant())


class AmphoraPlant(Species):
    value: int = 0
    name: str = "Plant"
    code: str = "AMPPLA"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NONE]
    star_types: list[StarType] = [StarType("A", -1, "All")]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            needed_planets_in_system = star_system.get_bodies_by_attribute(
                BodyAttribute.ammonia_world_body,
                BodyAttribute.earth_like_world_body,
                BodyAttribute.gas_giant_ammonia_with_life,
                BodyAttribute.gas_giant_water_with_life,
                BodyAttribute.gas_giant_water)
            if len(needed_planets_in_system) == 0:
                return False
            else:
                return True
        else:
            return False