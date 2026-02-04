from pathlib import Path
import subprocess
import pyperclip
import toml
from enum import Enum#, auto
import math


config = toml.load("config.toml")

LOGS_DIRECTORY = Path(config["elite_dangerous_journal_path"])

WL_COPY_BIN_PATH: None | Path = Path(config["wl_copy_bin_path"]) if "wl_copy_bin_path" in config else None

EDSST_EVENTS: list[str] = ["CaughtUp"]

class AtmosphereType(Enum):
    Si_V =     "SilicateVapour"
    Si_VR =    "SilicateVapourRich"
    O2 =            "Oxygen"
    O2_R =          "OxygenRich"
    NH3 =           "Ammonia"
    NH3_R =         "AmmoniaRich"
    CO2 =           "CarbonDioxide"
    CO2_R =         "CarbonDioxideRich"
    N2 =            "Nitrogen"
    N2_R =          "NitrogenRich"
    CH4 =           "Methane"
    CH4_R =         "MethaneRich"
    H2O =           "Water"
    H2O_R =         "WaterRich"
    SO2 =           "SulphurDioxide"
    SO2_R =         "SulphurDioxideRich"
    Ne =       "Neon"
    Ne_R =     "NeonRich"
    Ar =       "Argon"
    Ar_R =     "ArgonRich"
    He =       "Helium"
    He_R =     "HeliumRich"
    NONE =          "None"
    ANY =           "Any"

class PlanetType(Enum):
    I =         "Icy body"
    RI =        "Rocky ice body"
    R =         "Rocky body"
    MR =        "Metal rich body"
    HMC =       "High metal content body"
    ELW =       "Earthlike body"
    AW =        "Ammonia world"
    WW =        "Water world"
    GG_I =      "Sudarsky class I gas giant"
    GG_II =     "Sudarsky class II gas giant"
    GG_III =    "Sudarsky class III gas giant"
    GG_IV =     "Sudarsky class IV gas giant"
    GG_V =      "Sudarsky class V gas giant"
    GG_WBL =    "Gas giant with water based life"
    GG_ABL =    "Gas giant with ammonia based life"
    GG_W =      "Water giant"
    GG_HR =     "Helium-rich"
    GG_H =      "Helium gas giant"
    NONE = ""


class StarType():
    spectral_class: str
    subclass: int
    luminosity: str

    def __init__(self, spectral_class: str, subclass: int, luminosity: str):
        self.spectral_class = spectral_class
        self.subclass = subclass
        self.luminosity = luminosity



def text_to_clipboard(text: str) -> None:
    if WL_COPY_BIN_PATH is not None:
        subprocess.check_call([WL_COPY_BIN_PATH, "--", text])
    else:
        pyperclip.copy(text)

def read_file_by_lines(file: Path) -> list[str]:
    with open(file) as f:
        return f.read().split("\n")

def reserialize_file(path: Path, contents: list[str]) -> None:
    open(path, "w").write("\n".join(contents))

def distance_from_parent_ls(semi_major_axis: float, eccentricity: float, mean_anomaly_deg: float) -> float:
    # Thank you, AI overlords...
    # Convert mean anomaly to radians
    mean_anomaly_radians = math.radians(mean_anomaly_deg)
    # Solve Kepler's equation for Eccentric Anomaly (E)
    # M = E - e*sin(E)
    # Using Newton-Raphson iteration
    eccentric_anomaly = mean_anomaly_radians  # Initial guess
    tolerance = 1e-10
    max_iterations = 100
    
    for i in range(max_iterations): # pyright: ignore[reportUnusedVariable]
        f = eccentric_anomaly - eccentricity * math.sin(eccentric_anomaly) - mean_anomaly_radians
        f_prime = 1 - eccentricity * math.cos(eccentric_anomaly)
        E_new = eccentric_anomaly - f / f_prime
        
        if abs(E_new - eccentric_anomaly) < tolerance:
            eccentric_anomaly = E_new
            break
        eccentric_anomaly = E_new
    # Convert Eccentric Anomaly to True Anomaly (nu)
    # tan(nu/2) = sqrt((1+e)/(1-e)) * tan(E/2)
    true_anomaly = 2 * math.atan2(
        math.sqrt(1 + eccentricity) * math.sin(eccentric_anomaly / 2),
        math.sqrt(1 - eccentricity) * math.cos(eccentric_anomaly / 2)
    )
    # Calculate distance using orbit equation
    # r = a(1 - e²) / (1 + e*cos(nu))
    r = semi_major_axis * (1 - eccentricity**2) / (1 + eccentricity * math.cos(true_anomaly))
    r = r / 299792458
    return r

def abbreviate_planet_type(planet_type: str) -> str:    # EDSST planet type abbreviations
    match planet_type:
        case "Icy body":                                return "I"
        case "Rocky ice body":                          return "RI"
        case "Rocky body":                              return "R"
        case "Metal rich body":                         return "MR"
        case "High metal content body":                 return "HMC"
        case "Earthlike body":                          return "ELW"
        case "Ammonia world":                           return "AW"
        case "Water world":                             return "WW"
        case "Sudarsky class I gas giant":              return "GG I"
        case "Sudarsky class II gas giant":             return "GG II"
        case "Sudarsky class III gas giant":            return "GG III"
        case "Sudarsky class IV gas giant":             return "GG IV"
        case "Sudarsky class V gas giant":              return "GG V"
        case "Gas giant with water based life":         return "GG WBL"
        case "Gas giant with ammonia based life":       return "GG ABL"
        case "Water giant":                             return "GG W"
        case "Helium-rich":                             return "GG HR"
        case "Helium gas giant":                        return "GG H"
        case _: return planet_type

def abbreviate_atmosphere_type(atmosphere_type: str) -> str:
    match atmosphere_type:
        case "SilicateVapour":          return "Si-V"
        case "SilicateVapourRich":      return "Si-VR"
        case "Oxygen":                  return "O2"
        case "OxygenRich":              return "O2-R"
        case "Ammonia":                 return "NH3"
        case "AmmoniaRich":             return "NH3-R"
        case "CarbonDioxide":           return "CO2"
        case "CarbonDioxideRich":       return "CO2-R"
        case "Nitrogen":                return "N2"
        case "NitrogenRich":            return "N2-R"
        case "Methane":                 return "CH4"
        case "MethaneRich":             return "CH4-R"
        case "Water":                   return "H2O"
        case "WaterRich":               return "H2O-R"
        case "SulphurDioxide":          return "SO2"
        case "SulphurDioxideRich":      return "SO2-R"
        case "Neon":                    return "Ne"
        case "NeonRich":                return "Ne-R"
        case "Argon":                   return "Ar"
        case "ArgonRich":               return "Ar-R"
        case "Helium":                  return "He"
        case "HeliumRich":              return "He-R"
        case _:                         return atmosphere_type


