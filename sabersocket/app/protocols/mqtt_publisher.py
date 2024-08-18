import paho.mqtt.client as mqtt

from sabersocket.app.logger import logger
from sabersocket.app.protocols.base import Publisher


class MQTTPublisher(Publisher):
    def __init__(self, host: str, port: int):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # type: ignore
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.host = host
        self.port = port

    def connect(self):
        self.client.connect(host=self.host, port=self.port, keepalive=60)
        self.client.loop_start()

    def publish(self, topic: str, payload: str):
        self.client.publish(topic, payload)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_disconnect(self, client, userdata, rc, *args, **kwargs):
        logger.info("Disconnected with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        pass

    def on_publish(self, client, userdata, mid, reason_code, properties):
        logger.info("<<< Message Published...")
