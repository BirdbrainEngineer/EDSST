from src.modules.core import Bodies
from typing import Any
from src.util import AtmosphereType, StarType, PlanetType
from src.modules.core import BodyAttribute
from src.version import TESTING_MODE, TestingMode


class Species:
    value: int = 0
    name: str = "UNKNOWN SPECIES"
    code: str = "N/A"
    atmosphere_types: list[AtmosphereType] = []
    min_max_temperature: tuple[int, int] = (0, 0)
    star_types: list[StarType] = []
    planet_types: list[PlanetType] = []

    def check_viability(self, star_system: Bodies, planet: dict[str, Any]) -> bool:
        if self.planet_types:
            valid_planet: bool = False
            for planet_type in self.planet_types:
                if planet_type == PlanetType(planet["PlanetClass"]):
                    valid_planet = True
                    break
            if not valid_planet:
                if TESTING_MODE == TestingMode.Testing: print(f"Rejected {self.code} because of planet type")
                return False
            
        if self.atmosphere_types:
            if AtmosphereType.ANY in self.atmosphere_types and AtmosphereType(planet["AtmosphereType"]) != AtmosphereType.NONE:
                pass
            else:
                valid_atmosphere: bool = False
                for atmosphere in self.atmosphere_types:
                    if atmosphere == AtmosphereType(planet["AtmosphereType"]):
                        valid_atmosphere = True
                        break
                if not valid_atmosphere:
                    if TESTING_MODE == TestingMode.Testing: print(f"Rejected {self.code} because of atmosphere type")
                    return False
            
        if self.star_types:
            valid_star_type: bool = False
            stars_in_system = star_system.get_bodies_by_attribute(BodyAttribute.star)
            for star_type in self.star_types:
                for star in stars_in_system:
                    if star_type.spectral_class == star["StarType"]:
                        if star_type.luminosity == star["Luminosity"] or star_type.luminosity == "All":
                            if star_type.subclass < 0:
                                if star_type.subclass == star["Subclass"]:
                                    valid_star_type = True
                                    break
                            else:
                                valid_star_type = True
                                break
            if not valid_star_type:
                if TESTING_MODE == TestingMode.Testing: print(f"Rejected {self.code} because of star type")
                return False

        planet_surface_temperature = int(planet["SurfaceTemperature"])
        min_temperature, max_temperature = self.min_max_temperature
        if min_temperature == 0 and max_temperature == 0:
            return True
        if min_temperature == max_temperature:
            if min_temperature < 0:
                if planet_surface_temperature <= abs(min_temperature):
                    return True
            else:
                if planet_surface_temperature >= min_temperature:
                    return True
        else:
            if planet_surface_temperature >= min_temperature and planet_surface_temperature < max_temperature:
                return True
        if TESTING_MODE == TestingMode.Testing: print(f"Rejected {self.code} because of temperature")
        return False
    
    def check_if_gravity_less_than(self, planet: dict[str, Any], g: float) -> bool:
        if (float(planet["SurfaceGravity"]) / 9.8) < g:
            return True
        else:
            return False