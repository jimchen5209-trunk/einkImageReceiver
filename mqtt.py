import json
from umqttsimple import MQTTClient
import ubinascii
from machine import unique_id, reset
from errorlog import ErrorLogger
from led import Led

class MQTT:
    def __init__(self):
        with open('./config.json', 'r') as f:
            self.__data = json.loads(f.read())

        self.__host = self.__data['mqtt']['host']
        self.__port = self.__data['mqtt']['port']
        self.__topic = self.__data['mqtt']['topic']
        self.__username = self.__data['mqtt']['username']
        self.__password = self.__data['mqtt']['password']
        self.__keepalive = 60

        # connect to mqtt client
        self.__mqtt = MQTTClient(
            client_id=ubinascii.hexlify(unique_id()),
            server=self.__host,
            port=self.__port,
            user=self.__username,
            password=self.__password,
            keepalive=self.__keepalive
        )

        self.__mqtt.connect()

    def send_message(self, msg):
        self.__mqtt.publish(self.__topic, msg)

    def send_topic_message(self, topic, msg):
        self.__mqtt.publish(topic, msg)

    def set_on_message(self, f):
        self.__mqtt.set_callback(f)

    def listen(self):
        self.__mqtt.subscribe(self.__topic)
        self.__mqtt.subscribe(f"{self.__topic}/black")
        self.__mqtt.subscribe(f"{self.__topic}/red")
        while True:
            try:
                self.__mqtt.check_msg()
            except OSError as e:
                led = Led()
                led.flash(3)
                print(f"MQTT error {e}")
                self.__mqtt.disconnect()
                self.__mqtt.connect()
                self.__mqtt.subscribe(self.__topic)
                self.__mqtt.subscribe(f"{self.__topic}/black")
                self.__mqtt.subscribe(f"{self.__topic}/red")
                print("MQTT connection restored")
                led.turn_off()
            except MemoryError as e:
                print(e)
                self.send_message("ERROR")
                error_logger = ErrorLogger()
                error_times = error_logger.add_error('Memory error')
                error_logger.retry(error_times)
