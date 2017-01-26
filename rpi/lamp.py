from datetime import datetime, timedelta
import json
import threading
import pykka

'''
on: time_h=19 photoresistor=50
time_h=18 photoresistor=20 -> nothing
time_h=20 photoresistor=60 -> nothing
time_h=21 photoresistor=40 -> switch on
time_h=3 photoresistor=60 -> ???

off: time_h=6 photoresistor=70
time_h=4 photoresistor=60 -> nothing
time_h=5 photoresistor=75 -> switch off
or
time_h=6 photoresistor=60 -> switch off
'''
# no need for a lock because everything here is single thread
# TODO tell the nearby
# TODO if there is a car, what to do with pr value?


class Lamp(pykka.ThreadingActor):
    def __init__(self, lamp_id, pr_proxy, us_proxy, lamp_policy_on=None, lamp_policy_off=None, lamp_energy=None):
        super(Lamp, self).__init__()
        self.lamp_id = lamp_id
        self.lamp_policy_on = lamp_policy_on
        self.lamp_policy_off = lamp_policy_off
        self.lamp_energy = lamp_energy
        self.timer_on = threading.Timer(0, None)
        self.timer_energy_on = threading.Timer(0, None)
        self.timer_energy_timeout = threading.Timer(0, None)
        self.my_proxy = None
        self.start_time_on = None
        self.start_time_energy_on = None
        self.timeout_on_off = 0
        self.timeout_energy = 0
        self.on = False
        pass  # set off
        self.pr_proxy = pr_proxy
        self.us_proxy = us_proxy

    def set_self_proxy(self, lamp_proxy):
        self.my_proxy = lamp_proxy

    def update_schedules(self):
        self.timeout_on_off = self.get_delta(self.lamp_policy_on.time_h, self.lamp_policy_on.time_m, 0,
                                             self.lamp_policy_off.time_h, self.lamp_policy_off.time_m, 0)
        self.timeout_energy = self.get_delta(self.lamp_energy.time_h_on, self.lamp_energy.time_m_on, 0,
                                             self.lamp_energy.time_h_off, self.lamp_energy.time_m_off, 0)

    def start_schedule_on(self):
        today = datetime.today()
        wait_t = self.get_delta(today.hour, today.minute, today.second, self.lamp_policy_on.time_h,
                                self.lamp_policy_on.time_m, 0)
        self.timer_on.cancel()
        self.timer_on = threading.Timer(wait_t, self.pr_proxy.add_actor, [self.my_proxy])
        self.timer_on.start()
        self.start_time_on = datetime.today() + timedelta(seconds=wait_t)

    def start_schedule_energy_on(self):
        today = datetime.today()
        wait_t = self.get_delta(today.hour, today.minute, today.second, self.lamp_energy.time_h_on,
                                self.lamp_energy.time_m_on, 0)
        self.timer_energy_on.cancel()
        self.timer_energy_on = threading.Timer(wait_t, self.us_proxy.add_actor, [self.my_proxy])
        self.timer_energy_on.start()
        self.start_time_energy_on = datetime.today() + timedelta(seconds=wait_t)

    def update_light(self, current_intensity):
        print(threading.get_ident())
        if self.is_in_schedule():
            if self.on and current_intensity > self.lamp_policy_off.photoresistor:
                pass  # set off
                print("lamp off")
                self.on = False
            elif not self.on and current_intensity < self.lamp_policy_on.photoresistor:
                pass  # set on
                print("lamp on")
                self.on = True
        else:
            print("schedule is over, see you tomorrow")
            self.pr_proxy.remove_actor(self.my_proxy)
            self.start_schedule_on()

    def ultrasonic_notify(self, us_timeout):
        print(threading.get_ident())
        if self.is_in_schedule() and self.is_energy_saving_time():
            self.timer_energy_timeout.cancel()
            pass  # set on lamp_policy_on.intensity
            print("There is a car! Lamp full power")
            # TODO dim the light to the lamp_energy.intensity value
            self.timer_energy_timeout.cancel()
            self.timer_energy_timeout = threading.Timer(us_timeout, print, ["Everything is quiet, dim the light!"])
            self.timer_energy_timeout.start()
        else:
            self.timer_energy_timeout.cancel()
            print("schedule is over, see you tomorrow")
            self.us_proxy.remove_actor(self.my_proxy)
            self.start_schedule_energy_on()

    def to_json(self):
        return json.dumps([self.lamp_id, self.lamp_policy_on, self.lamp_policy_off, self.lamp_energy],
                          default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    @staticmethod
    def get_delta(start_h, start_m, start_s, end_h, end_m, end_s):
        today = datetime.today()
        start = today.replace(hour=start_h, minute=start_m, second=start_s)
        end = today.replace(hour=end_h, minute=end_m, second=end_s)
        if (end - start).seconds < 1:
            print("and even today we do it tomorrow")
            end = end.replace(day=end.day + 1)
        print("seconds to wait " + str((end - start).seconds))
        return (end - start).seconds

    def is_in_schedule(self):  # TODO check if elapsed is negative?
        now = datetime.today()
        elapsed = (now - self.start_time_on).seconds
        return elapsed < self.timeout_on_off

    def is_energy_saving_time(self):
        now = datetime.today()
        elapsed = (now - self.start_time_energy_on).seconds
        print("Are we in energy saving? " + str(elapsed < self.timeout_energy))
        return elapsed < self.timeout_energy
