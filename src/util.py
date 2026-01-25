from pathlib import Path
import subprocess

WL_COPY_BIN_PATH = Path("/home/***REMOVED***/Documents/Programming/wl-clipboard-rs/target/debug/wl-copy")

def text_to_clipboard(text: str) -> None:
    ##print("text: ", text) ##uncomment for simple debugging
    subprocess.check_call([WL_COPY_BIN_PATH, "--", text])


def read_file_by_lines(file: Path) -> list[str]:
    with open(file) as f:
        return f.read().split("\n")


def reserialize_file(path: Path, contents: list[str]) -> None:
    open(path, "w").write("\n".join(contents))