"""Tools to highlight a string with colour.

Classes:
    Highlighter: Take a string and return a version with ANSI colour codes
        inserted.

Functions:
    find_strings: Take a string and a list of substrings, then return a list of
        position 2-tuples describing where the substrings are found in the
        string.
"""

from typing import Optional

HIGHLIGHT_COLOUR = "\x1b[36;1m"
RESET_STR = "\x1b[0m"


class Highlighter:
    """Main highlighter class.

    Take a string, emote mode flag, list of substrings and list of position
    indices to highlight then return the highlighted string.

    Methods:
        get_highlight: Return the highlighted string.
        get_string: Return the original string without highlighting.
    """

    def __init__(
        self,
        emote=False,
        string="",
        substrings: Optional[list[str]] = None,
        indices: Optional[list[tuple]] = None,
    ):
        """Create the Highlighter object.

        Args:
            emote: Flag to treat the positions as "emotes", i.e. only highlight
                if the positions correspond to word boundaries.
            string: The input string to highlight.
            substrings: List of strings to search for and highlight in the
                input string.
            indices: List of position 2-tuples to directly highlight in the
                input string.
        """
        self.string = string
        substrings = substrings if substrings is not None else []
        indices = indices if indices is not None else []
        indices += list(set(find_strings(string, substrings)))
        if emote:
            indices = [index for index in indices if _is_emote(string, index)]
        self.indices = list(set(indices))

    def get_highlight(self):
        """Return the highlighted string, with ANSI colour codes inserted."""
        return _highlight(self.string, self.indices)

    def get_string(self):
        """Return the original string."""
        return self.string


def _highlight(string, positions):
    """Return string highlighted at the given positions.

    Take a string and a list of position tuples, then return the string with
    ANSI colour codes inserted at each position.

    Args:
        string: The string to highlight.
        positions: List or tuple with he positions to insert ANSI colour codes
            around.

    Returns:
        The string with ANSI colour codes inserted.
    """
    exploded_string = list(string)
    # Walk the exploded string in reverse, so that each insertion doesn't
    # affect the position of subsequent insertions.
    for start, reset in sorted(positions, reverse=True):
        exploded_string.insert(reset, RESET_STR)
        exploded_string.insert(start, HIGHLIGHT_COLOUR)
    return "".join(exploded_string)


def _calc_indices(string, search, padding=0):
    """Take a string and search it recursively for the given substring.

    Args:
        string: String to search in.
        search: Substring to search for.
        padding: Offset to add to the returned position indices.

    Returns:
        List of position 2-tuples for each position the substring is found at.
    """
    length = len(search)
    if length < 1:
        raise ValueError("Search string must have non-zero length")
    try:
        position = string.index(search)
        start, end = padding + position, padding + position + length
        return [(start, end), *_calc_indices(string[position + length :], search, end)]
    except (ValueError, RecursionError):
        return []


def _is_emote(string: str, pos: tuple):
    """Check the string at the given position for word boundaries.

    Args:
        string: String to search within.
        pos: 2-tuple with the positions to check.

    Returns:
        True if the position fully describes a single word.
    """
    start, end = pos
    first_bound = int(start) == 0 or string[start - 1 : start] == " "
    second_bound = int(end) == len(string) or string[end : end + 1] == " "
    return all([first_bound, second_bound, start < end, " " not in string[start:end]])


def find_strings(string, substrings):
    """Search the given string for occurrences of the substrings.

    Args:
        string: String to search.
        substrings: List of strings to search the string for.

    Returns:
        List of position 2-tuples for every occurrence of a substring.
    """
    return sorted(index for sub in substrings for index in _calc_indices(string, sub))


if __name__ == "__main__":
    import sys

    print(Highlighter(True, sys.argv[1], sys.argv[2:], [(0, 3)]).get_highlight())
