class Highlighter:
    def __init__(self, emote=False, string='', substrings=None, indices=None):
        self.string = string
        substrings = substrings if substrings is not None else []
        indices = indices if indices is not None else []
        indices += list(set(
            find_strings(string, substrings)
        ))
        if emote:
            indices = [index for index in indices if _is_emote(string, index)]
        self.indices = list(set(indices))

    def get_highlight(self):
        return _highlight(self.string, self.indices)

    def get_string(self):
        return self.string


def _highlight(string, positions):
    exploded_string = list(string)
    for i in sorted(positions, reverse=True):
        exploded_string.insert(i[1], '\33[0m')
        exploded_string.insert(i[0], '\33[36;2m')
    return "".join(exploded_string)


def _calc_indices(string, search, padding=0):
    length = len(search)
    try:
        position = string.index(search)
        start, end = padding + position, padding + position + length
        return (
            [(start, end)] + _calc_indices(string[position + length:], search, end)
        )
    except ValueError:
        return []


def _is_emote(string, pos):
    start = int(pos[0]) == 0 or string[pos[0] - 1:pos[0]] == " "
    end = int(pos[1]) == len(string) or string[pos[1]:pos[1] + 1] == " "
    return start and end


def find_strings(string, substrings):
    return sorted(
        sum(
            (_calc_indices(string, sub) for sub in substrings), start=[]
        )
    )


if __name__ == "__main__":
    import sys
    print(
        Highlighter(True, sys.argv[1], sys.argv[2:], [(0, 3)]).get_highlight()
    )
