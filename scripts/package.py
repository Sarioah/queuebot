"""Handle packaging the queuebot into a standalone executable file."""

import os
import sys
from subprocess import call

from .update_version import update_version

PLATFORM = "win" if os.name == "nt" else "linux"
PARAMETERS = {
    "base": [
        "--standalone",
        "--onefile",
        "--remove-output",
        "--include-package-data=jaraco.text",
        "--include-data-file=version.txt=version.txt",
        "--noinclude-pytest-mode=nofollow",
        "--noinclude-setuptools-mode=nofollow",
        "--noinclude-unittest-mode=nofollow",
        "--onefile-cache-mode=cached",
        "--onefile-tempdir-spec={CACHE_DIR}/resources",
    ],
    "win": [
        "--mingw64",
        r"--windows-icon-from-ico=.\robot.ico",
        "-o",
        "sari_queuebot.exe",
        r".\src\queuebot\main.py",
    ],
    "linux": [
        "--linux-onefile-icon=./robot.png",
        "-o",
        "sari_queuebot",
        "./src/queuebot/main.py",
    ],
}


def build():
    """Run nuitka with platform specific arguments to build the bot binary."""
    print("Running build tool...")
    update_version()
    call([sys.executable, "-m", "nuitka"] + PARAMETERS["base"] + PARAMETERS[PLATFORM])


if __name__ == "__main__":
    build()
