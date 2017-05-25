import threading
import time
import pykka
import logging
# import RPi.GPIO as GPIO
import RPiMockGPIO as GPIO


WAIT_TIME = 0.2
TIMEOUT = 10  # seconds of timeout after a car passes
logger = logging.getLogger(__name__)


class Ultrasonic(pykka.ThreadingActor):
    """
    Use an ultrasonic sensor
    Attributes:
        gpio_trigger: pin number of trigger
        gpio_echo: pin number of echo
    """
    def __init__(self, gpio_trigger, gpio_echo, right_lane, wait_time):
        super(Ultrasonic, self).__init__()
        self.gpio_trigger = gpio_trigger
        self.gpio_echo = gpio_echo
        self.right_lane = right_lane
        self.wait_time = wait_time
        self.measure_ev = threading.Event()
        self.cv = threading.Condition()
        self._listActors = []
        self.actors_ev = threading.Event()
        t = threading.Thread(target=self.start_measuring)
        t.daemon = True
        t.start()

    def add_actor(self, actor_ref):
        with self.cv:
            self._listActors.append(actor_ref)
            if len(self._listActors) == 1:
                self.actors_ev.set()
        logger.info("[{0}]I added an actor {1}".format(self.right_lane, actor_ref))

    def remove_actor(self, actor_ref):
        with self.cv:
            self._listActors.remove(actor_ref)
            if len(self._listActors) == 0:
                self.actors_ev.clear()

    def start_measuring(self):
        """ Start the measuring with an infinite loop """
        GPIO.setup(self.gpio_trigger, GPIO.OUT)
        GPIO.setup(self.gpio_echo, GPIO.IN)
        GPIO.output(self.gpio_trigger, False)
        t = threading.Thread(target=self.send_input)
        t.daemon = True
        t.start()
        while True:
            self.actors_ev.wait()
            distance = self._measure_average()
            logger.debug("distance: {0}".format(distance))
            if distance < 20:
                logger.info("I saw a car!")
                with self.cv:
                    for actor in self._listActors:
                        actor.ultrasonic_notify(TIMEOUT, self.wait_time, self.right_lane)
                time.sleep(TIMEOUT/2)
            time.sleep(WAIT_TIME)

    def send_input(self):
        while True:
            self.measure_ev.wait()
            GPIO.output(self.gpio_trigger, True)
            time.sleep(0.00001)
            GPIO.output(self.gpio_trigger, False)

    def measure(self):
        self.measure_ev.set()
        GPIO.wait_for_edge(self.gpio_echo, GPIO.RISING)
        start = time.time()
        GPIO.wait_for_edge(self.gpio_echo, GPIO.FALLING)
        stop = time.time()
        self.measure_ev.clear()
        elapsed = stop - start

        # Time multiplied by the speed of sound (cm/s), go and return so half the value
        return (elapsed * 34300) / 2

    # Takes 2 measurements and returns the average.
    def _measure_average(self):
        distance1 = self.measure()
        time.sleep(0.02)
        distance2 = self.measure()
        return (distance1 + distance2) / 2
