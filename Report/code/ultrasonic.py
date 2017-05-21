def start_measuring(self):
    t = threading.Thread(target=self.send_input)
    t.daemon = True
    t.start()
    while True:
        self.actors_ev.wait()
        distance = self._measure_average()
        if distance < threshold:
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

def _measure_average(self):
    distance1 = self.measure()
    time.sleep(0.05)
    distance2 = self.measure()
    return (distance1 + distance2) / 2
