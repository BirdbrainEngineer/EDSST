from typing import Any
from src.modules.core import Bodies, BodyAttribute
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import distance_from_parent_ls
from src.util import AtmosphereType, StarType#, PlanetType

class Crystalline(Genus):
    name: str = "Crystalline"
    code = "CRY"
    colony_range = 100
    species: list[Species] = []

    def __init__(self):
        self.species.append(Shard())


class Shard(Species):
    value: int = 3626400
    name: str = "Shard"
    code: str = "CRYSHA"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NONE]
    star_types: list[StarType] = [
        StarType("A", -1, "All"),
        StarType("F", -1, "All"),
        StarType("G", -1, "All"),
        StarType("K", -1, "All"),
        StarType("M", -1, "All"),
        StarType("S", -1, "All"),
    ]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if super().check_viability(star_system, planet):
            if distance_from_parent_ls(planet["SemiMajorAxis"], planet["Eccentricity"], planet["MeanAnomaly"]) > 12000:
                planet_query = star_system.get_bodies_by_attribute(
                    BodyAttribute.icy_body, 
                    BodyAttribute.ammonia_world_body,
                    BodyAttribute.gas_giant_water_with_life,
                    BodyAttribute.gas_giant_ammonia_with_life,
                    BodyAttribute.gas_giant_water
                )
                if planet_query:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False