import json
from waveshare_epd import epd1in54_V2
from errorlog import ErrorLogger
from mqtt import MQTT
from machine import Pin

class EInkReceiver():
    def __init__(self):
        with open('./config.json', 'r') as f:
            self.data = json.loads(f.read())

        self.led = Pin(self.data['pins']['indicator_led'], Pin.OUT)
        self.led(0)
        self.__error_logger = ErrorLogger()
        self.__silent = False
        errors = self.__error_logger.read_error()
        self.epd = epd1in54_V2.EPD()
        if len(errors) != 0:
            self.__silent = True
            self.epd.init(0)
            print("Recovered from error")
            print(errors)
            self.__error_logger.clear_error()
        else:
            self.epd.init(0)
            self.epd.Clear(0xFF)
            self.__display_init()

        self.mqtt = MQTT()
        self.mqtt.set_on_message(self.on_message)

    def __display_init(self):
        with open('init.txt', 'r') as fs:
            self.epd.display(eval(fs.readline()))
    
    def __display_ready(self):
        with open('ready.txt', 'r') as fs:
            self.epd.display(eval(fs.readline()))

    def on_message(self, topic, payload):
        self.led(0)
        print(topic.decode('UTF-8'))
        if topic.decode('UTF-8') == self.data['mqtt']['topic']:
            try: 
                message = payload.decode('UTF-8')
            except UnicodeError:
                self.epd.init(0)
                try:
                    self.epd.display(payload)
                except Exception as e:
                    print(e)
                    self.mqtt.send_message("ERROR")
            else:
                if message == "CLEAR":
                    self.epd.init(0)
                    self.epd.Clear(0xFF)
                elif "ERROR" not in message:
                    self.epd.init(0)
                    try:
                        data = eval(message)
                        self.epd.display(data)
                    except Exception as e:
                        print(e)
                        self.mqtt.send_message("ERROR")
            self.epd.sleep()
        self.led(1)

    def listen(self):
        if not self.__silent:
            self.__display_ready()
        self.epd.sleep()
        self.led(1)
        self.mqtt.listen()

main = EInkReceiver()
main.listen()