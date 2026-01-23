import unittest


from tools import highlight_string


# ruff: noqa: D101, D102
class TestHighlightFunctions(unittest.TestCase):

    def test_highlighter(self):
        test_string = "aa bb baab aa daa bb aad abba"
        highlighter = highlight_string.Highlighter(
            True, test_string, substrings=["aa", "bb"]
        )
        self.assertEqual(highlighter.get_string(), test_string)
        self.assertEqual(
            highlighter.get_highlight(),
            "\x1b[36;1maa\x1b[0m \x1b[36;1mbb\x1b[0m baab "
            "\x1b[36;1maa\x1b[0m daa \x1b[36;1mbb\x1b[0m aad abba",
        )
        highlighter = highlight_string.Highlighter(
            False, test_string, substrings=["aa", "bb"]
        )
        self.assertEqual(highlighter.get_string(), test_string)
        self.assertEqual(
            highlighter.get_highlight(),
            "\x1b[36;1maa\x1b[0m \x1b[36;1mbb\x1b[0m b\x1b[36;1maa\x1b[0mb "
            "\x1b[36;1maa\x1b[0m d\x1b[36;1maa\x1b[0m \x1b[36;1mbb\x1b[0m "
            "\x1b[36;1maa\x1b[0md a\x1b[36;1mbb\x1b[0ma",
        )
        highlighter = highlight_string.Highlighter(
            True, test_string, indices=[(2, 4), (6, 15)]
        )
        self.assertEqual(highlighter.get_string(), test_string)
        self.assertEqual(highlighter.get_highlight(), test_string)

        highlighter = highlight_string.Highlighter(
            False, test_string, indices=[(2, 4), (6, 15)]
        )
        self.assertEqual(highlighter.get_string(), test_string)
        self.assertEqual(
            highlighter.get_highlight(),
            "aa\x1b[36;1m b\x1b[0mb \x1b[36;1mbaab aa d\x1b[0maa bb aad abba",
        )

        highlighter = highlight_string.Highlighter(
            True,
            test_string,
            indices=[
                (0, 2),
                (3, 5),
                (7, 9),
                (11, 13),
                (15, 17),
                (18, 20),
                (21, 23),
                (26, 28),
            ],
        )
        self.assertEqual(highlighter.get_string(), test_string)
        self.assertEqual(
            highlighter.get_highlight(),
            "\x1b[36;1maa\x1b[0m \x1b[36;1mbb\x1b[0m baab "
            "\x1b[36;1maa\x1b[0m daa \x1b[36;1mbb\x1b[0m aad abba",
        )

    def test_highlight(self):
        res = highlight_string._highlight(
            "aa bb baab aa daa bb aad abba",
            [
                (0, 2),
                (3, 5),
                (7, 9),
                (11, 13),
                (15, 17),
                (18, 20),
                (21, 23),
                (26, 28),
            ],
        )
        self.assertEqual(
            res,
            "\x1b[36;1maa\x1b[0m \x1b[36;1mbb\x1b[0m b\x1b[36;1maa\x1b[0mb "
            "\x1b[36;1maa\x1b[0m d\x1b[36;1maa\x1b[0m \x1b[36;1mbb\x1b[0m "
            "\x1b[36;1maa\x1b[0md a\x1b[36;1mbb\x1b[0ma",
        )

    def test_calc_indices(self):
        self.assertEqual(
            highlight_string._calc_indices("aa bb baab daa aad abba", "aa"),
            [(0, 2), (7, 9), (12, 14), (15, 17)],
        )
        self.assertEqual(highlight_string._calc_indices("", "aa"), [])
        self.assertRaises(
            ValueError, highlight_string._calc_indices, "aa bb baab daa aad abba", ""
        )

    def test_is_emote(self):
        test_string = "This is a test string"
        res = [
            ((x, y), test_string[x:y], emote)
            for x in range(len(test_string) + 1)
            for y in range(len(test_string) + 1)
            if (emote := highlight_string._is_emote(test_string, (x, y)))
        ]
        self.assertEqual(
            res,
            [
                ((0, 4), "This", True),
                ((5, 7), "is", True),
                ((8, 9), "a", True),
                ((10, 14), "test", True),
                ((15, 21), "string", True),
            ],
        )

    def test_find_strings(self):
        self.assertEqual(
            highlight_string.find_strings(
                "aa bb baab aa daa bb aad abba", ["aa", "bb"]
            ),
            [(0, 2), (3, 5), (7, 9), (11, 13), (15, 17), (18, 20), (21, 23), (26, 28)],
        )
