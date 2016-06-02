import time


class DelayTime(object):
    default_delay_count = 1
    default_delay_time = 45

    def __init__(self, delay_time=None):
        self.delay_time = self.default_delay_time if delay_time is None else delay_time

    def delay(self):
        time.sleep(self.delay_time + self.default_delay_count)
        self.__class__.default_delay_count += 1


storage_word = []



