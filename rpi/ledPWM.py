import threading

# import RPi.GPIO as GPIO
import RPiMockGPIO as GPIO

frequency = 100
cv = threading.Condition()
current_intensity = {}


def set_led_intensity(pin, intensity):
    with cv:
        current_intensity[pin] = intensity
        GPIO.setup(pin, GPIO.OUT)
        GPIO.PWM(pin, frequency).start(intensity)


def get_led_intensity(pin):
    with cv:
        return current_intensity.get(pin, None)
