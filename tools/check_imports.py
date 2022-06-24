"""Checks to ensure the system has the right modules installed to run the bot"""
# TODO: Replace with a venv or other similar semi-automatic dependency handling strategy
import sys
import os
import importlib

modules = [
        "colorama", "readchar", "irc",
        "nuitka", "keyring", "aiohttp"
        ]
if os.name == "nt":
    modules += ["win32api"]
else:
    modules += ["sagecipher"]


def check_module(module):
    """Attempt to import a module, return True if module imports without error"""
    try:
        importlib.import_module(module)
    except ModuleNotFoundError:
        return False
    else:
        return True


if __name__ == "__main__":
    failures = [
        module for module in modules
        if not check_module(module)
    ]
    if failures:
        if "win32api" in failures:
            failures[failures.index("win32api")] = "pywin32"
        print(
            f"Module(s) \"{', '.join(failures)}\" not found, "
            + "please install via pip"
        )
        sys.exit(1)
