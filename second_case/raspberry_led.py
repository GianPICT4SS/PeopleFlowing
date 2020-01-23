"""usage pin: GPIO4-GPIO22-GPIO9-GPIO6"""

import time
from threading import Thread, Event

import RPi.GPIO as gpio

from common.config import QUEUE
from common.bot import bot


class LedProcessor(Thread):

    def __init__(self):
        super(LedProcessor, self).__init__()
        self.stop_event_ = Event()
        self.start()


    def run(self):


        while not self.stop_event_.is_set():
            if QUEUE.empty():
               print('WAITING in Processor')
               time.sleep(1)
            else:
                msg = QUEUE.get()
                if msg == 'RED':
                    print(f'IN LED: {msg}')
                    new_msg = QUEUE.get()
                    while new_msg == "RED":
                        gpio.setmode(gpio.BCM)
                        gpio.setup(4, gpio.OUT)
                        print(f"LED {new_msg} ON")
                        #time.sleep(2)
                        gpio.output(4, True)
                        #time.sleep(.5)
                        new_msg = QUEUE.get()
                        try:
                            bot('Level', 'AulaMagna', 'RED')
                        except:
                            pass
                    gpio.output(4, False)
                elif msg == 'YELLOW':
                    print(f'IN LED: {msg}')
                    new_msg = QUEUE.get()
                    while new_msg == "YELLOW":
                        gpio.setmode(gpio.BCM)
                        gpio.setup(22, gpio.OUT)
                        print(f"LED {new_msg} ON")
                        # time.sleep(2)
                        gpio.output(22, True)
                        # time.sleep(.5)
                        new_msg = QUEUE.get()
                        try:
                            bot('Level', 'AulaMagna', 'YELLOW')
                        except:
                            pass
                    gpio.output(22, False)
                elif msg == 'BLUE':
                    print(f'IN LED: {msg}')
                    new_msg = QUEUE.get()
                    while new_msg == "BLUE":
                        gpio.setmode(gpio.BCM)
                        gpio.setup(9, gpio.OUT)
                        print(f"LED {new_msg} ON")
                        # time.sleep(2)
                        gpio.output(9, True)
                        # time.sleep(.5)
                        new_msg = QUEUE.get()
                        try:
                            bot('Level', 'AulaMagna', 'BLUE')
                        except:
                            pass
                    gpio.output(9, False)
                elif msg == 'GREEN':
                    print(f'IN LED: {msg}')
                    new_msg = QUEUE.get()
                    while new_msg == "GREEN":
                        gpio.setmode(gpio.BCM)
                        gpio.setup(6, gpio.OUT)
                        print(f"LED {new_msg} ON")
                        # time.sleep(2)
                        gpio.output(6, True)
                        # time.sleep(.5)
                        new_msg = QUEUE.get()
                        try:
                            bot('Level', 'AulaMagna', 'GREEN')
                        except:
                            pass
                    gpio.output(6, False)

        print('STOP in processor.')






    def stop_event(self):
        self.stop_event_.set()
        pass




