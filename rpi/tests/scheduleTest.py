import configparser
from datetime import datetime
from unittest.mock import patch
from const import CONST
import unittest
import time
import logging
import RPiMockGPIO
import ledPWM
import main
import os
import threading
import photoresistor
import ultrasonic


class ScheduleTest(unittest.TestCase):
    logging.basicConfig(level=logging.INFO)
    os.chdir('..')

    @patch('lamp.datetime')
    def test_schedule(self, mock_date):
        C = CONST()
        config = configparser.ConfigParser()
        config.read(C.PATH_LIGHTS + "0" + C.EXTENSION)
        pl_time_h_on = int(config[C.LAMP_POLICY_ON][C.TIME_H])
        pl_time_m_on = int(config[C.LAMP_POLICY_ON][C.TIME_M])

        # We set the current time before the policy schedule
        mock_date.today.return_value = datetime(2017, 2, 1, pl_time_h_on, pl_time_m_on - 1, 50)
        RPiMockGPIO.wait_seconds = 1  # Wait of 1 second means that there aren't cars
        photoresistor.WAIT_TIME = 2
        ultrasonic.TIMEOUT = 1  # Reduce the timeout after a car passes
        t = threading.Thread(target=main.main)
        t.daemon = True
        t.start()
        time.sleep(3)
        lamp_pin = int(config['GENERAL']['lamp_pin'])
        assert ledPWM.get_led_intensity(lamp_pin) == 0

        # We wait a few seconds and we should be in the policy schedule
        time.sleep(12)
        assert ledPWM.get_led_intensity(lamp_pin) == int(config[C.LAMP_POLICY_ON][C.INTENSITY])
        pl_time_h_off = int(config[C.LAMP_POLICY_OFF][C.TIME_H])
        pl_time_m_off = int(config[C.LAMP_POLICY_OFF][C.TIME_M])

        # We set the current time after the policy schedule
        mock_date.today.return_value = datetime(2017, 2, 2, pl_time_h_off, pl_time_m_off + 1)
        time.sleep(5)

        # The lamp needs to be off
        assert ledPWM.get_led_intensity(lamp_pin) == 0
