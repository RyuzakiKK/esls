import pickle
import configparser
import threading
import os.path

from flask import Flask, jsonify, abort, make_response, request
from flask_httpauth import HTTPBasicAuth

from lamp import Lamp
from lampEnergySaving import LampEnergySaving
from lampPolicy import LampPolicy
from photoresistor import Photoresistor
from ultrasonic import Ultrasonic

app = Flask(__name__)
auth = HTTPBasicAuth()

lights = []
version = "v0.1"
intensity = "intensity"
time_h = "time_h"
time_m = "time_m"
time_h_on = "time_h_on"
time_m_on = "time_m_on"
time_h_off = "time_h_off"
time_m_off = "time_m_off"
photoresistor = "photoresistor"
path_lights = "lights/light"
extension = ".cfg"
user = ""
password = ""
cv = threading.Condition()
lock = threading.Lock()
readers = 0
want_to_write = 0
lamp_number = 0


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
            ret_val = future.get(timeout=0.2), 201
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
    with cv:
        want_to_write += 1
        while readers > 0:
            cv.wait()
        want_to_write -= 1
        global lamp_number
        if lamp_id < lamp_number and sanity_check(request.json):
            if intensity in request.json:
                new_intensity = int(request.json[intensity])
            else:
                new_intensity = 100
            policy_on = LampPolicy(new_intensity, int(request.json[time_h]), int(request.json[time_m]),
                                   int(request.json[photoresistor]))
            lights[lamp_id].lamp_policy_on = policy_on
            lights[lamp_id].update_schedules()
            lights[lamp_id].start_schedule_on()
            config = configparser.ConfigParser()
            config.read(path_lights + str(lamp_id) + extension)
            config['LampPolicyOn'][intensity] = new_intensity
            config['LampPolicyOn'][time_h] = int(request.json[time_h])
            config['LampPolicyOn'][time_m] = int(request.json[time_m])
            config['LampPolicyOn'][photoresistor] = int(request.json[photoresistor])
            with open(path_lights + str(lamp_id) + extension, 'w') as configfile:
                config.write(configfile)
            return jsonify({"result": "ok"}), 201
        else:
            abort(400)


@app.route("/esls/api/" + version + "/policies/lamp/<int:lamp_id>/off", methods=['POST'])
@auth.login_required
def set_lamp_policy_off(lamp_id):
    global readers
    global want_to_write
    if not request.json:
        abort(400)
    with cv:
        want_to_write += 1
        while readers > 0:
            cv.wait()
        want_to_write -= 1
        global lamp_number
        if lamp_id < lamp_number and sanity_check(request.json):
            policy_off = LampPolicy(0, int(request.json[time_h]), int(request.json[time_m]),
                                    int(request.json[photoresistor]))
            lights[lamp_id].lamp_policy_off = policy_off
            lights[lamp_id].update_schedules()
            lights[lamp_id].start_schedule_on()
            config = configparser.ConfigParser()
            config.read(path_lights + str(lamp_id) + extension)
            config['LampPolicyOff'][intensity] = 0
            config['LampPolicyOff'][time_h] = int(request.json[time_h])
            config['LampPolicyOff'][time_m] = int(request.json[time_m])
            config['LampPolicyOff'][photoresistor] = int(request.json[photoresistor])
            with open(path_lights + str(lamp_id) + extension, 'w') as configfile:
                config.write(configfile)
            return jsonify({"result": "ok"}), 201
        abort(400)


@app.route("/esls/api/" + version + "/policies/lamp/<int:lamp_id>/energy", methods=['POST'])
@auth.login_required
def set_energy_saving(lamp_id):
    global readers
    global want_to_write
    if not request.json:
        abort(400)
    with cv:
        want_to_write += 1
        while readers > 0:
            cv.wait()
        want_to_write -= 1
        global lamp_number
        if lamp_id < lamp_number and sanity_check(request.json):
            lamp_energy = LampEnergySaving(int(request.json[intensity]), int(request.json[time_h_on]),
                                           int(request.json[time_m_on]), int(request.json[time_h_off]),
                                           int(request.json[time_m_off]))
            lights[lamp_id].lamp_energy = lamp_energy
            lights[lamp_id].update_schedules()
            lights[lamp_id].start_schedule_energy_on()
            config = configparser.ConfigParser()
            config.read(path_lights + str(lamp_id) + extension)
            config['LampEnergySaving'][intensity] = int(request.json[intensity])
            config['LampEnergySaving'][time_h_on] = int(request.json[time_h_on])
            config['LampEnergySaving'][time_m_on] = int(request.json[time_m_on])
            config['LampEnergySaving'][time_h_off] = int(request.json[time_h_off])
            config['LampEnergySaving'][time_m_off] = int(request.json[time_m_off])
            with open(path_lights + str(lamp_id) + extension, 'w') as configfile:
                config.write(configfile)
            return jsonify({"result": "ok"}), 201
        abort(400)


def sanity_check(reqjs):
    try:
        if intensity in reqjs and (int(reqjs[intensity]) < 0 or int(reqjs[intensity]) > 100):
            return False
        elif time_h in reqjs and time_m in reqjs and photoresistor in reqjs:
            if int(reqjs[time_h]) < 0 or int(reqjs[time_h]) > 23:
                return False
            elif int(reqjs[time_m]) < 0 or int(reqjs[time_m]) > 59:
                return False
            elif int(reqjs[photoresistor]) < 0 or int(reqjs[photoresistor]) > 200:
                return False
            else:
                return True
        elif time_h_on in reqjs and time_m_on in reqjs and time_h_off in reqjs and time_m_off in reqjs:
            if int(reqjs[time_h_on]) < 0 or int(reqjs[time_h_on]) > 23:
                return False
            elif int(reqjs[time_m_on]) < 0 or int(reqjs[time_m_on]) > 59:
                return False
            elif int(reqjs[time_h_off]) < 0 or int(reqjs[time_h_off]) > 23:
                return False
            elif int(reqjs[time_m_off]) < 0 or int(reqjs[time_m_off]) > 59:
                return False
            else:
                return True
        else:
            return False
    except ValueError:
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
        if os.path.isfile(path_lights + str(lamp_number) + extension):
            lamp_number += 1
        else:
            still_reading = False
    for i in range(lamp_number):
        config.read(path_lights + str(i) + extension)
        lamp_id = config['GENERAL']['lamp_id']
        lamp_pin = config['GENERAL']['lamp_pin']
        pl_intensity_on = config['LampPolicyOn'][intensity]
        pl_time_h_on = config['LampPolicyOn'][time_h]
        pl_time_m_on = config['LampPolicyOn'][time_m]
        pl_photoresistor_on = config['LampPolicyOn'][photoresistor]
        pl_intensity_off = config['LampPolicyOff'][intensity]
        pl_time_h_off = config['LampPolicyOff'][time_h]
        pl_time_m_off = config['LampPolicyOff'][time_m]
        pl_photoresistor_off = config['LampPolicyOff'][photoresistor]
        en_intensity = config['LampEnergySaving'][intensity]
        en_time_h_on = config['LampEnergySaving'][time_h_on]
        en_time_m_on = config['LampEnergySaving'][time_m_on]
        en_time_h_off = config['LampEnergySaving'][time_h_off]
        en_time_m_off = config['LampEnergySaving'][time_m_off]
        lamp_policy_on = LampPolicy(pl_intensity_on, pl_time_h_on, pl_time_m_on, pl_photoresistor_on)
        lamp_policy_off = LampPolicy(pl_intensity_off, pl_time_h_off, pl_time_m_off, pl_photoresistor_off)
        lamp_energy = LampEnergySaving(en_intensity, en_time_h_on, en_time_m_on, en_time_h_off, en_time_m_off)
        lamp_proxy = Lamp.start(lamp_id, lamp_number, lamp_pin, pr_proxy, us_proxy_1, us_proxy_2, lamp_policy_on,
                                lamp_policy_off, lamp_energy).proxy()
        lamp_proxy.set_self_proxy(lamp_proxy)
        lamp_proxy.update_schedules()
        lamp_proxy.start_schedule_on()
        lamp_proxy.start_schedule_energy_on()
        lights.append(lamp_proxy)


def main():
    pr_proxy = Photoresistor.start().proxy()
    us_proxy_1 = Ultrasonic.start(1, 2, True, 1).proxy()
    us_proxy_2 = Ultrasonic.start(1, 2, False, 1).proxy()
    config = configparser.ConfigParser()
    config.read("config" + extension)
    global user
    user = config['DEFAULT']['User']
    global password
    password = config['DEFAULT']['Pass']
    load_lights_ini(pr_proxy, us_proxy_1, us_proxy_2)


if __name__ == '__main__':
    main()
    # app.run(debug=True, threaded=True)
    app.run(threaded=True)
