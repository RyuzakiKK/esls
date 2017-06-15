from datetime import datetime, timedelta
import json
import threading
import logging
from enum import Enum
from const import CONST
from main import send_post
import pykka
import ledPWM

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

logger = logging.getLogger(__name__)
action = Enum('action', 'turn_on turn_off energy_saving car_detected')
error = Enum('error', 'generic')
C = CONST()


class Lamp(pykka.ThreadingActor):
    def __init__(self, lamp_id, lamp_number, pin, area, pr_proxy, us_proxy_1, us_proxy_2, lamp_policy_on=None,
                 lamp_policy_off=None, lamp_energy=None):
        super(Lamp, self).__init__()
        self.lamp_id = lamp_id
        self.lamp_number = lamp_number
        self.pin = pin
        self.area = area
        self.pr_proxy = pr_proxy
        self.us_proxy_1 = us_proxy_1
        self.us_proxy_2 = us_proxy_2
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
        self.old_intensity = 0
        ledPWM.set_led_intensity(self.pin, 0)
        self.update_schedules()

    def set_self_proxy(self, lamp_proxy):
        self.my_proxy = lamp_proxy

    def update_schedules(self):
        self.timeout_on_off = self.get_delta(self.lamp_policy_on.time_h, self.lamp_policy_on.time_m, 0,
                                             self.lamp_policy_off.time_h, self.lamp_policy_off.time_m, 0)
        self.timeout_energy = self.get_delta(self.lamp_energy.time_h_on, self.lamp_energy.time_m_on, 0,
                                             self.lamp_energy.time_h_off, self.lamp_energy.time_m_off, 0)

    def start_schedule_on(self):
        wait_t = self.get_wait(self.lamp_policy_on.time_h, self.lamp_policy_on.time_m, 0,
                               self.lamp_policy_off.time_h, self.lamp_policy_off.time_m, 0)
        logger.debug("wait = {0}".format(wait_t))
        self.timer_on.cancel()
        self.timer_on = threading.Timer(wait_t, self.pr_proxy.add_actor, [self.my_proxy])
        self.timer_on.start()
        self.start_time_on = datetime.today() + timedelta(seconds=wait_t)

    def start_schedule_energy_on(self):
        wait_t = self.get_wait(self.lamp_energy.time_h_on, self.lamp_energy.time_m_on, 0,
                               self.lamp_energy.time_h_off, self.lamp_energy.time_m_off, 0)
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
            url = C.SERVER_URL + C.CHANGE_LIGHT
            if self.is_in_schedule():
                if self.on and current_photoresistor > self.lamp_policy_off.photoresistor:
                    self.timer_energy_timeout.cancel()
                    ledPWM.set_led_intensity(self.pin, 0)
                    logger.info("lamp off")
                    self.on = False
                    post_fields = self.create_post_fields(action.turn_off.value, 0, current_photoresistor)
                    send_post(url, post_fields)
                elif not self.on and current_photoresistor < self.lamp_policy_on.photoresistor:
                    if self.is_energy_saving_time():
                        ledPWM.set_led_intensity(self.pin, self.lamp_energy.intensity)
                        logger.info("lamp energy")
                        self.on = True
                        post_fields = self.create_post_fields(action.energy_saving.value, self.lamp_energy.intensity,
                                                              current_photoresistor)
                        send_post(url, post_fields)
                    else:
                        ledPWM.set_led_intensity(self.pin, self.lamp_policy_on.intensity)
                        logger.info("lamp on")
                        self.on = True
                        post_fields = self.create_post_fields(action.turn_on.value, self.lamp_policy_on.intensity,
                                                              current_photoresistor)
                        send_post(url, post_fields)
            else:
                logger.info("schedule is over, see you tomorrow")
                ledPWM.set_led_intensity(self.pin, 0)
                logger.info("lamp off")
                self.on = False
                self.pr_proxy.remove_actor(self.my_proxy)
                post_fields = self.create_post_fields(action.turn_off.value, 0, current_photoresistor)
                send_post(url, post_fields)
                self.start_schedule_on()

    def ultrasonic_notify(self, us_timeout, wait_time, right_lane, notified=False):
        logger.info("[{0}]Received an ultrasonic notify".format(self.lamp_id))
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
                        threading.Timer(wait_time * position, notify_nearby, [right_lane]).start()
                    threading.Timer(wait_time * position, self.car_detected).start()
                    logger.info("[{0}]There is a car! Lamp full power".format(self.lamp_id))
                    self.timer_energy_timeout.cancel()
                    self.timer_energy_timeout = threading.Timer(us_timeout + wait_time * position, self.set_to_energy)
                    self.timer_energy_timeout.start()
            else:
                self.timer_energy_timeout.cancel()
                logger.info("schedule is over, see you tomorrow")
                self.us_proxy_1.remove_actor(self.my_proxy)
                self.us_proxy_2.remove_actor(self.my_proxy)
                self.start_schedule_energy_on()

    def force_on(self, new_intensity):
        if not self.debug:
            self.debug = True
            self.old_intensity = ledPWM.get_led_intensity(self.pin)
        ledPWM.set_led_intensity(self.pin, new_intensity)

    def force_off(self):
        if not self.debug:
            self.debug = True
            self.old_intensity = ledPWM.get_led_intensity(self.pin)
        ledPWM.set_led_intensity(self.pin, 0)

    def stop_debug(self):
        if self.debug:
            self.debug = False
            ledPWM.set_led_intensity(self.pin, self.old_intensity)

    def car_detected(self):
        ledPWM.set_led_intensity(self.pin, self.lamp_policy_on.intensity)
        logger.info("{0} Car detected".format(ledPWM.get_led_intensity(self.pin)))
        url = C.SERVER_URL + C.CHANGE_LIGHT
        post_fields = self.create_post_fields(action.car_detected.value, self.lamp_policy_on.intensity)
        send_post(url, post_fields)

    def set_to_energy(self):
        ledPWM.set_led_intensity(self.pin, self.lamp_energy.intensity)
        logger.info("{0} Set to energy".format(ledPWM.get_led_intensity(self.pin)))
        url = C.SERVER_URL + C.CHANGE_LIGHT
        post_fields = self.create_post_fields(action.energy_saving.value, self.lamp_energy.intensity)
        send_post(url, post_fields)

    def create_post_fields(self, this_action, intensity, photoresistor=-1, timestamp=0):
        return {'area': self.area, 'action': this_action, 'intensity': intensity, 'photoresistor': photoresistor,
                'timestamp': timestamp}

    def to_json(self):
        return json.dumps([self.lamp_id, self.lamp_policy_on, self.lamp_policy_off, self.lamp_energy],
                          default=lambda o: o.__dict__, indent=4)

    @staticmethod
    def get_delta(start_h, start_m, start_s, end_h, end_m, end_s):
        today = datetime.today()
        start = today.replace(hour=start_h, minute=start_m, second=start_s)
        end = today.replace(hour=end_h, minute=end_m, second=end_s)
        if (end - start).total_seconds() < 1:
            end = end + timedelta(days=1)
        return (end - start).total_seconds()

    @staticmethod
    def get_wait(start_h, start_m, start_s, end_h, end_m, end_s):
        today = datetime.today()
        start = today.replace(hour=start_h, minute=start_m, second=start_s)
        end = today.replace(hour=end_h, minute=end_m, second=end_s)
        if (end - start).total_seconds() < 1:
            end = end + timedelta(days=1)
        if (end - start).total_seconds() > 24*60*60:
            start = start + timedelta(days=1)
        if (today - end).total_seconds() > 1:
            start = start + timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        if (start - tomorrow).total_seconds() < 1 < (end - tomorrow).total_seconds():
            today = today + timedelta(days=1)
        return (start - today).total_seconds()

    def is_in_schedule(self):
        now = datetime.today()
        logger.info("now = {0}".format(now))
        logger.info("start time = {0}".format(self.start_time_on))
        elapsed = (now - self.start_time_on).total_seconds()
        logger.info("elapsed {0} seconds, timeout is {1}".format(elapsed, self.timeout_on_off))
        return elapsed < self.timeout_on_off

    def is_energy_saving_time(self):
        now = datetime.today()
        elapsed = (now - self.start_time_energy_on).total_seconds()
        logger.debug("Are we in energy saving? " + str(0 < elapsed < self.timeout_energy))
        return 0 < elapsed < self.timeout_energy
