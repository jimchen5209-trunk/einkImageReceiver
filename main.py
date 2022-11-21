import gc
import json
from waveshare_epd import epd1in54_V2
from errorlog import ErrorLogger
from mqtt import MQTT
from led import Led

class EInkReceiver():
    def __init__(self):
        print(f"Memory free: {gc.mem_free()}")
        self.__led = Led()
        self.__led.turn_on()
        with open('./config.json', 'r') as f:
            self.data = json.loads(f.read())

        self.__error_logger = ErrorLogger()
        errors = self.__error_logger.read_error()
        self.epd = epd1in54_V2.EPD()
        self.epd.init(0)
        if len(errors) != 0:
            print("Recovered from error")
            print(errors)
            self.__error_logger.clear_error()

        self.mqtt = MQTT()
        self.mqtt.set_on_message(self.on_message)

    def on_message(self, topic, payload):
        self.__led.turn_on()
        print(topic.decode('UTF-8'))
        if topic.decode('UTF-8') == self.data['mqtt']['topic']:
            gc.collect()
            try:
                message = payload.decode('UTF-8')
            except UnicodeError:
                self.__save(payload)
            else:
                if message == "CLEAR":
                    self.epd.init(0)
                    self.epd.Clear(0xFF)
                elif "ERROR" not in message:
                    self.__save(eval(message))

        self.__led.turn_off()

    def __save(self, buffer):
        self.__temp_black = buffer
        self.__display()

    def __display(self):
        self.epd.init(0)
        try:
            print(f"Memory free: {gc.mem_free()}")
            self.epd.display(self.__temp_black)
        except Exception as e:
            print(e)
            self.mqtt.send_message("ERROR")
        self.__temp_black = None
        self.epd.sleep()
        gc.collect()

    def listen(self):
        self.epd.sleep()
        self.__led.turn_off()
        self.mqtt.listen()

main = EInkReceiver()
main.listen()