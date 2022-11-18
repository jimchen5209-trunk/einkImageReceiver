import gc
import json
from waveshare_epd import epd7in5bc
from errorlog import ErrorLogger
from mqtt import MQTT
import framebuf
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
        self.epd = epd7in5bc.EPD()
        self.epd.init()
        if len(errors) != 0:
            print("Recovered from error")
            print(errors)
            self.__error_logger.clear_error()

        self.mqtt = MQTT()
        self.mqtt.set_on_message(self.on_message)
        self.__temp_black = None
        self.__temp_red = None

    def on_message(self, topic, payload):
        self.__led.turn_on()
        print(topic.decode('UTF-8'))
        if topic.decode('UTF-8').startswith(self.data['mqtt']['topic']):
            try: 
                gc.collect()
                message = payload.decode('UTF-8')
            except UnicodeError:
                self.__save(topic, payload)
            else:
                if message == "CLEAR":
                    self.epd.init()
                    self.epd.Clear()
                elif message == "BLANK":
                    buf = bytearray(self.epd.width * self.epd.height// 8)
                    fb = framebuf.FrameBuffer(buf, self.epd.width, self.epd.height, framebuf.MONO_HLSB)
                    fb.fill(1)
                    self.__save(topic, buf)
                elif "ERROR" not in message:
                    self.__save(topic, eval(message))

        self.__led.turn_off()

    def __save(self, topic, buffer):
        if topic.decode('UTF-8').endswith("black"):
            self.__temp_black = buffer
            if self.__temp_red != None:
                self.__display()
            else:
                print("Black stored, waiting for red.")

        if topic.decode('UTF-8').endswith("red"):
            self.__temp_red = buffer
            if self.__temp_black != None:
                self.__display()
            else:
                print("Red stored, waiting for black.")

    def __display(self):
        self.epd.init()
        try:
            print(f"Memory free: {gc.mem_free()}")
            self.epd.display(self.__temp_black, self.__temp_red)
        except Exception as e:
            print(e)
            self.mqtt.send_message("ERROR")
        self.__temp_black = None
        self.__temp_red = None
        self.epd.sleep()
        gc.collect()

    def listen(self):
        self.epd.sleep()
        self.__led.turn_off()
        self.mqtt.listen()

main = EInkReceiver()
main.listen()