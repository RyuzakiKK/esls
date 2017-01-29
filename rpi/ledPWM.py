import threading

# import RPi.GPIO as GPIO

frequency = 100
cv = threading.Condition()


def set_led_intensity(pin, intensity):
    with cv:
        pass
        # GPIO.setup(pin, GPIO.OUT)
        # GPIO.PWM(pin, frequency).start(intensity)
