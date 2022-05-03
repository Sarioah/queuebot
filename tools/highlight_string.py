#!/usr/bin/python3
import sys


class highlighter():

    def __init__(self, emote=False):
        self.emote = emote

    def __call__(self, string, substrings=[], indices=[]):
        results = indices + find_strings(string, substrings)
        if self.emote:
            results = [
                    p
                    for p in results
                    if is_emote(string, p)
                    ]
        return highlight(string, results)


def highlight(string, positions):
    L = list(string)
    for i in sorted(positions, reverse=True):
        L.insert(i[1], '[0m')
        L.insert(i[0], '[36;2m')
    return "".join(L)


def substring(string, search, padding=0):
    L = len(search)
    try:
        position = string.index(search)
        start, end = padding + position, padding + position + L
        return [(start, end)] + substring(string[position + L:], search, end)
    except ValueError:
        return []


def find_strings(string, substrings):
    return sorted(sum([substring(string, s) for s in substrings], start=[]))


def highlight_string(string, substrings):
    return highlight(string, find_strings(string, substrings))


def is_emote(string, pos):
    a = int(pos[0]) == 0 or string[pos[0] - 1:pos[0]] == " "
    b = int(pos[1]) == len(string) or string[pos[1]:pos[1] + 1] == " "
    return a and b


if __name__ == "__main__":
    positions = find_strings(sys.argv[1], *sys.argv[2:])
    print(f"Strings found at positions: {positions}")
    print(highlight(sys.argv[1], positions))
    print(highlight_string(sys.argv[1], sys.argv[2:]))
