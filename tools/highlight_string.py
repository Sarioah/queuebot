"""
Tools to highlight a string with colour.

Classes:
    Highlighter: take a string and return a version with ANSI colour codes inserted

Functions:
    find_strings: take a string and a list of substrings, then return a list of position
                  2-tuples describing where the substrings are found in the string
"""


class Highlighter:
    """
    Take a string, emote mode flag, list of substrings and list of position indices to highlight
    then return the highlighted string.

    Methods:
        get_highlight: return the highlighted string

        get_string: return the original string without highlighting
    """

    def __init__(self, emote=False, string="", substrings=None, indices=None):
        """
        Create the Highlighter object.

        Args:
            emote: flag to treat the positions as "emotes", i.e. only highlight if the positions
                   correspond to word boundaries

            string: the input string to highlight

            substrings: list of strings to search for and highlight in the input string

            indices: list of position 2-tuples to directly highlight in the input string
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
    """
    Take a string and a list of position tuples, then return the string with ANSI colour
    codes inserted at each position.

    Args:
        string: the string to highlight

        positions: the positions to insert ANSI colour codes around

    Return the string with ANSI colour codes inserted
    """
    exploded_string = list(string)
    # Walk the exploded string in reverse, so that each insertion doesn't
    # affect the position of subsequent insertions.
    for start, reset in sorted(positions, reverse=True):
        exploded_string.insert(reset, "\33[0m")
        exploded_string.insert(start, "\33[36;2m")
    return "".join(exploded_string)


def _calc_indices(string, search, padding=0):
    """
    Take a string and search it recursively for the given substring.

    Args:
        string: the string to search in

        search: the substring to search for

    Return a list of position 2-tuples for each position the substring is found at.
    """
    length = len(search)
    try:
        position = string.index(search)
        start, end = padding + position, padding + position + length
        return [(start, end)] + _calc_indices(string[position + length :], search, end)
    except ValueError:
        return []


def _is_emote(string, pos):
    """
    Check the string at the given position for word boundaries.

    Args:
        string: the string to search within

        pos: 2-tuple with the positions to check

    Return True if the position fully describes an entire word.
    """
    start = int(pos[0]) == 0 or string[pos[0] - 1 : pos[0]] == " "
    end = int(pos[1]) == len(string) or string[pos[1] : pos[1] + 1] == " "
    return start and end


def find_strings(string, substrings):
    """
    Search the given string for occurences of the substrings.

    Args:
        string: the string to search

        substrings: list of strings to search the string for

    Return a list of position 2-tuples for every occurence of a substring
    """
    return sorted(sum((_calc_indices(string, sub) for sub in substrings), start=[]))


if __name__ == "__main__":
    import sys

    print(Highlighter(True, sys.argv[1], sys.argv[2:], [(0, 3)]).get_highlight())
