from shine2mqtt.domain.interfaces.registry import SessionRegistry


class ReadRegisterHandler:
    def __init__(self, session_registry: SessionRegistry):
        self.session_registry = session_registry
