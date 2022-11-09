import time
from umqttsimple import MQTTClient
import ubinascii
from machine import unique_id, reset


class MQTT:
    def __init__(self):

        with open('./config.json', 'r') as f:
            self.__data = json.loads(f.read())

        self.__host = self.__data
        self.__port = self.__data
        self.__topic = self.__data
        self.__username = self.__data
        self.__password = self.__data
        self.__keepalive = 60

        # connect to mqtt client
        self.mqtt = MQTTClient(
            client_id=ubinascii.hexlify(unique_id()),
            server=self.__host,
            port=self.__port,
            user=self.__username,
            password=self.__password,
            keepalive=self.__keepalive
        )

        self.__mqtt.connect()
        self.__mqtt.subscribe(self.__topic)

    def send_message(self, msg):
        self.__mqtt.publish(self.__topic, msg)

    def send_topic_message(self, topic, msg):
        self.__mqtt.publish(topic, msg)

    def set_on_message(self, f):
        self.__mqtt.set_callback(f)