import threading

# import RPi.GPIO as GPIO
import RPiMockGPIO as GPIO

frequency = 100
cv = threading.Condition()
led_list = {}


def set_led_intensity(pin, intensity):
    with cv:
        p = led_list.get(pin, None)
        if p is None:
            p = GPIO.PWM(pin, frequency)
            p.start(intensity)
        else:
            p = p[1]
            p.ChangeDutyCycle(intensity)
        led_list[pin] = [intensity, p]


def get_led_intensity(pin):
    with cv:
        led = led_list.get(pin, None)
        if led is not None:
            led = led[0]
        return led
