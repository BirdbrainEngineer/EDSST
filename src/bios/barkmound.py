#from typing import Any
#from src.modules.core import Bodies
from src.bios.genus import Genus
from src.bios.species import Species
from src.util import AtmosphereType#, StarType, PlanetType


# Because it is not possible to reliably know the distance to the closest nebula, this genus and species will never be handled.

class Bark(Genus):
    name: str = "Bark"
    code: str = "BAR"
    colony_range = 100
    species: list[Species] = []

class Mound(Species):
    value: int = 1471900
    name: str = "Mound"
    code: str = "BARMOU"
    atmosphere_types: list[AtmosphereType] = [AtmosphereType.NONE]