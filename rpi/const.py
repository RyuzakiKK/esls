
class CONST(object):
    VERSION = "1.0"
    GENERAL = "GENERAL"
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
    SERVER_URL = "https://esls.tk/esls/api/" + VERSION + "/"
    CHANGE_LIGHT = "changeLightIntensity"
    CHANGE_POLICY = "changePolicy"
    ERROR = "notifyError"

    def __setattr__(self, *_):
        pass
