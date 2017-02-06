from datetime import datetime
from unittest.mock import patch
import unittest

import main


class MainTest(unittest.TestCase):
    @patch('main.datetime')
    def test_sanity_check(self, mock_date):

        mock_date.today.return_value = datetime(year=2017, month=2, day=6, hour=14, minute=0)
        assert main.sanity_check(0, pl_intensity_on=100, pl_time_h_on=11, pl_time_m_on=30, photoresistor_on=40,
                                 pl_time_h_off=5, pl_time_m_off=30, photoresistor_off=70, en_intensity=60,
                                 en_time_h_on=1, en_time_m_on=0, en_time_h_off=5, en_time_m_off=30)

        mock_date.today.return_value = datetime(year=2017, month=2, day=6, hour=2, minute=0)
        assert main.sanity_check(0, pl_intensity_on=100, pl_time_h_on=11, pl_time_m_on=30, photoresistor_on=40,
                                 pl_time_h_off=5, pl_time_m_off=30, photoresistor_off=70, en_intensity=60,
                                 en_time_h_on=1, en_time_m_on=0, en_time_h_off=5, en_time_m_off=30)

        mock_date.today.return_value = datetime(year=2017, month=2, day=6, hour=10, minute=0)
        assert main.sanity_check(0, pl_intensity_on=100, pl_time_h_on=11, pl_time_m_on=30, photoresistor_on=40,
                                 pl_time_h_off=5, pl_time_m_off=30, photoresistor_off=70, en_intensity=60,
                                 en_time_h_on=1, en_time_m_on=0, en_time_h_off=5, en_time_m_off=30)

        mock_date.today.return_value = datetime(year=2017, month=2, day=6, hour=19, minute=0)
        assert main.sanity_check(0, pl_intensity_on=100, pl_time_h_on=18, pl_time_m_on=30, photoresistor_on=40,
                                 pl_time_h_off=23, pl_time_m_off=30, photoresistor_off=70, en_intensity=60,
                                 en_time_h_on=20, en_time_m_on=0, en_time_h_off=23, en_time_m_off=30)

        # photoresistor_on > photoresistor_off
        mock_date.today.return_value = datetime(year=2017, month=2, day=6, hour=19, minute=0)
        assert not main.sanity_check(0, pl_intensity_on=100, pl_time_h_on=18, pl_time_m_on=30, photoresistor_on=60,
                                     pl_time_h_off=23, pl_time_m_off=30, photoresistor_off=50, en_intensity=60,
                                     en_time_h_on=20, en_time_m_on=0, en_time_h_off=23, en_time_m_off=30)

        # energy saving schedule out of policy schedule
        mock_date.today.return_value = datetime(year=2017, month=2, day=6, hour=19, minute=0)
        assert not main.sanity_check(0, pl_intensity_on=100, pl_time_h_on=18, pl_time_m_on=30, photoresistor_on=40,
                                     pl_time_h_off=23, pl_time_m_off=30, photoresistor_off=70, en_intensity=60,
                                     en_time_h_on=20, en_time_m_on=0, en_time_h_off=2, en_time_m_off=30)

        # energy saving schedule out of policy schedule
        mock_date.today.return_value = datetime(year=2017, month=2, day=6, hour=19, minute=0)
        assert not main.sanity_check(0, pl_intensity_on=100, pl_time_h_on=18, pl_time_m_on=30, photoresistor_on=40,
                                     pl_time_h_off=23, pl_time_m_off=30, photoresistor_off=70, en_intensity=60,
                                     en_time_h_on=17, en_time_m_on=0, en_time_h_off=22, en_time_m_off=30)