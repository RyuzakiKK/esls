from datetime import datetime
import pickle
import configparser
import threading
import os.path
import ssl
from distutils.util import strtobool

import logging
from flask import Flask, jsonify, abort, make_response, request
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS

import ledPWM
from lamp import Lamp
from lampEnergySaving import LampEnergySaving
from lampPolicy import LampPolicy
from photoresistor import Photoresistor
from ultrasonic import Ultrasonic
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from pykka import ThreadingActor

app = Flask(__name__)
auth = HTTPBasicAuth()
CORS(app)

lights = []
version = "1.0"
INTENSITY = "intensity"
TIME_H = "time_h"
TIME_M = "time_m"
TIME_H_ON = "time_h_on"
TIME_M_ON = "time_m_on"
TIME_H_OFF = "time_h_off"
TIME_M_OFF = "time_m_off"
PHOTORESISTOR = "photoresistor"
LAMP_POLICY_ON = "LampPolicyOn"
LAMP_POLICY_OFF = "LampPolicyOff"
LAMP_ENERGY_SAVING = "LampEnergySaving"
RIGHT_LANE = "right_lane"
PATH_LIGHTS = "lights/light"
PATH_NEIGHBORS = "neighbors/nearby"
EXTENSION = ".cfg"
SERVER_URL = "https://supersecureserver.com/esls/api/1.0/changePolicy"
user = ""
password = ""
cv = threading.Condition()
lock = threading.Lock()
readers = 0
want_to_write = 0
lamp_number = 0
old_intensity = {}
neighbors = [[], []]


@auth.get_password
def get_password(username):
    if username == user:
        return password
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def internal_error(_):
    return make_response(jsonify({'error': 'Internal error, the server may be overloaded'}), 500)


@app.route("/esls/api/" + version + "/policies/<int:lamp_id>", methods=['GET'])
@auth.login_required
def get_lamp_policies(lamp_id):
    global readers
    error = False
    error_number = 0
    ret_val = 0
    with cv:
        while want_to_write > 0:
            cv.wait()
        readers += 1

    if lamp_id < len(lights):
        future = lights[lamp_id].to_json()
        try:
            ret_val = future.get(timeout=0.2), 200
        except Exception:
            error = True
            error_number = 500
    else:
        error = True
        error_number = 404

    with cv:
        readers -= 1
        if not readers:
            cv.notifyAll()
        if not error:
            return ret_val
        else:
            abort(error_number)


@app.route("/esls/api/" + version + "/policies/lamp/<int:lamp_id>/on", methods=['POST'])
@auth.login_required
def set_lamp_policy_on(lamp_id):
    global readers
    global want_to_write
    if not request.json:
        abort(400)
    try:
        new_intensity = int(request.json[INTENSITY]) if INTENSITY in request.json else 100
        new_h_on = int(request.json[TIME_H])
        new_m_on = int(request.json[TIME_M])
        new_photoresistor = int(request.json[PHOTORESISTOR])
        with cv:
            want_to_write += 1
            while readers > 0:
                cv.wait()
            want_to_write -= 1
            global lamp_number
            if lamp_id < lamp_number and sanity_check(lamp_id, pl_intensity_on=new_intensity, pl_time_h_on=new_h_on,
                                                      pl_time_m_on=new_m_on, photoresistor_on=new_photoresistor):
                policy_on = LampPolicy(new_intensity, new_h_on, new_m_on, new_photoresistor)
                lights[lamp_id].lamp_policy_on = policy_on
                lights[lamp_id].update_schedules()
                lights[lamp_id].start_schedule_on()
                config = configparser.ConfigParser()
                config.read(PATH_LIGHTS + str(lamp_id) + EXTENSION)
                config[LAMP_POLICY_ON][INTENSITY] = str(new_intensity)
                config[LAMP_POLICY_ON][TIME_H] = str(new_h_on)
                config[LAMP_POLICY_ON][TIME_M] = str(new_m_on)
                config[LAMP_POLICY_ON][PHOTORESISTOR] = str(new_photoresistor)
                # post_fields = {'area': config['GENERAL']['lamp_area'], 'timestamp': '0'}
                # send_post(SERVER_URL, post_fields)
                with open(PATH_LIGHTS + str(lamp_id) + EXTENSION, 'w') as configfile:
                    config.write(configfile)
                return jsonify({"result": "ok"}), 200
            else:
                abort(400)
    except KeyError:
        abort(400)


@app.route("/esls/api/" + version + "/policies/lamp/<int:lamp_id>/off", methods=['POST'])
@auth.login_required
def set_lamp_policy_off(lamp_id):
    global readers
    global want_to_write
    if not request.json:
        abort(400)
    try:
        new_h_off = int(request.json[TIME_H])
        new_m_off = int(request.json[TIME_M])
        new_photoresistor = int(request.json[PHOTORESISTOR])
        with cv:
            want_to_write += 1
            while readers > 0:
                cv.wait()
            want_to_write -= 1
            global lamp_number
            if lamp_id < lamp_number and sanity_check(lamp_id, pl_time_h_off=new_h_off, pl_time_m_off=new_m_off,
                                                      photoresistor_off=new_photoresistor):
                policy_off = LampPolicy(0, new_h_off, new_m_off, new_photoresistor)
                lights[lamp_id].lamp_policy_off = policy_off
                lights[lamp_id].update_schedules()
                lights[lamp_id].start_schedule_on()
                config = configparser.ConfigParser()
                config.read(PATH_LIGHTS + str(lamp_id) + EXTENSION)
                config[LAMP_POLICY_OFF][INTENSITY] = '0'
                config[LAMP_POLICY_OFF][TIME_H] = str(new_h_off)
                config[LAMP_POLICY_OFF][TIME_M] = str(new_m_off)
                config[LAMP_POLICY_OFF][PHOTORESISTOR] = str(new_photoresistor)
                # post_fields = {'area': config['GENERAL']['lamp_area'], 'timestamp': '0'}
                # send_post(SERVER_URL, post_fields)
                with open(PATH_LIGHTS + str(lamp_id) + EXTENSION, 'w') as configfile:
                    config.write(configfile)
                return jsonify({"result": "ok"}), 200
            abort(400)
    except KeyError:
        abort(400)


@app.route("/esls/api/" + version + "/policies/lamp/<int:lamp_id>/energy", methods=['POST'])
@auth.login_required
def set_energy_saving(lamp_id):
    global readers
    global want_to_write
    if not request.json:
        abort(400)
    try:
        new_intensity = int(request.json[INTENSITY])
        new_h_on = int(request.json[TIME_H_ON])
        new_m_on = int(request.json[TIME_M_ON])
        new_h_off = int(request.json[TIME_H_OFF])
        new_m_off = int(request.json[TIME_M_OFF])
        with cv:
            want_to_write += 1
            while readers > 0:
                cv.wait()
            want_to_write -= 1
            global lamp_number
            if lamp_id < lamp_number and sanity_check(lamp_id, en_intensity=new_intensity, en_time_h_on=new_h_on,
                                                      en_time_m_on=new_m_on, en_time_h_off=new_h_off,
                                                      en_time_m_off=new_m_off):
                lamp_energy = LampEnergySaving(new_intensity, new_h_on, new_m_on, new_h_off, new_m_off)
                lights[lamp_id].lamp_energy = lamp_energy
                lights[lamp_id].update_schedules()
                lights[lamp_id].start_schedule_energy_on()
                config = configparser.ConfigParser()
                config.read(PATH_LIGHTS + str(lamp_id) + EXTENSION)
                config[LAMP_ENERGY_SAVING][INTENSITY] = str(new_intensity)
                config[LAMP_ENERGY_SAVING][TIME_H_ON] = str(new_h_on)
                config[LAMP_ENERGY_SAVING][TIME_M_ON] = str(new_m_on)
                config[LAMP_ENERGY_SAVING][TIME_H_OFF] = str(new_h_off)
                config[LAMP_ENERGY_SAVING][TIME_M_OFF] = str(new_m_off)
                # post_fields = {'area': config['GENERAL']['lamp_area'], 'timestamp': '0'}
                # send_post(SERVER_URL, post_fields)
                with open(PATH_LIGHTS + str(lamp_id) + EXTENSION, 'w') as configfile:
                    config.write(configfile)
                return jsonify({"result": "ok"}), 200
            abort(400)
    except KeyError:
        abort(400)


@app.route("/esls/api/" + version + "/internal/notify", methods=['POST'])
@auth.login_required
def notify_received():
    global readers
    global want_to_write
    if not request.json:
        abort(400)
    with cv:
        while want_to_write > 0:
            cv.wait()
        readers += 1
    right_lane = False
    try:
        right_lane = int(request.json[RIGHT_LANE])
    except KeyError:
        abort(400)

    for lamp in lights:
        lamp.ultrasonic_notify(1, 2, right_lane, notified=True)
    with cv:
        readers -= 1
        if not readers:
            cv.notifyAll()
    return jsonify({"result": "ok"}), 200


@app.route("/esls/api/" + version + "/debug/lamp/<int:lamp_id>/on", methods=['POST'])
@auth.login_required
def force_lamp_on(lamp_id):
    if not request.json:
        abort(400)
    global lamp_number
    global old_intensity
    if lamp_id < lamp_number:
        debug_future = lights[lamp_id].debug
        pin_future = lights[lamp_id].pin
        debug = debug_future.get(timeout=0.2)
        pin = pin_future.get(timeout=0.2)
        try:
            new_intensity = int(request.json[INTENSITY])
            if not debug:
                lights[lamp_id].debug = True
                old_intensity[lamp_id] = ledPWM.get_led_intensity(pin)
            ledPWM.set_led_intensity(pin, new_intensity)
            return jsonify({"result": "lamp is now on"}), 200
        except KeyError:
            abort(400)


@app.route("/esls/api/" + version + "/debug/lamp/<int:lamp_id>/off", methods=['POST'])
@auth.login_required
def force_lamp_off(lamp_id):
    if len(request.form) > 0:
        abort(400)
    global lamp_number
    global old_intensity
    if lamp_id < lamp_number:
        with cv:
            debug_future = lights[lamp_id].debug
            pin_future = lights[lamp_id].pin
            debug = debug_future.get(timeout=0.2)
            pin = pin_future.get(timeout=0.2)
            if not debug:
                lights[lamp_id].debug = True
                old_intensity[lamp_id] = ledPWM.get_led_intensity(pin)
            ledPWM.set_led_intensity(pin, 0)
            return jsonify({"result": "lamp is now off"}), 200


@app.route("/esls/api/" + version + "/debug/lamp/<int:lamp_id>/stop", methods=['POST'])
@auth.login_required
def force_lamp_stop(lamp_id):
    if len(request.form) > 0:
        abort(400)
    global lamp_number
    global old_intensity
    if lamp_id < lamp_number:
        with cv:
            debug_future = lights[lamp_id].debug
            pin_future = lights[lamp_id].pin
            debug = debug_future.get(timeout=0.2)
            pin = pin_future.get(timeout=0.2)
            if debug:
                lights[lamp_id].debug = False
                ledPWM.set_led_intensity(pin, old_intensity.pop(lamp_id, 0))
                return jsonify({"result": "Debug stopped"}), 200
            else:
                return jsonify({"result": "Debug was already stopped"}), 200


def send_post(url, post_fields):
    request_sent = Request(url, urlencode(post_fields).encode())
    json_sent = urlopen(request_sent).read().decode()
    print(json_sent)


def sanity_check(lamp_id, pl_intensity_on=None, pl_time_h_on=None, pl_time_m_on=None, photoresistor_on=None,
                 pl_time_h_off=None, pl_time_m_off=None, photoresistor_off=None, en_intensity=None,
                 en_time_h_on=None, en_time_m_on=None, en_time_h_off=None, en_time_m_off=None):
    try:
        config = configparser.ConfigParser()
        config.read(PATH_LIGHTS + str(lamp_id) + EXTENSION)
        pl_intensity_on = int(config[LAMP_POLICY_ON][INTENSITY]) if pl_intensity_on is None else pl_intensity_on
        pl_time_h_on = int(config[LAMP_POLICY_ON][TIME_H]) if pl_time_h_on is None else pl_time_h_on
        pl_time_m_on = int(config[LAMP_POLICY_ON][TIME_M]) if pl_time_m_on is None else pl_time_m_on
        photoresistor_on = int(config[LAMP_POLICY_ON][PHOTORESISTOR]) if photoresistor_on is None else photoresistor_on
        pl_time_h_off = int(config[LAMP_POLICY_OFF][TIME_H]) if pl_time_h_off is None else pl_time_h_off
        pl_time_m_off = int(config[LAMP_POLICY_OFF][TIME_M]) if pl_time_m_off is None else pl_time_m_off
        photoresistor_off = int(
            config[LAMP_POLICY_OFF][PHOTORESISTOR]) if photoresistor_off is None else photoresistor_off
        en_intensity = int(config[LAMP_ENERGY_SAVING][INTENSITY]) if en_intensity is None else en_intensity
        en_time_h_on = int(config[LAMP_ENERGY_SAVING][TIME_H_ON]) if en_time_h_on is None else en_time_h_on
        en_time_m_on = int(config[LAMP_ENERGY_SAVING][TIME_M_ON]) if en_time_m_on is None else en_time_m_on
        en_time_h_off = int(config[LAMP_ENERGY_SAVING][TIME_H_OFF]) if en_time_h_off is None else en_time_h_off
        en_time_m_off = int(config[LAMP_ENERGY_SAVING][TIME_M_OFF]) if en_time_m_off is None else en_time_m_off
        if not (0 <= pl_intensity_on <= 100):
            return False
        elif not (0 <= en_intensity <= pl_intensity_on):
            return False
        elif not (photoresistor_on <= photoresistor_off):
            return False
        elif not (0 <= pl_time_h_on <= 23):
            return False
        elif not (0 <= pl_time_m_on <= 59):
            return False
        elif not (0 <= pl_time_h_off <= 23):
            return False
        elif not (0 <= pl_time_m_off <= 59):
            return False
        elif pl_time_h_on == pl_time_h_off and pl_time_m_on == pl_time_m_off:
            return False
        elif not (0 <= en_time_h_on <= 23):
            return False
        elif not (0 <= en_time_m_on <= 59):
            return False
        elif not (0 <= en_time_h_off <= 23):
            return False
        elif not (0 <= en_time_m_off <= 59):
            return False
        elif en_time_h_on == en_time_h_off and en_time_m_on == en_time_m_off:
            return False
        today = datetime.today()
        policy_start = today.replace(hour=pl_time_h_on, minute=pl_time_m_on, second=0)
        policy_end = today.replace(hour=pl_time_h_off, minute=pl_time_m_off, second=0)
        if (policy_end - policy_start).total_seconds() < 1:
            policy_end = policy_end.replace(day=policy_end.day + 1)
        en_start = today.replace(hour=en_time_h_on, minute=en_time_m_on, second=0)
        en_end = today.replace(hour=en_time_h_off, minute=en_time_m_off, second=0)
        if (en_start - policy_start).total_seconds() < 0:
            en_start = en_start.replace(day=en_start.day + 1)
        if (en_end - en_start).total_seconds() < 1:
            en_end = en_end.replace(day=en_end.day + 1)
        if en_start < policy_start or en_end > policy_end:
            return False
        return True
    except (ValueError, KeyError):
        return False


def save_object(lamp, filename):
    with open(filename, 'wb') as output_file:
        pickle.dump([lamp.lamp_id, lamp.lamp_policy_on, lamp.lamp_policy_off, lamp.lamp_energy], output_file,
                    pickle.HIGHEST_PROTOCOL)


def load_object(filename):
    with open(filename, 'rb') as input_file:
        return pickle.load(input_file)


def load_lights_ini(pr_proxy, us_proxy_1, us_proxy_2):
    config = configparser.ConfigParser()
    global lamp_number
    lamp_number = 0
    still_reading = True
    while still_reading:
        if os.path.isfile(PATH_LIGHTS + str(lamp_number) + EXTENSION):
            lamp_number += 1
        else:
            still_reading = False
    for i in range(lamp_number):
        config.read(PATH_LIGHTS + str(i) + EXTENSION)
        lamp_id = int(config['GENERAL']['lamp_id'])
        lamp_pin = int(config['GENERAL']['lamp_pin'])
        lamp_area = int(config['GENERAL']['lamp_area'])
        pl_intensity_on = int(config[LAMP_POLICY_ON][INTENSITY])
        pl_time_h_on = int(config[LAMP_POLICY_ON][TIME_H])
        pl_time_m_on = int(config[LAMP_POLICY_ON][TIME_M])
        pl_photoresistor_on = int(config[LAMP_POLICY_ON][PHOTORESISTOR])
        pl_intensity_off = int(config[LAMP_POLICY_OFF][INTENSITY])
        pl_time_h_off = int(config[LAMP_POLICY_OFF][TIME_H])
        pl_time_m_off = int(config[LAMP_POLICY_OFF][TIME_M])
        pl_photoresistor_off = int(config[LAMP_POLICY_OFF][PHOTORESISTOR])
        en_intensity = int(config[LAMP_ENERGY_SAVING][INTENSITY])
        en_time_h_on = int(config[LAMP_ENERGY_SAVING][TIME_H_ON])
        en_time_m_on = int(config[LAMP_ENERGY_SAVING][TIME_M_ON])
        en_time_h_off = int(config[LAMP_ENERGY_SAVING][TIME_H_OFF])
        en_time_m_off = int(config[LAMP_ENERGY_SAVING][TIME_M_OFF])
        lamp_policy_on = LampPolicy(pl_intensity_on, pl_time_h_on, pl_time_m_on, pl_photoresistor_on)
        lamp_policy_off = LampPolicy(pl_intensity_off, pl_time_h_off, pl_time_m_off, pl_photoresistor_off)
        lamp_energy = LampEnergySaving(en_intensity, en_time_h_on, en_time_m_on, en_time_h_off, en_time_m_off)
        lamp_proxy = Lamp.start(lamp_id, lamp_number, lamp_pin, lamp_area, pr_proxy, us_proxy_1, us_proxy_2,
                                lamp_policy_on, lamp_policy_off, lamp_energy).proxy()
        lamp_proxy.set_self_proxy(lamp_proxy)
        lamp_proxy.update_schedules()
        lamp_proxy.start_schedule_on()
        lamp_proxy.start_schedule_energy_on()
        lights.append(lamp_proxy)


def load_neighbors_ini():
    config = configparser.ConfigParser()
    neighbors_number = 0
    still_reading = True
    while still_reading:
        if os.path.isfile(PATH_NEIGHBORS + str(neighbors_number) + EXTENSION):
            neighbors_number += 1
        else:
            still_reading = False
    global neighbors
    for i in range(neighbors_number):
        config.read(PATH_NEIGHBORS + str(i) + EXTENSION)
        following = config['GENERAL']['following']
        neighbors[strtobool(following)].append(config['GENERAL']['url'])


def notify_nearby(right_lane):
    logging.info(right_lane)
    i = 1 if right_lane else 0
    for nearby in neighbors[i]:
        logging.info(nearby)  # TODO TEST
        send_post(nearby, {'right_lane': right_lane})


def main():
    ThreadingActor.use_daemon_thread = True
    pr_proxy = Photoresistor.start().proxy()
    us_proxy_1 = Ultrasonic.start(1, 2, True, 1).proxy()
    us_proxy_2 = Ultrasonic.start(1, 2, False, 1).proxy()
    config = configparser.ConfigParser()
    config.read("config" + EXTENSION)
    global user
    user = config['DEFAULT']['User']
    global password
    password = config['DEFAULT']['Pass']
    load_lights_ini(pr_proxy, us_proxy_1, us_proxy_2)
    load_neighbors_ini()
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)  # PROTOCOL_SSLv23 is an alias for PROTOCOL_TLS
    context.load_cert_chain('DO.crt', 'DO.key')
    app.run(threaded=True, host='192.168.2.194', port=9020, ssl_context=context)


if __name__ == '__main__':
    main()

