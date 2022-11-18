import json
import time
import machine
import utime
from led import Led

class ErrorLogger:
    def __init__(self):
        # read json file
        with open('./config.json', 'r') as f:
            self.__data = json.loads(f.read())

        self.__log_limit = self.__data['error']['log_limit']
        self.__error_retry = self.__data['error']['error_retry']
        self.__retry_time_limit = self.__data['error']['retry_limit']

        self.error = self.__read_error()

    def __read_error(self) -> list:
        try:
            with open('./error.json', "r") as f:
                return json.load(f)
        except OSError: 
           return []

    def __write_error(self):
        with open('./error.json', 'w') as f:
            json.dump(self.error, f)

    def __retry_time(self, times):
        return min(self.__error_retry * times, self.__retry_time_limit)

    def retry(self, times):
        led = Led()
        reset_time = self.__retry_time(times)
        for _ in range(5):
            led.turn_off()
            utime.sleep_ms(200)
            led.turn_on()
            utime.sleep_ms(200)
        print(f'Resetting in {reset_time} seconds')
        time.sleep(reset_time)
        machine.reset()

    def read_error(self):
        return self.error

    def clear_error(self):
        self.error.clear()
        self.__write_error()

    def add_error(self, message):
        error_count = 0
        if len(self.error) == 0 or self.error[-1]['message'] != message:
            self.error.append({'message': message, 'count': 1})
            error_count = 1
        else:
            self.error[-1]['count'] += 1
            error_count = self.error[-1]['count']
        if len(self.error) > self.__log_limit:
            for _ in range(len(self.error), self.__log_limit, -1):
                self.error.remove(self.error[0])
        
        self.__write_error()
        return error_count
