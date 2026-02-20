from shine2mqtt.adapters.mqtt.publisher import MqttEventPublisher
from shine2mqtt.adapters.mqtt.subscriber import MqttCommandSubscriber


class MqttBridge2:
    def __init__(self, publisher: MqttEventPublisher, subscriber: MqttCommandSubscriber, config):
        self.publisher = publisher
        self.subscriber = subscriber
        self.config = config
