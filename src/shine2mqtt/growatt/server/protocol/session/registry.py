from .session import ProtocolSession


class ProtocolSessionRegistry:
    def __init__(self):
        self.sessions = []

    def add(self, session: ProtocolSession):
        self.sessions.append(session)
