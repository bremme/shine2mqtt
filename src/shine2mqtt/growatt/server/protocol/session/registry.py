from .session import ServerProtocolSession


class ProtocolSessionRegistry:
    def __init__(self):
        self.sessions = []

    def add(self, session: ServerProtocolSession):
        self.sessions.append(session)
