### Elite Stellar Survey Tools v0.0.3

from pathlib import Path
from typing import Iterator
from watchfiles import awatch # pyright: ignore[reportUnknownVariableType]
import json
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

from src.program import CoreProgram, FSSReporter, BoxelSurvey, DensityColumnSurvey, Program


LOG_DIRECTORY = Path("/home/***REMOVED***/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous/")

core_program = CoreProgram()
programs: list[Program] = []
programs.append(core_program)
programs.append(FSSReporter(core_program))
programs.append(BoxelSurvey(core_program))
programs.append(DensityColumnSurvey())

programs[1].enable()


async def event_loop():
    log_paths: Iterator[Path] = LOG_DIRECTORY.glob("Journal.*.log")

    latest_log_path: Path | None = None
    for path in log_paths:
        if latest_log_path is None:
            latest_log_path = path
        latest_log_path = max(latest_log_path, path)
    
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
                    program.process_past_event(event)
                
        
        ##start listening to the logfile
        async for changes in awatch(latest_log_path):
            del changes
            for line in file.read().strip().split("\n"):
                if not line: 
                    continue
                event = json.loads(line)
                for program in programs:
                    if program.active:
                        program.process_event(event)

async def input_loop():
    session = PromptSession() # pyright: ignore[reportUnknownVariableType]
    while True:
        with patch_stdout():
            result = await session.prompt_async("Say something: ") # pyright: ignore[reportUnknownVariableType]
        for program in programs:
            program.process_user_input(str(result)) # pyright: ignore[reportUnknownArgumentType]

async def main():
    await asyncio.gather(event_loop(), input_loop())

asyncio.run(main())