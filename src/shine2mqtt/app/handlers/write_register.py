from shine2mqtt.domain.interfaces.registry import SessionRegistry


class WriteRegisterHandler:
    def __init__(self, session_registry: SessionRegistry):
        self.session_registry = session_registry
