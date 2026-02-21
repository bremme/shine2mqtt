class DataloggerNotConnectedError(Exception):
    def __init__(self, datalogger_serial: str):
        super().__init__(f"Datalogger '{datalogger_serial}' is not connected")
        self.datalogger_serial = datalogger_serial
