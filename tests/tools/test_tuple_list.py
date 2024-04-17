"""Tools for testing a TupleList.

Classes:
        TestTupleList: Test that the TupleList holds and returns the expected
            data.
"""

import unittest

from tools.tuple_list import TupleList

DATA = [
    ("Username 1", "Song Request 1"),
    ("Username 2", "Song Request 2"),
    ("Username 3", "Song Request 3"),
    ("Username 4", "Song Request 4"),
]


# ruff: noqa: D102
class TestTupleList(unittest.TestCase):
    """Test that the TupleList holds and returns the expected data."""

    def load_data(self):
        self.t_l = TupleList(*DATA)
        split = len(DATA) // 2
        self.split_data = (DATA[:split], DATA[split:])
        self.front = TupleList(*self.split_data[0])
        self.back = TupleList(*self.split_data[1])

    def setUp(self):
        self.load_data()

    def test_str(self):
        formatted_data = "\n".join(f'{user}: "{song}"' for user, song in DATA)
        expected = f"TupleList contents:\n{formatted_data}"
        result = str(self.t_l)
        self.assertEqual(result, expected)

    def test_get(self):
        for key, value in DATA:
            self.assertEqual(self.t_l[key], value)

    def test_contains(self):
        for key, _value in DATA:
            self.assertIn(key, self.t_l)

    def test_delitem(self):
        for key, _value in DATA:
            self.assertIn(key, self.t_l)
            del self.t_l[key]
            self.assertNotIn(key, self.t_l)
            self.assertIsNone(self.t_l[key])

    def test_iter(self):
        for (key, value), (expected_key, expected_value) in zip(self.t_l, DATA):
            self.assertEqual(key, expected_key)
            self.assertEqual(value, expected_value)

    def test_repr(self):
        new_t_l = eval(repr(self.t_l))
        self.assertIs(TupleList, type(new_t_l))
        for key, value in DATA:
            self.assertEqual(value, new_t_l[key])

    def test_bool(self):
        self.assertTrue(self.t_l)
        for key_name in [key for key, value in self.t_l]:
            del self.t_l[key_name]
        self.assertFalse(self.t_l)

    def test_len(self):
        self.assertEqual(len(self.t_l), len(DATA))

    def test_setitem(self):
        for key, value in DATA:
            new_value = "new " + value
            self.assertNotEqual(self.t_l[key], new_value)
            self.t_l[key] = new_value
            self.assertEqual(self.t_l[key], new_value)
            new_key = "new " + key
            self.assertIsNone(self.t_l[new_key])
            self.t_l[new_key] = new_value
            self.assertEqual(self.t_l[new_key], new_value)

    def test_equals(self):
        new_t_l = TupleList()
        self.assertNotEqual(self.t_l, new_t_l)
        new_t_l = TupleList(*DATA)
        self.assertEqual(self.t_l, new_t_l)

    def test_copy(self):
        new_t_l = self.t_l.copy()
        self.assertIsNot(new_t_l, self.t_l)
        self.assertEqual(new_t_l, self.t_l)

    def test_add(self):
        self.assertEqual(self.front + self.back, self.t_l)
        new_t_l = self.front.copy()
        new_t_l += self.back
        self.assertEqual(new_t_l, self.t_l)

    def test_sub(self):
        self.assertEqual(self.t_l - self.back, self.front)
        new_t_l = self.t_l.copy()
        new_t_l -= self.back
        self.assertEqual(new_t_l, self.front)
        new_t_l -= self.front
        self.assertEqual(new_t_l, TupleList())

    def test_deprioritise(self):
        new_t_l = self.t_l.deprioritise()
        self.assertEqual(new_t_l, self.t_l)
        new_t_l = new_t_l.deprioritise(self.front)
        self.assertEqual(new_t_l, TupleList(*self.split_data[1], *self.split_data[0]))

    def test_pop(self):
        for expected_key, expected_value in DATA:
            key, value = self.t_l.pop(0)
            self.assertEqual(key, expected_key)
            self.assertEqual(value, expected_value)

        self.load_data()
        for expected_key, expected_value in DATA[::-1]:
            key, value = self.t_l.pop(-1)
            self.assertEqual(key, expected_key)
            self.assertEqual(value, expected_value)

    def test_random(self):
        unpicked_keys = [key for key, _value in self.split_data[0]]
        picked_keys = [key for key, _value in self.split_data[1]]
        all_keys = [key for key, _value in DATA]

        front_length = len(DATA) // 2
        back_length = len(DATA) - front_length

        for _ in range(front_length):
            (key, value), picked = self.t_l.random(self.back)
            self.assertFalse(picked)
            self.assertIn(key, unpicked_keys)

        for _ in range(back_length):
            (key, value), picked = self.t_l.random(self.back)
            self.assertTrue(picked)
            self.assertIn(key, picked_keys)

        self.load_data()
        for _ in range(front_length + back_length):
            (key, value), picked = self.t_l.random()
            self.assertFalse(picked)
            self.assertIn(key, all_keys)

        self.load_data()
        for expected_key, expected_value in DATA:
            (key, value), picked = self.t_l.random(first=True)
            self.assertFalse(picked)
            self.assertEqual(key, expected_key)
            self.assertEqual(value, expected_value)

    def test_serialise(self):
        data = self.t_l.serialise()
        for result, expected in zip(data, DATA):
            self.assertSequenceEqual(result, expected)
