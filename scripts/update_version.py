"""Helper script to manage bot version number."""

import os
import subprocess


def update_version(path="."):
    """Generate file containing bot version number as per git.

    Check current bot version using git, then generate a file
    that the main function can load later.

    Version number is normalised and then passed to poetry to
    update the pyproject.toml.
    """
    version = (
        subprocess.check_output("git describe --tags".split())
        .decode(encoding="utf-8")
        .replace("\n", "")
    )
    segments = version.split("-")
    if len(segments) > 1:
        chunks = segments[0].split(".")
        segments[0] = f"{chunks[0]}.{chunks[1]}.{int(chunks[2])+1}"
        version = f"{segments[0]}.dev{segments[1]}+{segments[2]}"
    else:
        version = segments[0]

    with open(os.path.join(path, "version.txt"), "w", encoding="utf-8") as _fd:
        _fd.write(version)
    subprocess.call(f"poetry version {version}".split())


if __name__ == "__main__":
    update_version("..")
