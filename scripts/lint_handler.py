#!/usr/bin/python3
"""Script to help co-ordinate linters and their options."""

import os
import argparse

from subprocess import call

from .script_tools import valid_command


def fmt_heading(heading):
    """
    Format a string as a heading.

    Add colour to the provided string, then add coloured
    lines above and below to help the heading stand out

    Args:
        heading (str): string to format

    Returns:
        formatted string containing the full heading
    """
    col01 = "\33[36;2m"
    col02 = "\33[36;1m"
    reset = "\33[0m"

    lines = f"{col01}{'-' * (len(heading) + 3)}{reset}"
    return f"{lines}\n{col02}{heading}...{reset}\n{lines}"


def valid_file(path, exclusions):
    """
    Check if a filepath is one we care about.

    Must be a .py file, must not be part of the exclusions list

    Args:
        path (str): path to the file
        exclusions (str): prefix representing paths to discard

    Returns:
        True if file is valid
    """
    if any(
        [
            path.startswith(exclusions),
            os.path.splitext(path)[1] != ".py",
        ]
    ):
        return False
    return True


def find_files(exclusions):
    """
    Search current directory and subdirectories for files.

    Args:
        exclusions (str): path prefix representing files to ignore

    Returns:
        list of file paths for discovered files
    """
    return [
        path
        for entry in os.walk("./")
        for filename in entry[2]
        if valid_file((path := os.path.join(entry[0], filename)), exclusions)
    ]


def process_args():
    """
    Set up the ArgumentParser with the desired switches / parameters.

    Returns:
        Namespace holding the results of parsing the script arguments
    """
    parser = argparse.ArgumentParser(description="Linter script", add_help=True)
    parser.add_argument(
        dest="filenames",
        metavar="filename",
        nargs="*",
        help="list of filenames to search. Searches all .py files if omitted",
    )
    parser.add_argument(
        "-a",
        "--all",
        dest="all_files",
        action="store_true",
        help="include all files, including tests",
    )
    parser.add_argument(
        "-c",
        "--confirm-write",
        dest="black_write",
        action="store_true",
        help="allow black to write its changes back to file",
    )
    parser.add_argument(
        "-d",
        "--darglint",
        dest="darglint",
        action="store_true",
        help="check docstrings for proper documentation of paramaters / return values",
    )
    parser.add_argument(
        "-s",
        "--docstrings",
        dest="docstrings",
        action="store_true",
        help="check docstrings more stringently for appropriate formatting",
    )
    parser.add_argument(
        "-t",
        "--todo",
        dest="enable_todo",
        action="store_true",
        help="check code for TODO entries",
    )
    return parser.parse_args()


def process_settings(_args):
    """
    Transform arguments recieved from parser into options usable by the linting tools.

    Args:
        _args (Namespace): command line switches from argparser

    Returns:
        settings (dict): options dict
    """
    _settings = {
        "exclusions": "./tests/",
        "black_opts": "--line-length 99 --diff --color",
        "flake_opts": "--extend-ignore=",
        "pylint_opts": "",
    }

    if _args.all_files:
        _settings["exclusions"] = "-"
    if _args.black_write:
        _settings["black_opts"] = "--line-length 99"
    if not _args.darglint:
        _settings["flake_opts"] += ",DAR"
    if not _args.docstrings:
        _settings["flake_opts"] += ",D1,D2,D3,D4"
    if _args.enable_todo:
        _settings["pylint_opts"] = "--enable=fixme"

    return _settings


if __name__ == "__main__":
    args = process_args()
    PYTHON = "py" if valid_command("py --version") else "python3"
    settings = process_settings(args)

    print(fmt_heading("Searching for .py files"))
    files = args.filenames or find_files(settings["exclusions"])
    for _file in files:
        print(f"\33[30;1m{_file}\33[0m")

    print(fmt_heading("Running black"))
    call([PYTHON, "-m", "black"] + settings["black_opts"].split() + files)

    print(fmt_heading("Running pylint"))
    call([PYTHON, "-m", "pylint"] + settings["pylint_opts"].split() + files)

    print(fmt_heading("Running flake8"))
    call([PYTHON, "-m", "flake8"] + settings["flake_opts"].split() + files)
