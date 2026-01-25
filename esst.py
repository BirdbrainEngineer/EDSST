### Elite Stellar Survey Tools v0.0.2

from pathlib import Path
from typing import Iterator
from watchfiles import watch
import json

from src.program import BoxelSurvey, CoreProgram, DensityColumnSurvey, Program


LOG_DIRECTORY = Path("/home/***REMOVED***/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous/")

log_paths: Iterator[Path] = LOG_DIRECTORY.glob("Journal.*.log")

latest_log_path: Path | None = None
for path in log_paths:
    if latest_log_path is None:
        latest_log_path = path
    latest_log_path = max(latest_log_path, path)

##print(latest_log_path)

programs: list[Program] = []
programs.append(CoreProgram())
programs.append(BoxelSurvey(programs[0]))
programs.append(DensityColumnSurvey())

if not latest_log_path:
     exit("No valid log file found!")

print("Elite Stellar Survey Tools successfully booted.")

with open(latest_log_path) as file:
    ##parse through the logfile
    for line in file.read().strip().split("\n"):
            if not line: 
                continue
            event = json.loads(line)
            for program in programs:
                 program.process_initial_event(event)
            
    
    ##start listening to the logfile
    for changes in watch(latest_log_path):
        for line in file.read().strip().split("\n"):
            if not line: 
                continue
            event = json.loads(line)
            for program in programs:
                if program.active:
                    program.process_event(event)
                