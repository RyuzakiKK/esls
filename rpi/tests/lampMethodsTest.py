from datetime import datetime
from unittest.mock import patch
import unittest

import lamp


class LampMethodsTest(unittest.TestCase):
    @patch('lamp.datetime')
    def test_get_delta(self, mock_date):
        # start = 20:00 | end = 5:00
        mock_date.today.return_value = datetime(2017, 2, 1, 22, 0)
        assert lamp.Lamp.get_delta(20, 0, 0, 5, 0, 0) == 9 * 60 * 60

        # start = 20:00 | end = 23:00
        mock_date.today.return_value = datetime(2017, 2, 1, 19, 0)
        assert lamp.Lamp.get_delta(20, 0, 0, 23, 0, 0) == 3 * 60 * 60

    @patch('lamp.datetime')
    def test_get_wait(self, mock_date):
        # start = 20:00 | today = 22:00 | end = 5:00
        mock_date.today.return_value = datetime(2017, 2, 1, 22, 0)
        assert lamp.Lamp.get_wait(20, 0, 0, 5, 0, 0) == -2 * 60 * 60

        # start = 20:00 | end = 22:00 | today = 23:00
        mock_date.today.return_value = datetime(2017, 2, 1, 23, 0)
        assert lamp.Lamp.get_wait(20, 0, 0, 22, 0, 0) == 21 * 60 * 60

        # start = 20:00 | end = 5:00 | today = 6:00
        mock_date.today.return_value = datetime(2017, 2, 1, 6, 0)
        assert lamp.Lamp.get_wait(20, 0, 0, 5, 0, 0) == 14 * 60 * 60

        # today = 23:00 | start = 1:00 | end = 5:00
        mock_date.today.return_value = datetime(2017, 2, 1, 23, 0)
        assert lamp.Lamp.get_wait(1, 0, 0, 5, 0, 0) == 2 * 60 * 60

        # today = 19:00 | start = 20:00 | end = 5:00
        mock_date.today.return_value = datetime(2017, 2, 1, 19, 0)
        assert lamp.Lamp.get_wait(20, 0, 0, 5, 0, 0) == 1 * 60 * 60

        # start = 20:00 | today = 3:00 | end = 5:00
        mock_date.today.return_value = datetime(2017, 2, 1, 3, 0)
        assert lamp.Lamp.get_wait(20, 0, 0, 5, 0, 0) == -7 * 60 * 60
