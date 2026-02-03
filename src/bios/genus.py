from typing import Any
from src.modules.core import Bodies
from src.bios.species import Species
#from src.util import AtmosphereType, StarType, PlanetType


class Genus:
    name: str = "UNKNOWN GENUS"
    code: str
    species: list[Species]
    colony_range: int

    def list_possible_species(self, star_system: Bodies, planet: dict[str, Any]) -> list[Species]:
        result: list[Species] = []
        for organism in self.species:
            if organism.check_viability(star_system, planet):
                result.append(organism)
        return result
    
    def check_if_gravity_less_than(self, planet: dict[str, Any], g: float) -> bool:
        if (float(planet["SurfaceGravity"]) / 9.8) < g:
            return True
        else:
            return False
