from pathlib import Path
from math import sqrt
import subprocess
from typing import Any
import pyperclip
import toml
import httpx

config = toml.load("config.toml")

WL_COPY_BIN_PATH: None | Path = Path(config["wl_copy_bin_path"]) if "wl_copy_bin_path" in config else None

commander_name = config["commander_name"]
edsm_api_key = config["edsm_api_key"]

def get_edsm_bodies(system_name: str):
    r = httpx.get("https://www.edsm.net/api-system-v1/bodies", params={"systemName": system_name})
    return r.json()

def post_to_edsm(event: str):
    data: dict[str, Any] = {
        "commanderName": commander_name,
        "apiKey": edsm_api_key,
        "fromSoftware": "EDSST",
        "fromSoftwareVersion": "0.0.1",
        "fromGameVersion": "4.3.0.1",
        "fromGameBuild": "r322188/r0 ",
        "message": event
    }

    r = httpx.post("https://www.edsm.net/api-journal-v1", data=data)
    r.raise_for_status()
    code = r.json()
    print(code)
    assert isinstance(code, int)
    return code

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

def get_distance(system_a: tuple[float, float, float], system_b: tuple[float, float, float]) -> float:
    return sqrt((system_a[0] - system_b[0])**2 + (system_a[1] - system_b[1])**2 + (system_a[2] - system_b[2])**2)

def abbreviate_planet_type(planet_type: str) -> str:
    match planet_type:
        case "Icy body":                                return "I"
        case "Rocky ice body":                          return "RI"
        case "Rocky body":                              return "R"
        case "Metal rich body":                         return "MR"
        case "High metal content body":                 return "HMC"
        case "Earth-like world":                        return "ELW"
        case "Ammonia world":                           return "AW"
        case "Water world":                             return "WW"
        case "Sudarsky class I gas giant":              return "GG I"
        case "Sudarsky class II gas giant":             return "GG II"
        case "Sudarsky class II gas giant":             return "GG III"
        case "Sudarsky class IV gas giant":             return "GG IV"
        case "Sudarsky class V gas giant":              return "GG V"
        case "Gas giant with water based life":         return "GG WBL"
        case "Gas giant with ammonia based life":       return "GG ABL"
        case "Water giant":                             return "GG W"
        case "Helium-rich":                             return "GG HR"
        case "Helium gas giant":                        return "GG H"
        case _: return planet_type