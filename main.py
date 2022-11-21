import json
from waveshare_epd import epd1in54_V2
from errorlog import ErrorLogger
from mqtt import MQTT
from led import Led

class EInkReceiver():
    def __init__(self):
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
        self.__led.turn_off()

    def listen(self):
        self.epd.sleep()
        self.__led.turn_off()
        self.mqtt.listen()

main = EInkReceiver()
main.listen()