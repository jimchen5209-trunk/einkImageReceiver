import gc
import json
from waveshare_epd import epd7in5bc
from errorlog import ErrorLogger
from mqtt import MQTT
import framebuf
from machine import Pin

class EInkReceiver():
    def __init__(self):
        self.led=Pin(2, Pin.OUT)
        self.led(1)
        print(f"Memory free: {gc.mem_free()}")
        with open('./config.json', 'r') as f:
            self.data = json.loads(f.read())

        self.__error_logger = ErrorLogger()
        self.__silent = False
        errors = self.__error_logger.read_error()
        self.epd = epd7in5bc.EPD()
        self.epd.init()
        if len(errors) != 0:
            self.__silent = True
            print("Recovered from error")
            print(errors)
            self.__error_logger.clear_error()

        self.mqtt = MQTT()
        self.mqtt.set_on_message(self.on_message)
        self.__temp_black = None
        self.__temp_red = None

    def __display_ready(self):
        buf = bytearray(self.epd.width * self.epd.height// 8)
        fb = framebuf.FrameBuffer(buf, self.epd.width, self.epd.height, framebuf.MONO_HLSB)
        fb.fill(1)
        fb.text("Ready to receive image", 10, 10 ,0)
        buf_r = bytearray(self.epd.width * self.epd.height// 8)
        fb_r = framebuf.FrameBuffer(buf_r, self.epd.width, self.epd.height, framebuf.MONO_HLSB)
        fb_r.fill(1)
        fb_r.text("Ready to receive image", 10, 18 ,0)
        print(f"Memory free: {gc.mem_free()}")
        self.epd.display(buf, buf_r)

    def on_message(self, topic, payload):
        self.led(1)
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
                    if topic.decode('UTF-8').endswith("black"):
                        self.__temp_black = buf
                    elif topic.decode('UTF-8').endswith("red"):
                        self.__temp_red = buf
                elif "ERROR" not in message:
                    self.__save(topic, eval(message))
        
        self.led(0)

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
        if not self.__silent:
            self.__display_ready()
            gc.collect()
        self.epd.sleep()
        self.led(0)
        self.mqtt.listen()

main = EInkReceiver()
main.listen()