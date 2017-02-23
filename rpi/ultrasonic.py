import threading
import time
import pykka
import logging
# import RPi.GPIO as GPIO
import RPiMockGPIO as GPIO

# GPIO.cleanup() ?

WAIT_TIME = 1
TIMEOUT = 10  # seconds of timeout after a car passes
logger = logging.getLogger(__name__)


class Ultrasonic(pykka.ThreadingActor):
    """
    Use an ultrasonic sensor
    Attributes:
        GPIO_TRIGGER: pin number of trigger
        GPIO_ECHO: pin number of echo
    """
    def __init__(self, gpio_trigger, gpio_echo, right_lane, wait_time):
        super(Ultrasonic, self).__init__()
        self.GPIO_TRIGGER = gpio_trigger
        self.GPIO_ECHO = gpio_echo
        self.right_lane = right_lane
        self.wait_time = wait_time
        self.e = threading.Event()
        self.blocked = True
        self.lock = threading.Lock()
        self.cv = threading.Condition()
        self._listActors = []
        t = threading.Thread(target=self.start_measuring)
        t.daemon = True
        t.start()

    def add_actor(self, actor_ref):
        with self.cv:
            self._listActors.append(actor_ref)
        logger.info("[{0}{1}]I added an actor {2}".format("ultra", self.right_lane, actor_ref))

    def remove_actor(self, actor_ref):
        with self.cv:
            self._listActors.remove(actor_ref)

    def start_measuring(self):
        """ Start the measuring with an infinite loop """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)
        # Set trigger to False (Low)
        GPIO.output(self.GPIO_TRIGGER, False)
        t = threading.Thread(target=self.send_input)
        t.daemon = True
        t.start()
        while True:
            with self.cv:
                if len(self._listActors) is not 0:
                    distance = self._measure_average()
                    logger.debug("distance: {0}".format(distance))
                    if distance < 20:
                        logger.info("I saw a car!")
                        for actor in self._listActors:
                            actor.ultrasonic_notify(TIMEOUT, self.wait_time, self.right_lane)
            time.sleep(WAIT_TIME)

    def send_input(self):
        while True:
            self.e.wait()
            self.e.clear()
            logger.debug("running")
            while True:
                with self.lock:
                    if not self.blocked:
                        logger.debug("break!")
                        break  # exit the last while True and wait for the event
                GPIO.output(self.GPIO_TRIGGER, True)
                time.sleep(0.00001)
                GPIO.output(self.GPIO_TRIGGER, False)

    def measure(self):
        with self.lock:
            self.blocked = True
        self.e.set()
        GPIO.wait_for_edge(self.GPIO_ECHO, GPIO.RISING)
        start = time.time()
        GPIO.wait_for_edge(self.GPIO_ECHO, GPIO.FALLING)
        stop = time.time()
        with self.lock:
            self.blocked = False
        elapsed = stop - start
        # Time multiplied by the speed of sound (cm/s), go and return so half the value
        return (elapsed * 34300) / 2

    # Takes 2 measurements and returns the average.
    def _measure_average(self):
        distance1 = self.measure()
        time.sleep(0.05)
        distance2 = self.measure()
        return (distance1 + distance2) / 2
