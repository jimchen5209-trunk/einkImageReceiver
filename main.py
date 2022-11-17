import gc
import json
from waveshare_epd import epd7in5bc
from errorlog import ErrorLogger
from mqtt import MQTT
import framebuf

class EInkReceiver():
    def __init__(self):
        print(f"Memory free: {gc.mem_free()}")
        with open('./config.json', 'r') as f:
            self.data = json.loads(f.read())

        self.__error_logger = ErrorLogger()
        self.__silent = False
        errors = self.__error_logger.read_error()
        self.epd = epd7in5bc.EPD()
        if len(errors) != 0:
            self.__silent = True
            self.epd.init()
            print("Recovered from error")
            print(errors)
            self.__error_logger.clear_error()
        else:
            self.epd.init()
            print(f"Memory free: {gc.mem_free()}")
            self.epd.Clear()
            print(f"Memory free: {gc.mem_free()}")
            gc.collect()
            print(f"Memory free after gc: {gc.mem_free()}")
            self.__display_init()
            gc.collect()
            print(f"Memory free after gc: {gc.mem_free()}")

        self.mqtt = MQTT()
        self.mqtt.set_on_message(self.on_message)

    def __display_init(self):
        buf = bytearray(self.epd.width * self.epd.height // 8)
        fb = framebuf.FrameBuffer(buf, self.epd.width, self.epd.height, framebuf.MONO_HLSB)
        fb.fill(1)
        fb.text("Initializing", 10, 10 ,0)
        buf_r = bytearray(self.epd.width * self.epd.height// 8)
        fb_r = framebuf.FrameBuffer(buf_r, self.epd.width, self.epd.height, framebuf.MONO_HLSB)
        fb_r.fill(1)
        fb_r.text("Initializing", 10, 18 ,0)
        print(f"Memory free: {gc.mem_free()}")
        self.epd.display(buf, buf_r)
    
    def __display_ready(self):
        buf = bytearray(self.epd.width * self.epd.height// 8)
        fb = framebuf.FrameBuffer(buf, self.epd.width, self.epd.height, framebuf.MONO_HLSB)
        fb.fill(1)
        fb.text("Ready to receive imagge", 10, 10 ,0)
        buf_r = bytearray(self.epd.width * self.epd.height// 8)
        fb_r = framebuf.FrameBuffer(buf_r, self.epd.width, self.epd.height, framebuf.MONO_HLSB)
        fb_r.fill(1)
        fb_r.text("Ready to receive imagge", 10, 18 ,0)
        print(f"Memory free: {gc.mem_free()}")
        self.epd.display(buf, buf_r)

    def on_message(self, topic, payload):
        print(topic.decode('UTF-8'))
        if topic.decode('UTF-8') == self.data['mqtt']['topic']:
            try: 
                gc.collect()
                message = payload.decode('UTF-8')
            except UnicodeError:
                self.__display(payload)
            else:
                if message == "CLEAR":
                    self.epd.init()
                    self.epd.Clear()
                elif "ERROR" not in message:
                    self.__display(eval(message))
            self.epd.sleep()

    def __display(self, buff_b):
        self.epd.init()
        buf_r = bytearray(self.epd.width * self.epd.height// 8)
        fb_r = framebuf.FrameBuffer(buf_r, self.epd.width, self.epd.height, framebuf.MONO_HLSB)
        fb_r.fill(1)
        try:
            print(f"Memory free: {gc.mem_free()}")
            self.epd.display(buff_b,buf_r)
        except Exception as e:
            print(e)
            self.mqtt.send_message("ERROR")
        gc.collect()

    def listen(self):
        if not self.__silent:
            self.__display_ready()
            gc.collect()
        self.epd.sleep()
        self.mqtt.listen()

main = EInkReceiver()
main.listen()