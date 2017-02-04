import time

class Clock:
    def __init__(self):
        self.tick()

    def tick(self):
        self.last_tick = time.time()

    @property
    def elapsed(self):
        return time.time() - self.last_tick

    def passed(self, seconds):
        return self.elapsed >= seconds
