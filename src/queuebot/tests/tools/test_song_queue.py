import json
import unittest
from unittest.mock import Mock, patch

from queuebot.state import song_queue

# ruff: noqa: D101, D102
with open("src/queuebot/tests/tools/song_queue_testdata.json", encoding="UTF-8") as fd_:
    testdata = json.load(fd_)
    DATA = testdata["inputs"]
    EXPECTED_RESULTS = testdata["expected results"]


class TestBaseMethods(unittest.TestCase):
    def setUp(self):
        self.mocked_parent = Mock()
        self.b_m = song_queue.BaseMethods(self.mocked_parent)

    def test_getitem(self):
        res = self.b_m["test_attribute"]
        print(res)
        print(dir(self.mocked_parent.mock_calls))

    def test_init(self):
        pass

    def test_clear(self):
        pass

    def test_close(self):
        pass

    def test_leave(self):
        pass

    def test_listusers(self):
        pass

    def test_removeuser(self):
        pass

    def test_testqueue(self):
        pass


class TestSongQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch("builtins.open")
        cls.mocked_open = cls.patcher.start()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()
        super().tearDownClass()

    def setup_mocked_open(self, result=""):
        self.mocked_open.reset_mock()
        self.mocked_open.return_value.__enter__.return_value.read.return_value = result
        self.mocked_open.return_value.__enter__.return_value.write = self.mocked_writer
        self.mocked_open_write_result = None

    def mocked_writer(self, input_string):
        self.mocked_open_write_result = input_string

    def setUp(self):
        self.setup_mocked_open("")
        with patch("builtins.print"):
            self.s_q = song_queue.SongQueue("example_channel")

    def test_init(self):
        self.setup_mocked_open()
        with patch("builtins.print") as mocked_print:
            self.s_q = song_queue.SongQueue("example_channel")
        mocked_print.assert_called()
        self.assertIn(
            "Failed to load saved queue, creating new one",
            mocked_print.mock_calls[0].args[0],
        )

    def test_save(self):
        self.s_q.save()
        res = json.loads(self.mocked_open_write_result)
        self.assertIn("time", res["currentusers"])
        del res["currentusers"]["time"]
        self.assertDictEqual(res, EXPECTED_RESULTS["test_save"])

    def test_load(self):
        for chunk in DATA["test_load"]:
            self.setup_mocked_open(json.dumps(chunk))
            with patch("builtins.print") as mocked_print:
                self.s_q = song_queue.SongQueue("example_channel")
            self.s_q.save()
            mocked_print.assert_not_called()
            self.assertDictEqual(json.loads(self.mocked_open_write_result), chunk)


class TestSongQueueFunctions(unittest.TestCase):
    def test_trunc(self):
        pass
