from random import randint
from threading import Thread
import time
import pykka


class Photoresistor(pykka.ThreadingActor):
    def __init__(self):
        super(Photoresistor, self).__init__()
        self._pin = 1
        self._listActors = []
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
            print("busy waiting, that's so boring")
            while len(self._listActors) is not 0:
                current_intensity = randint(0, 100)  # TODO get the intensity
                print("measured " + str(current_intensity))
                for actor in self._listActors:
                    actor.update_light(current_intensity)
                time.sleep(10)
            time.sleep(10)
