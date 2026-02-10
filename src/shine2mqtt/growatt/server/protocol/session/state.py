from dataclasses import dataclass, field

from shine2mqtt.growatt.protocol.announce.announce import GrowattAnnounceMessage
from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.header.header import MBAPHeader


@dataclass
class ServerProtocolSessionState:
    protocol_id: int = 0
    unit_id: int = 0
    datalogger_serial: str = ""

    _announced: bool = False
    last_transaction_id: dict[FunctionCode, int] = field(
        default_factory=lambda: {
            FunctionCode.PING: 0,
            FunctionCode.ANNOUNCE: 0,
            FunctionCode.DATA: 0,
            FunctionCode.BUFFERED_DATA: 0,
            FunctionCode.SET_CONFIG: 0,
            FunctionCode.GET_CONFIG: 0,
        }
    )

    def is_announced(self) -> bool:
        return self._announced

    def announce(self, message: GrowattAnnounceMessage) -> None:
        self._announced = True
        self.protocol_id = message.header.protocol_id
        self.unit_id = message.header.unit_id
        self.datalogger_serial = message.datalogger_serial

    def get_next_transaction_id(self, function_code: FunctionCode) -> int:
        self.last_transaction_id[function_code] += 1
        return self.last_transaction_id[function_code]

    def set_incoming_transaction_id(self, header: MBAPHeader) -> None:
        self.last_transaction_id[header.function_code] = header.transaction_id
