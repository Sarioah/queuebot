import json
import unittest

import tools.text

PAGE_LENGTH = 100
STRING_LENGTH = 5
SEPARATOR = "."

with open("tests/tools/text_testdata.json", encoding="UTF-8") as fd_:
    testdata = json.load(fd_)
    DATA = testdata["inputs"]
    EXPECTED_RESULTS = testdata["expected results"]


# ruff: noqa: D101, D102
class TestPaginate(unittest.TestCase):

    def setUp(self):
        self.pag = tools.text.Paginate(DATA["very long string"], PAGE_LENGTH, SEPARATOR)

    def test_str(self):
        self.assertEqual(str(self.pag), EXPECTED_RESULTS["pages"]["long string"][0])

    def test_getitem(self):
        for page_num, page in enumerate(EXPECTED_RESULTS["pages"]["long string"]):
            failure_msg = f"Test failed on page {page_num + 1}"
            self.assertEqual(self.pag[page_num + 1], page, failure_msg)
        self.assertEqual(
            self.pag["bad index"], EXPECTED_RESULTS["pages"]["long string"][0]
        )

    def test_iter(self):
        self.assertSequenceEqual(
            list(self.pag), EXPECTED_RESULTS["pages"]["long string"]
        )

        def generate_first_pages(sep=""):
            return [
                str(tools.text.Paginate(DATA["long unicode string"], length, sep))
                for length in range(40, 70)
            ]

        self.assertSequenceEqual(
            generate_first_pages(),
            EXPECTED_RESULTS["iter"]["long unicode string"]["no seperator"],
        )
        self.assertSequenceEqual(
            generate_first_pages(" "),
            EXPECTED_RESULTS["iter"]["long unicode string"]["space"],
        )
        self.assertSequenceEqual(
            generate_first_pages(".-."),
            EXPECTED_RESULTS["iter"]["long unicode string"]["long seperator"],
        )

        def generate_all_pages(sep=""):
            return [
                [*tools.text.Paginate(DATA["long string"], length, sep)]
                for length in range(15, 35)
            ]

        self.assertSequenceEqual(
            generate_all_pages(),
            EXPECTED_RESULTS["iter"]["long string"]["no seperator"],
        )
        self.assertSequenceEqual(
            generate_all_pages(" "), EXPECTED_RESULTS["iter"]["long string"]["space"]
        )


class TestFunctions(unittest.TestCase):
    """Test the functions in the text module."""

    def test_to_string(self):
        self.assertEqual(tools.text.to_string(b"good string"), "good string")
        self.assertEqual(tools.text.to_string("bad string"), "")
        self.assertEqual(tools.text.to_string(1), "")

    def test_to_bytes(self):
        self.assertEqual(tools.text.to_bytes("good string"), b"good string")
        self.assertEqual(tools.text.to_bytes(b"bad string"), b"")
        self.assertEqual(tools.text.to_bytes(1), b"")

    def test_trim_bytes(self):
        def generate_test_data(input_string):
            byte_length = len(tools.text.to_bytes(input_string))
            return [
                tools.text.trim_bytes(input_string, length)
                for length in range(byte_length + 1)
            ]

        self.assertSequenceEqual(
            generate_test_data(DATA["long string"]),
            [
                tuple(element)
                for element in EXPECTED_RESULTS["trim bytes"]["long string"]
            ],
        )
        self.assertSequenceEqual(
            generate_test_data(DATA["long unicode string"]),
            [
                tuple(element)
                for element in EXPECTED_RESULTS["trim bytes"]["long unicode string"]
            ],
        )

    def test_colourise(self):
        results = [
            tools.text.colourise(DATA["long string"], colour)
            for colour in DATA["colours"]
        ]
        self.assertSequenceEqual(results, EXPECTED_RESULTS["colourise"])
        with self.assertRaises(KeyError):
            tools.text.colourise(DATA["long string"], "bad colour")
