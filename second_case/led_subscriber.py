import json
import logging
import time
from datetime import datetime

import paho.mqtt.client as mqtt

from common.config import QUEUE
from .raspberry_led import LedProcessor

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                    datefmt='%d/%m/%Y %H:%M ',
                    level=logging.INFO)

logger = logging.getLogger(__name__)




class Led_subscriber():
    """Class Led_subscriber: its instances can connect to the broker and subscriber to some topic"""

    msg_body = {}



    def __init__(self, clientID, broker="mqtt.eclipse.org", port=1883, topic="", qos=1):

        self.clientID_ = clientID
        self.broker_ = broker
        self.port_ = port
        self.mqtt_client = mqtt.Client(self.clientID_, clean_session=False)
        self.isSubscribe_ = False
        self.topic_ = topic
        self.qos_ = qos
        #self.queue_ = Queue()

        self.mqtt_client.on_connect = self.OnConnect
        self.mqtt_client.on_message = self.OnMessage
        self.mqtt_client.on_disconnect = self.OnDisconnect
        logger.info(f"User {self.clientID_} initialized.")



    def OnConnect(self, mqtt_client, userdata, flags, rc):
        """ myOnConnect function called by on_connect callback:

        Called upon connection to the broker. Everything goes well if rc == 0
        otherwise we have some connection issues with the broker. If so it is
        printed in the terminal and the notify() method of the notifier is
        called so that an appropriate action can be taken.

        Args:
            mqtt_client (:obj: MQTT.Client): client instance of the callback
            userdata (str): user data as set in Client (not used here)
            flags (int): flag to notify if the user's session is still
                available (not used here)
            rc (int): result code
        """
        errMsg = ""

        if rc == 0:
            logger.info(f"MQTT client {self.clientID_} successfully connected to the Broker {self.broker_}!")
            return str(rc)

        # If we go through this we had a problem with the connection phase
        elif 0 < rc <= 5:
            errMsg = "/!\ " + self.clientID_ + " connection to broker was " \
                                              "refused because of: "
            if rc == 1:
                errMsg.append("the use of an incorrect protocol version!")
            elif rc == 2:
                errMsg.append("the use of an invalid client identifier!")
            elif rc == 3:
                errMsg.append("the server is unavailable!")
            elif rc == 4:
                errMsg.append("the use of a bad username or password!")
            else:
                errMsg.append("it was not authorised!")
        else:
            errMsg = "/!\ " + self.clientID_ + " connection to broker was " \
                                              "refused for unknown reasons!"
        logger.error(errMsg)


    def subscribe(self):

        self.mqtt_client.subscribe(topic=self.topic_, qos=self.qos_)
        self.isSubscribe_ = True
        logger.info(f"Client {self.clientID_} subscribe to the topic: {self.topic_}")





    def OnMessage(self, client, userdata, msg):
        global msg_body
        get_time = datetime.now()
        current_time = get_time.strftime("%Y-%m-%d %H:%M:%S")
        print("--------------------------------------------------------------------")
        print("message received: ", str(msg.payload.decode("utf-8")))
        print("at time: " + str(current_time))
        print("--------------------------------------------------------------------")

        msg_body = dict(json.loads(msg.payload.decode("utf-8")))







    def OnDisconnect(self, mqtt_client, userdata, rc):
        """ myOnDisconnect function called by on_disconnect callback:

        Can be triggered in one of two cases:
        - in response to a disconnect(): normal case, it was asked
        - in response to an unexpected disconnection: in that case the client
        will try to reconnect

        In both cases we log it.

        Args:
            mqtt_client (:obj: MQTT.Client): client instance of the callback
            userdata (str): user data as set in Client (not used here)
            rc (int): result code
        """
        if rc == 0:
            logger.info(f"MQTT client {self.clientID_} successfully disconnected!")
        else:
            logger.warning(f"Unexpected disconnection of MQTT client {self.clientID_}. "\
                           "Reconnecting right away!")
            # The reconnection is performed automatically by our client since
            # we're using loop_start() so no need to manually tell our client
            # to reconnect.

    def start(self):

        self.mqtt_client.connect(host=self.broker_, port=self.port_)
        self.mqtt_client.loop_start()
        #logger.info(f"Client {self.clientID_} connected to the Broker {self.broker_}")

    def stop(self):

        if self.isSubscribe_:
            self.mqtt_client.unsubscribe(self.topic_)
            logger.info(f"MQTT client {self.clientID_} unsubscribed from topic {self.topic_}.")

        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        logger.info(f"Client {self.clientID_} disconnected from the Broker")


if __name__ == "__main__":

    mqtt_client = Led_subscriber(clientID="LED_1", topic="AulaMagna", qos=0)
    mqtt_client.subscribe()
    msg_body = {'Time': None, 'Payload': None}
    ledProcessor = LedProcessor()
    while True:
        #time.sleep(.3)
        if msg_body['Payload'] is not None:
            msg = msg_body['Payload']
            logger.info(f'put msg: {msg} to the QUEUE')
            QUEUE.put(msg_body['Payload'])
            #time.sleep(.3)
            if msg == 'STOP':
                logger.info('STOP in led_subscriber.')
                QUEUE.put(msg)
                time.sleep(.5)
                break
        else:
            logger.info('Waiting in led_subscriber')
            time.sleep(1)
    logger.info('led_subscriber stops ledProcessor and unsubscribe itself')
    ledProcessor.stop_event()
    mqtt_client.stop()

"""TO DO: al momento riesco a caricare la queue con i msg ricevuti dal broker. Devo aggiungere la parte
che carica i dati sul database."""


















