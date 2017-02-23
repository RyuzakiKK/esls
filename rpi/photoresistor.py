import threading
import time
import pykka
import logging
# import smbus
import smbusMock as smbus

WAIT_TIME = 10
logger = logging.getLogger(__name__)


class Photoresistor(pykka.ThreadingActor):
    def __init__(self):
        super(Photoresistor, self).__init__()
        bus_number = 1
        self.address_TSL2561 = 0x39
        self.start = 0x51
        self.i2cBus = smbus.SMBus(bus_number)
        self.i2cBus.write_byte_data(self.address_TSL2561, 0x80, 0x03)
        self.cv = threading.Condition()
        self._listActors = []
        t = threading.Thread(target=self.start_measuring)
        t.daemon = True
        t.start()

    def add_actor(self, actor_ref):
        with self.cv:
            self._listActors.append(actor_ref)
        logger.info("[{0}]I added an actor {1}".format("photo", actor_ref))

    def remove_actor(self, actor_ref):
        with self.cv:
            self._listActors.remove(actor_ref)

    def start_measuring(self):
        while True:
            logger.info("busy waiting, that's so boring")
            while len(self._listActors) is not 0:
                current_lux = self.measure()
                logger.info("measured {0}".format(current_lux))
                for actor in self._listActors:
                    actor.update_light(current_lux)
                time.sleep(WAIT_TIME)
            time.sleep(WAIT_TIME)

    def measure(self):
        atmosphere_low_byte = self.i2cBus.read_byte_data(self.address_TSL2561, 0x8c)
        atmosphere_high_byte = self.i2cBus.read_byte_data(self.address_TSL2561, 0x8d)
        atmosphere = (atmosphere_high_byte * 256) + atmosphere_low_byte
        logger.debug("Atmosphere {0}".format(atmosphere))
        ir_low_byte = self.i2cBus.read_byte_data(self.address_TSL2561, 0x8e)
        ir_high_byte = self.i2cBus.read_byte_data(self.address_TSL2561, 0x8f)
        ir = (ir_high_byte * 256) + ir_low_byte
        logger.debug("IR {0}".format(ir))
        ratio = ir / float(atmosphere) if atmosphere != 0 else 0
        logger.debug("Ratio {0}".format(ratio))
        if 0 < ratio <= 0.50:
            lux = 0.0304 * atmosphere - 0.062 * atmosphere * (ratio ** 1.4)
        elif 0.50 < ratio <= 0.61:
            lux = 0.0224 * atmosphere - 0.031 * ir
        elif 0.61 < ratio <= 0.80:
            lux = 0.0128 * atmosphere - 0.0153 * ir
        elif 0.80 < ratio <= 1.3:
            lux = 0.00146 * atmosphere - 0.00112 * ir
        else:
            lux = 0
        logger.debug("Lux = {0}".format(lux))
        return lux
