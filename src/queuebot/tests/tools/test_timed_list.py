import unittest
from time import sleep

from queuebot.tools import timed_list

DELAY = 0.01
DEFAULT_DELAY = 0.02
DATA = [1, 2, 3]


# ruff: noqa: D101, D102
class TestTimedList(unittest.TestCase):
    def setUp(self):
        self.t_l = timed_list.TimedList(delay=DELAY)
        self.load_data()

    def load_data(self):
        self.t_l.data = DATA.copy()

    def test_arguments(self):
        timed_list.TimedList.default_delay = DEFAULT_DELAY
        self.t_l = timed_list.TimedList()
        self.load_data()
        self.test_assign(DEFAULT_DELAY)
        self.t_l = timed_list.TimedList(DELAY)
        self.load_data()
        self.test_assign()
        self.t_l = timed_list.TimedList(delay=DELAY)
        self.load_data()
        self.test_assign()
        self.t_l = timed_list.TimedList(**{"delay": DELAY})
        self.load_data()
        self.test_assign()
        self.t_l = timed_list.TimedList(**{"data": DATA, "delay": DELAY, "time": 1})
        self.assertListEqual(self.t_l.data, [])

    def test_assign(self, delay=DELAY):
        self.assertListEqual(self.t_l.get(), DATA)
        sleep(delay / 2)
        self.assertListEqual(self.t_l.get(), DATA)
        sleep(delay / 2)
        self.assertListEqual(self.t_l.get(), [])

    def test_get(self):
        self.assertEqual(self.t_l.data, self.t_l.get())

    def test_serialise(self):
        res = self.t_l.serialise()
        self.assertIn("time", res)
        del res["time"]
        self.assertEqual(res, {"data": [1, 2, 3], "delay": DELAY})

    def test_bool(self):
        self.assertTrue(self.t_l)
        sleep(DELAY)
        self.assertFalse(self.t_l)

    def test_len(self):
        self.assertEqual(len(DATA), len(self.t_l))
        sleep(DELAY)
        self.assertEqual(len(self.t_l), 0)

    def test_append(self):
        self.t_l.append(max(DATA) + 1)
        self.assertListEqual(self.t_l.data, [*DATA, max(DATA) + 1])
        sleep(DELAY)
        self.assertListEqual(self.t_l.data, [])

    def test_iter(self):
        self.assertCountEqual(self.t_l, DATA)

    def test_getitem(self):
        for index, _ in enumerate(DATA):
            self.assertEqual(DATA[index], self.t_l[index])

    def test_contains(self):
        for item in DATA:
            self.assertIn(item, self.t_l)
