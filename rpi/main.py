import pickle
import configparser
import threading

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
extension = ".pkl"
user = ""
password = ""
cv = threading.Condition()
lock = threading.Lock()
readers = 0
want_to_write = 0

# TODO number of lights is pre-defined and not editable


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
            ret_val = future.get(timeout=0.8), 201
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
        if lamp_id < len(lights) and sanity_check(request.json):
            policy_off_future = lights[lamp_id].lamp_policy_off
            lamp_energy_future = lights[lamp_id].lamp_energy
            if intensity in request.json:
                policy_on = LampPolicy(int(request.json[intensity]), int(request.json[time_h]),
                                       int(request.json[time_m]), int(request.json[photoresistor]))
            else:
                policy_on = LampPolicy(100, int(request.json[time_h]), int(request.json[time_m]),
                                       int(request.json[photoresistor]))
            lights[lamp_id].lamp_policy_on = policy_on
            lights[lamp_id].update_schedules()
            lights[lamp_id].start_schedule_on()
            policy_off = None
            lamp_energy = None
            try:
                policy_off = policy_off_future.get(timeout=0.8)
                lamp_energy = lamp_energy_future.get(timeout=0.8)
            except Exception:
                abort(500)
            save_object(Lamp(lamp_id, None, None, policy_on, policy_off, lamp_energy),
                        path_lights + str(lamp_id) + extension)
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
        if lamp_id < len(lights) and sanity_check(request.json):
            policy_on_future = lights[lamp_id].lamp_policy_on
            lamp_energy_future = lights[lamp_id].lamp_energy
            policy_off = LampPolicy(0, int(request.json[time_h]), int(request.json[time_m]),
                                    int(request.json[photoresistor]))
            lights[lamp_id].lamp_policy_off = policy_off
            lights[lamp_id].update_schedules()
            lights[lamp_id].start_schedule_on()
            policy_on = None
            lamp_energy = None
            try:
                policy_on = policy_on_future.get(timeout=0.8)
                lamp_energy = lamp_energy_future.get(timeout=0.8)
            except Exception:
                abort(500)
            save_object(Lamp(lamp_id, None, None, policy_on, policy_off, lamp_energy), path_lights + str(lamp_id) + extension)
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
        if lamp_id < len(lights) and sanity_check(request.json):
            policy_on_future = lights[lamp_id].lamp_policy_on
            policy_off_future = lights[lamp_id].lamp_policy_off
            lamp_energy = LampEnergySaving(int(request.json[intensity]), int(request.json[time_h_on]),
                                           int(request.json[time_m_on]), int(request.json[time_h_off]),
                                           int(request.json[time_m_off]))
            lights[lamp_id].lamp_energy = lamp_energy
            lights[lamp_id].update_schedules()
            lights[lamp_id].start_schedule_energy_on()
            policy_on = None
            policy_off = None
            try:
                policy_on = policy_on_future.get(timeout=0.8)
                policy_off = policy_off_future.get(timeout=0.8)
            except Exception:
                abort(500)
            save_object(Lamp(lamp_id, None, None, policy_on, policy_off, lamp_energy), path_lights + str(lamp_id) + extension)
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


def main():
    pr_proxy = Photoresistor.start().proxy()
    us_proxy = Ultrasonic.start().proxy()
    config = configparser.ConfigParser()
    config.read("config.cfg")
    global user
    user = config['DEFAULT']['User']
    global password
    password = config['DEFAULT']['Pass']

    # save_object(
    #     Lamp(0, None, None, LampPolicy(100, 11, 46, 50), LampPolicy(0, 5, 30, 50), LampEnergySaving(60, 1, 0, 5, 30)),
    #     path_lights + str(0) + extension)
    # save_object(
    #     Lamp(1, None, None, LampPolicy(100, 11, 46, 50), LampPolicy(0, 5, 30, 50), LampEnergySaving(60, 1, 0, 5, 30)),
    #     path_lights + str(1) + extension)
    # save_object(
    #     Lamp(2, None, None, LampPolicy(100, 19, 0, 50), LampPolicy(0, 5, 30, 50), LampEnergySaving(60, 1, 0, 5, 30)),
    #     path_lights + str(2) + extension)

    try:
        for i in range(10):  # TODO number of lights and initialization
            lamp = load_object(path_lights + str(i) + extension)
            lamp_proxy = Lamp.start(lamp[0], pr_proxy, us_proxy, lamp[1], lamp[2], lamp[3]).proxy()
            lamp_proxy.set_self_proxy(lamp_proxy)
            lamp_proxy.update_schedules()
            lamp_proxy.start_schedule_on()
            lamp_proxy.start_schedule_energy_on()
            lights.append(lamp_proxy)
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    main()
    # app.run(debug=True, threaded=True)
    app.run(threaded=True)
