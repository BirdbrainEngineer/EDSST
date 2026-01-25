### Elite Stellar Survey Tools v0.0.1

from pathlib import Path
from typing import Iterator
from watchfiles import watch
from enum import Enum, auto
from cli_color_py import yellow, bright_green, bright_blue, bright_cyan
    ##black, red, green, yellow, blue, magenta, cyan, white, bright_red, bright_green, bright_yellow, bright_blue, bright_magenta, bright_cyan
import json
import subprocess

class SurveyMode(Enum):
    Boxel = auto()
    DensityColumn = auto()
    Idle = auto()

survey_mode: SurveyMode = SurveyMode.Idle
commander_greeted = False

LOG_DIRECTORY = Path("/home/***REMOVED***/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous/")
WL_COPY_BIN_PATH = Path("/home/***REMOVED***/Documents/Programming/wl-clipboard-rs/target/debug/wl-copy")

SYSTEM_LIST_FILE = Path("systemlist")
BOXEL_LOG_FILE = Path("boxel_log")

def text_to_clipboard(text: str) -> None:
    ##print("text: ", text) ##uncomment for simple debugging
    subprocess.check_call([WL_COPY_BIN_PATH, "--", text])

def read_system_list() -> list[str]:
    with open(SYSTEM_LIST_FILE) as f:
        return f.read().split("\n")
    
def reserialize_file(path: Path, contents: list[str]) -> None:
    open(path, "w").write("\n".join(contents))

def load_next_system(system_list: list[str]) -> str:
    return system_list.pop(0)

log_paths: Iterator[Path] = LOG_DIRECTORY.glob("Journal.*.log")

latest_log_path: Path | None = None
for path in log_paths:
    if latest_log_path is None:
        latest_log_path = path
    latest_log_path = max(latest_log_path, path)

##print(latest_log_path)

current_system: str = ""
terraformables: list[str] = []
biologicals: list[tuple[str, int]] = []
geologicals: list[tuple[str, int]] = []
total_bio_signatures: int = 0
total_geo_signatures: int = 0

system_list: list[str] = read_system_list()
next_system: str = load_next_system(system_list)

print("Elite Stellar Survey Tools successfully booted.")

with open(latest_log_path) as file:
    ##parse through the logfile
    for line in file.read().strip().split("\n"):
            if not line: 
                continue
            event = json.loads(line)
            match event["event"]:
                case "Commander":
                    if not commander_greeted:
                        print("Welcome Commander " + event["Name"])
                        commander_greeted = True
                case "Shutdown":
                    print("Elite: Dangerous not launched!\nExiting.")
                    exit()
                case _: pass
    if next_system:
        text_to_clipboard(next_system)
        print("Detected ongoing Boxel suvey\nNext Boxel survey system: " + next_system)
        survey_mode = SurveyMode.Boxel
    
    ##start listening to the logfile
    for changes in watch(latest_log_path):
        for line in file.read().strip().split("\n"):
            if not line: 
                continue
            event = json.loads(line)
            print(event["event"])
            match event["event"]:
                case "Shutdown":
                    exit()
                case "FSSBodySignals":
                    for signal in event["Signals"]:
                        match signal["Type"]:
                            case "$SAA_SignalType_Biological;":
                                biological = (str(event["BodyName"]), int(signal["Count"]))
                                biologicals.append(biological)
                                total_bio_signatures += int(signal["Count"])
                            case "$SAA_SignalType_Geological;":
                                geological = (str(event["BodyName"]), int(signal["Count"]))
                                geologicals.append(geological)
                                total_geo_signatures += int(signal["Count"])
                            case _: pass
                case "Scan":
                    if "TerraformState" in event:
                        if event["TerraformState"] == "Terraformable":
                            terraformables.append(event["BodyName"])
                case "FSSAllBodiesFound":
                    print(bright_cyan("\nFull system scan complete!\n"))
                    if terraformables:
                        print(bright_blue("Terraformable planets: " + str(len(terraformables))))
                        for terraformable in terraformables:
                            print(bright_blue("\t" + terraformable))
                    if biologicals:
                        print(bright_green("Biological signatures: " + str(len(biologicals)) + " (" + str(total_bio_signatures) + ")"))
                        for biological in biologicals:
                            print(bright_green("\t" + biological[0] + ": " + str(biological[1])))
                    if geologicals:
                        print(yellow("Geological signatures: " + str(len(geologicals)) + " (" + str(total_geo_signatures) + ")"))
                        for geological in geologicals:
                            print(yellow("\t" + geological[0] + ": " + str(geological[1])))
                case "StartJump":
                    terraformables = []
                    biologicals = []
                    geologicals = []
                    total_bio_signatures = 0
                    total_geo_signatures = 0
                    if survey_mode == SurveyMode.Idle and not next_system:
                        system_list = read_system_list()
                        next_system = load_next_system(system_list)
                        if next_system:
                            survey_mode = SurveyMode.Boxel
                            text_to_clipboard(next_system)
                            print("Detected new Boxel Survey!\nNext Boxel survey system: ", next_system)

                case "FSDJump":
                    print("Jumped to system:", event["StarSystem"])
                    match survey_mode:
                        case SurveyMode.Boxel:
                            if next_system.lower() == event["StarSystem"].lower():
                                reserialize_file(SYSTEM_LIST_FILE, system_list)
                                open(BOXEL_LOG_FILE, "a").write(next_system + "\n")
                                if not system_list:
                                    survey_mode = SurveyMode.Idle
                                    print("Boxel Survey Completed!")
                                    break
                                next_system = load_next_system(system_list)
                                text_to_clipboard(next_system)
                                print("Next Boxel Survey System: ", next_system)

                        case SurveyMode.DensityColumn:
                            coordinates_and_system = f'{event["StarPos"][0]}\t{event["StarPos"][1]}\t{event["StarPos"][2]}\t{event["StarSystem"]}'
                            text_to_clipboard(coordinates_and_system)
                        case SurveyMode.Idle:
                            pass
                case _: pass
                