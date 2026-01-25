from pathlib import Path
from typing import Iterator
from watchfiles import watch
from enum import Enum, auto
import json
import subprocess

class SurveyMode(Enum):
    Boxel = auto()
    Density = auto()
    Idle = auto()

survey_mode: SurveyMode = SurveyMode.Boxel

LOG_DIRECTORY = Path("/home/***REMOVED***/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous/")
WL_COPY_BIN_PATH = Path("/home/***REMOVED***/Documents/Programming/wl-clipboard-rs/target/debug/wl-copy")

def text_to_clipboard(text: str) -> None:
    ##print("text: ", text) ##uncomment for simple debugging
    subprocess.check_call([WL_COPY_BIN_PATH, "--", text])

def read_system_list() -> list[str]:
    with open("systemlist") as f:
        return f.read().split("\n")

log_paths: Iterator[Path] = LOG_DIRECTORY.glob("Journal.*.log")

latest_log_path: Path | None = None
for path in log_paths:
    if latest_log_path is None:
        latest_log_path = path
    latest_log_path = max(latest_log_path, path)

print(latest_log_path)

system_list: list[str] = read_system_list()
next_system: str = system_list.pop(0)
text_to_clipboard(next_system)

with open(latest_log_path) as file:
    file.read()
    for changes in watch(latest_log_path):
        for line in file.read().strip().split("\n"):
            if not line: 
                continue
            event = json.loads(line)
            print(event["event"])
            match event["event"]:
                case "Shutdown":
                    exit()
                case "StartJump":
                    if survey_mode == SurveyMode.Idle and not next_system:
                        system_list = read_system_list()
                        next_system = system_list.pop()
                        if next_system:
                            survey_mode = SurveyMode.Boxel
                            text_to_clipboard(next_system)
                            print("Next Boxel Survey System: ", next_system)

                case "FSDJump":
                    print("Jumped to system:", event["StarSystem"])
                    match survey_mode:
                        case SurveyMode.Boxel:
                            if next_system.lower() == event["StarSystem"].lower():
                                open("systemlist", "w").write("\n".join(system_list))
                                if not system_list:
                                    survey_mode = SurveyMode.Idle
                                    print("Boxel Survey Completed!")
                                    break
                                open("boxel_log", "wa").write(next_system + "\n")
                                next_system = system_list.pop(0)
                                text_to_clipboard(next_system)
                                print("Next Boxel Survey System: ", next_system)

                        case SurveyMode.Density:
                            coordinates_and_system = f'{event["StarPos"][0]}\t{event["StarPos"][1]}\t{event["StarPos"][2]}\t{event["StarSystem"]}'
                            text_to_clipboard(coordinates_and_system)
                        case SurveyMode.Idle:
                            continue
                