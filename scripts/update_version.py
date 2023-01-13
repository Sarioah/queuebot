"""Helper script to manage bot version number."""

import subprocess


def update_version():
    """Generate file containting bot version number as per git.

    Check current bot version using git, then generate a file
    that the main function can load later.
    """
    version = (
        subprocess.check_output("git describe --tags".split())
        .decode(encoding="utf-8")
        .replace("\n", "")
    )
    with open("./version.txt", "w", encoding="utf-8") as _fd:
        _fd.write(version)


if __name__ == "__main__":
    update_version()
