import json
import utime
from machine import Pin

class Led:
    def __init__(self):
        with open('./config.json', 'r') as f:
            self.__data = json.loads(f.read())
        self.__led = Pin(self.__data['pins']['indicator_led']['pin'], Pin.OUT)
        self.__led_on = 0 if self.__data['pins']['indicator_led']['invert'] else 1
        self.__led_off = 1 if self.__data['pins']['indicator_led']['invert'] else 0

    def turn_on(self):
        self.__led(self.__led_on)

    def turn_off(self):
        self.__led(self.__led_off)

    def flash(self, times = 5):
        for _ in range(times):
            self.turn_off()
            utime.sleep_ms(200)
            self.turn_on()
            utime.sleep_ms(200)
