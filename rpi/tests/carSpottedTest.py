import configparser
from datetime import datetime
from unittest.mock import patch
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

INTENSITY = "intensity"
TIME_H = "time_h"
TIME_M = "time_m"
TIME_H_ON = "time_h_on"
TIME_M_ON = "time_m_on"
LAMP_POLICY_ON = "LampPolicyOn"
LAMP_POLICY_OFF = "LampPolicyOff"
LAMP_ENERGY_SAVING = "LampEnergySaving"
PATH_LIGHTS = "lights/light"
EXTENSION = ".cfg"


class CarSpottedTest(unittest.TestCase):
    logging.basicConfig(level=logging.INFO)
    os.chdir('..')

    @patch('lamp.datetime')
    def test_car_spotted(self, mock_date):
        config = configparser.ConfigParser()
        config.read(PATH_LIGHTS + "0" + EXTENSION)
        en_time_h = int(config[LAMP_ENERGY_SAVING][TIME_H_ON])
        en_time_m = int(config[LAMP_ENERGY_SAVING][TIME_M_ON])
        # We set the current time in the energy saving schedule
        mock_date.today.return_value = datetime(2017, 2, 1, en_time_h, en_time_m + 1)
        RPiMockGPIO.wait_seconds = 0  # Wait of 0 means that there is a car
        photoresistor.WAIT_TIME = 2
        ultrasonic.TIMEOUT = 1  # Reduce the timeout after a car passes
        t = threading.Thread(target=main.main)
        t.daemon = True
        t.start()
        time.sleep(3)
        lamp_pin = int(config['GENERAL']['lamp_pin'])
        # Because we spotted some cars, the lamp needs to be at policy on intensity
        assert ledPWM.get_led_intensity(lamp_pin) == int(config[LAMP_POLICY_ON][INTENSITY])
        RPiMockGPIO.wait_seconds = 1  # Wait of 1 second means that there aren't cars
        time.sleep(6)
        # No cars = lamp at energy saving intensity
        assert ledPWM.get_led_intensity(lamp_pin) == int(config[LAMP_ENERGY_SAVING][INTENSITY])
        pl_time_h_off = int(config[LAMP_POLICY_OFF][TIME_H])
        pl_time_m_off = int(config[LAMP_POLICY_OFF][TIME_M])
        # We set the current time after the policy schedule
        mock_date.today.return_value = datetime(2017, 2, 2, pl_time_h_off, pl_time_m_off + 1)
        time.sleep(5)
        # The lamp needs to be off
        assert ledPWM.get_led_intensity(lamp_pin) == 0
