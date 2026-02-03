from typing import Any
from src.modules.core import Bodies, BodyAttribute
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType, PlanetType#, StarType

class Electricae(Genus):
    name: str = "Electricae"
    code = "ELE"
    colony_range = 1000
    species: list[Species] = []

    def __init__(self):
        self.species.append(Pluma())
    
    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        if self.check_if_gravity_less_than(planet, 0.27):
            return super().list_possible_species(star_system, planet)
        else:
            return []


class Pluma(Species):
    value: int = 6284600
    name: str = "Pluma"
    code: str = "ELEPLU"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.He, AtmosphereType.Ne, AtmosphereType.Ar]
    planet_types: list[PlanetType] = [PlanetType.I]
    allowed_startypes: list[str] = ["a", "o", "b", "black hole", "d", "da", "dab", "dao", "dav", "daz", "db", "dbv", "dc", "dcv", "do", "dov", "dq", "dx"]
    disallowed_luminosities: list[str] = ["vi", "vii"]

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        stars = star_system.get_bodies_by_attribute(BodyAttribute.star)
        for star in stars:
            if star["Luminosity"] in self.disallowed_luminosities:
                return False
            else:
                if star["StarType"] in self.allowed_startypes:
                    return True
                else:
                    return False
        else:
            return False
        

# because Radialem only appears in nebulae, then it will be handled separately elsewhere.
class Radialem(Species):
    value: int = 6284600
    name: str = "Radialem"
    code: str = "ELERAD"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.He, AtmosphereType.Ne, AtmosphereType.Ar]
    planet_types: list[PlanetType] = [PlanetType.I]