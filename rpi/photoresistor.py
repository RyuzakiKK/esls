import threading
import time
import pykka
import smbus


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
        print("I added an actor")

    def remove_actor(self, actor_ref):
        with self.cv:
            self._listActors.remove(actor_ref)

    def start_measuring(self):
        while True:
            print("busy waiting, that's so boring")
            while len(self._listActors) is not 0:
                current_lux = self.measure()
                print("measured {0}".format(current_lux))
                for actor in self._listActors:
                    actor.update_light(current_lux)
                time.sleep(10)
            time.sleep(10)

    def measure(self):
        atmosphere_low_byte = self.i2cBus.read_byte_data(self.address_TSL2561, 0x8c)
        atmosphere_high_byte = self.i2cBus.read_byte_data(self.address_TSL2561, 0x8d)
        atmosphere = (atmosphere_high_byte * 256) + atmosphere_low_byte
        print("Atmosphere {0}".format(atmosphere))
        ir_low_byte = self.i2cBus.read_byte_data(self.address_TSL2561, 0x8e)
        ir_high_byte = self.i2cBus.read_byte_data(self.address_TSL2561, 0x8f)
        ir = (ir_high_byte * 256) + ir_low_byte
        print("IR {0}".format(ir))
        ratio = ir / float(atmosphere) if atmosphere != 0 else 0
        print("Ratio {0}".format(ratio))
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
        print("Lux = {0}".format(lux))
        return lux
