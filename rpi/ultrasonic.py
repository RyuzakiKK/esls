from random import randint
from threading import Thread
import time
import pykka


class Ultrasonic(pykka.ThreadingActor):
    def __init__(self):
        super(Ultrasonic, self).__init__()
        self._pin = 1
        self._listActors = []
        self.timeout = 10  # seconds of timeout after a car passes
        t = Thread(target=self.start_measuring)
        t.daemon = True
        t.start()

    def add_actor(self, actor_ref):
        self._listActors.append(actor_ref)
        print("I added an actor")

    def remove_actor(self, actor_ref):
        self._listActors.remove(actor_ref)

    def start_measuring(self):
        while True:
            print("too early, let me sleep a little more")
            while len(self._listActors) is not 0:
                current_distance = randint(0, 100)  # TODO get the intensity
                if current_distance < 20:  # A car is on this street
                    print("I saw a car!")
                    for actor in self._listActors:
                        actor.ultrasonic_notify(self.timeout)
                time.sleep(10)
            time.sleep(10)
