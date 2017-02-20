from datetime import datetime, timedelta
import json
import threading

import pykka
import ledPWM
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from enum import Enum

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


action = Enum('action', 'turn_on turn_off energy_saving car_detected')
error = Enum('error', 'generic')


class Lamp(pykka.ThreadingActor):
    def __init__(self, lamp_id, lamp_number, pin, area, pr_proxy, us_proxy_1, us_proxy_2, lamp_policy_on=None,
                 lamp_policy_off=None, lamp_energy=None):
        super(Lamp, self).__init__()
        self.lamp_id = lamp_id
        self.lamp_number = lamp_number
        self.pin = pin
        self.area = area
        self.lamp_policy_on = lamp_policy_on
        self.lamp_policy_off = lamp_policy_off
        self.lamp_energy = lamp_energy
        self.timer_on = threading.Timer(0, None)
        self.timer_energy_on_1 = threading.Timer(0, None)
        self.timer_energy_on_2 = threading.Timer(0, None)
        self.start_energy = threading.Timer(0, None)
        self.timer_energy_timeout = threading.Timer(0, None)
        self.my_proxy = None
        self.start_time_on = None
        self.start_time_energy_on = None
        self.timeout_on_off = 0
        self.timeout_energy = 0
        self.on = False
        self.debug = False
        ledPWM.set_led_intensity(self.pin, 0)
        self.pr_proxy = pr_proxy
        self.us_proxy_1 = us_proxy_1
        self.us_proxy_2 = us_proxy_2

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
        print(wait_t)
        self.timer_on.cancel()
        self.timer_on = threading.Timer(wait_t, self.pr_proxy.add_actor, [self.my_proxy])
        self.timer_on.start()
        self.start_time_on = datetime.today() + timedelta(seconds=wait_t)

    def start_schedule_energy_on(self):
        today = datetime.today()
        wait_t = self.get_delta(today.hour, today.minute, today.second, self.lamp_energy.time_h_on,
                                self.lamp_energy.time_m_on, 0)
        self.timer_energy_on_1.cancel()
        self.timer_energy_on_1 = threading.Timer(wait_t, self.us_proxy_1.add_actor, [self.my_proxy])
        self.timer_energy_on_1.start()
        self.timer_energy_on_2.cancel()
        self.timer_energy_on_2 = threading.Timer(wait_t, self.us_proxy_2.add_actor, [self.my_proxy])
        self.timer_energy_on_2.start()
        self.start_energy.cancel()
        self.start_energy = threading.Timer(wait_t, self.set_to_energy)
        self.start_energy.start()
        self.start_time_energy_on = datetime.today() + timedelta(seconds=wait_t)

    def update_light(self, current_photoresistor):
        if not self.debug:
            if self.is_in_schedule():
                if self.on and current_photoresistor > self.lamp_policy_off.photoresistor:
                    self.timer_energy_timeout.cancel()
                    ledPWM.set_led_intensity(self.pin, 0)
                    print("lamp off")
                    self.on = False
                    self.send_post(action.turn_off.value, 0, current_photoresistor)
                elif not self.on and current_photoresistor < self.lamp_policy_on.photoresistor:
                    if self.is_energy_saving_time():
                        ledPWM.set_led_intensity(self.pin, self.lamp_energy.intensity)
                        print("lamp on")
                        self.on = True
                        self.send_post(action.energy_saving.value, self.lamp_energy.intensity, current_photoresistor)
                    else:
                        ledPWM.set_led_intensity(self.pin, self.lamp_policy_on.intensity)
                        print("lamp on")
                        self.on = True
                        self.send_post(action.turn_on.value, self.lamp_policy_on.intensity, current_photoresistor)
            else:
                print("schedule is over, see you tomorrow")
                self.pr_proxy.remove_actor(self.my_proxy)
                self.send_post(action.turn_off.value, 0, current_photoresistor)
                self.start_schedule_on()

    def ultrasonic_notify(self, us_timeout, wait_time, right_lane, notified=False):
        if not self.debug:
            if self.is_in_schedule() and self.is_energy_saving_time():
                if self.on:
                    # If the lamp is off because of the photoresistor, even if there is a car the lamp stay off
                    self.timer_energy_timeout.cancel()
                    if right_lane:
                        position = self.lamp_id
                    else:
                        position = self.lamp_number - self.lamp_id
                    # If this is the last lamp and we were not notified, we notify the nearest rpi
                    if position == self.lamp_number and not notified:
                        from main import notify_nearby
                        threading.Timer(wait_time * position, notify_nearby, right_lane)
                    threading.Timer(wait_time * position, self.car_detected)
                    print("There is a car! Lamp full power")
                    self.timer_energy_timeout.cancel()
                    self.timer_energy_timeout = threading.Timer(us_timeout + wait_time * position, self.set_to_energy)
                    self.timer_energy_timeout.start()
            else:
                self.timer_energy_timeout.cancel()
                print("schedule is over, see you tomorrow")
                self.us_proxy_1.remove_actor(self.my_proxy)
                self.us_proxy_2.remove_actor(self.my_proxy)
                self.start_schedule_energy_on()

    def send_post(self, this_action, intensity, photoresistor=-1, timestamp=0):
        url = 'https://httpbin.org/post'  # TODO Set server url
        post_fields = {'area': self.area, 'action': this_action, 'intensity': intensity, 'photoresistor': photoresistor,
                       'timestamp': timestamp}

        request = Request(url, urlencode(post_fields).encode())
        json_sent = urlopen(request).read().decode()
        print(json_sent)

    def car_detected(self):
        ledPWM.set_led_intensity(self.pin, self.lamp_policy_on.intensity)
        self.send_post(action.car_detected.value, self.lamp_policy_on.intensity)

    def set_to_energy(self):
        ledPWM.set_led_intensity(self.pin, self.lamp_energy.intensity)
        self.send_post(action.energy_saving.value, self.lamp_energy.intensity)

    def to_json(self):
        return json.dumps([self.lamp_id, self.lamp_policy_on, self.lamp_policy_off, self.lamp_energy],
                          default=lambda o: o.__dict__, indent=4)

    @staticmethod
    def get_delta(start_h, start_m, start_s, end_h, end_m, end_s):
        today = datetime.today()
        start = today.replace(hour=start_h, minute=start_m, second=start_s)
        end = today.replace(hour=end_h, minute=end_m, second=end_s)
        if (end - start).total_seconds() < 1:
            end = end.replace(day=end.day + 1)
        return (end - start).total_seconds()

    @staticmethod
    def get_wait(start_h, start_m, start_s, end_h, end_m, end_s):
        today = datetime.today()
        start = today.replace(hour=start_h, minute=start_m, second=start_s)
        end = today.replace(hour=end_h, minute=end_m, second=end_s)
        if (start - today).total_seconds() > 1:
            return (start - today).total_seconds()
        if (end - start).total_seconds() < 1:
            end = end.replace(day=end.day + 1)
        if (end - start).total_seconds() > 24*60*60:
            start = start.replace(day=start.day + 1)
        if (today - end).total_seconds() > 1:
            start = start.replace(day=start.day + 1)
        return (start - today).total_seconds()

    def is_in_schedule(self):
        now = datetime.today()
        elapsed = (now - self.start_time_on).total_seconds()
        return elapsed < self.timeout_on_off

    def is_energy_saving_time(self):
        now = datetime.today()
        elapsed = (now - self.start_time_energy_on).total_seconds()
        print("Are we in energy saving? " + str(elapsed < self.timeout_energy))
        return elapsed < self.timeout_energy
