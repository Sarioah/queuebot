"""
Tools used in utility scripts
"""

from subprocess import check_output, STDOUT, CalledProcessError, TimeoutExpired


def valid_command(command):
    """
    Checks if a command runs in the shell without error or timeout

    :param command: command to attempt running
    :returns: True if command ran without issue
    """
    try:
        check_output(command, shell=True, stderr=STDOUT, timeout=0.1)
    except (CalledProcessError, TimeoutExpired):
        return False
    return True
