from shine2mqtt.app.handlers.write_register import WriteRegisterHandler


class MqttCommandSubscriber:
    def __init__(self, write_handler: WriteRegisterHandler):
        self.write_handler = write_handler

    async def on_message(self, topic: str, payload: str) -> None:
        pass
