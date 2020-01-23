import time
import json
from datetime import datetime
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                    datefmt='%d/%m/%Y %H:%M ',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

from threading import Thread, Event

from common.publisher import Publisher_people
from common.config import QUEUE
from common.bot import bot

pub = Publisher_people(clientID='pub_vid', topic='AulaMagna')

dict_ = {'Time': None, 'Payload': ''}

class Flowing_pub(Thread):

    def __init__(self):
        super(Flowing_pub, self).__init__()
        self.stop_event_ = Event()
        self.start()

    def run(self):
        while not self.stop_event_.is_set():
            if QUEUE.empty():
                logger.info('Waiting in Thread')
                time.sleep(0.1)
            else:
                msg = QUEUE.get()
                if msg == 'GREEN':
                    logger.info('Payload: GREEN, published')
                    end = datetime.now().strftime('%Y/%m/%d | %H:%M:%S')
                    dict_['Time'] = end
                    dict_['Payload'] = 'GREEN'
                    payload = json.dumps(dict_)
                    time.sleep(1)
                    pub.publish(msg=payload)
                    logger.info('Payload: GREEN, published')
                    try:
                        bot('Level', 'AulaMagna', 'GREEN')
                    except:
                        pass
                elif msg == 'YELLOW':
                    end = datetime.now().strftime('%Y/%m/%d | %H:%M:%S')
                    dict_['Time'] = end
                    dict_['Payload'] = 'YELLOW'
                    payload = json.dumps(dict_)
                    time.sleep(1)
                    pub.publish(msg=payload)
                    logger.info('Payload: YELLOW, published')
                    try:
                        bot('Level', 'AulaMagna', 'YELLOW')
                    except:
                        pass
                elif msg == 'RED':
                    end = datetime.now().strftime('%Y/%m/%d | %H:%M:%S')
                    dict_['Time'] = end
                    dict_['Payload'] = 'RED'
                    payload = json.dumps(dict_)
                    time.sleep(1)
                    pub.publish(msg=payload)
                    logger.info('Payload: RED, published')
                    try:
                        bot('Level', 'AulaMagna', 'RED')
                    except:
                        pass

    def stop_event(self):
        self.stop_event_.set()
        pass
