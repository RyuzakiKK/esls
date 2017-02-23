import time
import logging

BCM = "BCM"
OUT = "out"
IN = "in"
RISING = "rising"
FALLING = "falling"
wait_seconds = 0.001
logger = logging.getLogger(__name__)


def setmode(mode):
    print(mode)


def setup(pin, mode):
    logger.debug("Pin {0} now {1}".format(pin, mode))


def output(pin, mode):
    logger.debug("Pin {0} now {1}".format(pin, mode))


def wait_for_edge(pin, edge):
    time.sleep(wait_seconds)


class PWM:
    def __init__(self, pin, frequency):
        pass

    def start(self, intensity):
        pass
