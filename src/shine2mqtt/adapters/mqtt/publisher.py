class MqttEventPublisher:
    def __init__(self, event_queue, config):
        self.event_queue = event_queue
        self.config = config
