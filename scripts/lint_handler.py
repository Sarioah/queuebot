#!/usr/bin/python3
"""
Script to help co-ordinate linters and their options
"""

import os
import argparse

from subprocess import call

from .script_tools import valid_command


def fmt_heading(heading):
    """
    Format a string as a heading, colouring it and
    spacing it above and below with lines

    :param heading: string to format
    :returns: formatted string
    """
    col01 = "\33[36;2m"
    col02 = "\33[36;1m"
    reset = "\33[0m"

    lines = f"{col01}{'-' * (len(heading) + 3)}{reset}"
    return f"{lines}\n{col02}{heading}...{reset}\n{lines}"


def valid_file(path):
    """
    Checks if a filepath is one we care about

    Must be a .py file, must not be part of the exclusions list

    :param path: path to the file
    :returns: True if file is valid
    """
    if any(
        [
            path.startswith(SETTINGS["exclusions"]),
            os.path.splitext(path)[1] != ".py",
        ]
    ):
        return False
    return True


def find_files():
    """
    Search current directory and subdirectories for files

    :returns: list of file paths for discovered files
    """
    return [
        path
        for entry in os.walk("./")
        for filename in entry[2]
        if valid_file((path := os.path.join(entry[0], filename)))
    ]


def process_args():
    """
    Set up the ArgumentParser with the desired switches / parameters

    :returns Namespace: holds the results of parsing the script arguments
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
        "-t",
        "--todo",
        dest="enable_todo",
        action="store_true",
        help="enables checking for TODO entries",
    )
    return parser.parse_args()


if __name__ == "__main__":
    ARGS = process_args()
    PYTHON = "py" if valid_command("py --version") else "python3"
    SETTINGS = {
        "exclusions": "-" if ARGS.all_files else "./tests/",
        "black_opts": "--line-length 99"
        if ARGS.black_write
        else "--line-length 99 --diff --color",
        "pylint_opts": "--enable=fixme" if ARGS.enable_todo else "",
    }

    print(fmt_heading("Searching for .py files"))
    FILES = ARGS.filenames or find_files()
    for _file in FILES:
        print(f"\33[30;1m{_file}\33[0m")

    print(fmt_heading("Running black"))
    call([PYTHON, "-m", "black"] + SETTINGS["black_opts"].split() + FILES)

    print(fmt_heading("Running pylint"))
    call([PYTHON, "-m", "pylint"] + SETTINGS["pylint_opts"].split() + FILES)

    print(fmt_heading("Running flake8"))
    call([PYTHON, "-m", "flake8"] + FILES)
