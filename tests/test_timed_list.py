"""Tools for testing a TimedList.

Classes:
    TestTimedList: Test how the list behaves over time.
"""
# pylint: disable=missing-function-docstring
import unittest
from time import sleep

from tools import timed_list

DELAY = 0.25
DEFAULT_DELAY = 0.5
DATA = [1, 2, 3]


class TestTimedList(unittest.TestCase):
    """Test how the list behaves over time.

    Ensure that the list wipes its data after the correct
    time delay has elapsed.
    """

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
        assert self.t_l.data == []

    def test_assign(self, delay=DELAY):
        assert self.t_l.get() == DATA
        sleep(delay / 2)
        assert self.t_l.get() == DATA
        sleep(delay / 2)
        assert self.t_l.get() == []

    def test_get(self):
        assert self.t_l.data == self.t_l.get()

    def test_serialise(self):
        res = self.t_l.serialise()
        assert "time" in res
        del res["time"]
        assert res == {"data": [1, 2, 3], "delay": DELAY}

    def test_bool(self):
        assert bool(self.t_l) is True
        sleep(DELAY)
        assert bool(self.t_l) is False

    def test_len(self):
        assert len(DATA) == len(self.t_l)
        sleep(DELAY)
        assert len(self.t_l) == 0

    def test_append(self):
        self.t_l.append(max(DATA) + 1)
        assert self.t_l.data == DATA + [max(DATA) + 1]
        sleep(DELAY)
        assert self.t_l.data == []

    def test_iter(self):
        for (value, expected) in zip(DATA, self.t_l):
            assert value == expected

    def test_getitem(self):
        for (index, _) in enumerate(DATA):
            assert DATA[index] == self.t_l[index]  # pylint: disable=unnecessary-list-index-lookup

    def test_contains(self):
        for item in DATA:
            assert item in self.t_l
