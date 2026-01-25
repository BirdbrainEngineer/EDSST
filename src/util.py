from pathlib import Path
import subprocess

WL_COPY_BIN_PATH = Path("/home/***REMOVED***/Documents/Programming/wl-clipboard-rs/target/debug/wl-copy")

def text_to_clipboard(text: str) -> None:
    ##print("text: ", text) ##uncomment for simple debugging
    subprocess.check_call([WL_COPY_BIN_PATH, "--", text])