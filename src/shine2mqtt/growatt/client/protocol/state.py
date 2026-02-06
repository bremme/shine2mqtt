from dataclasses import dataclass, field

from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.messages.ack import GrowattAckMessage
from shine2mqtt.growatt.protocol.messages.header import MBAPHeader


@dataclass
class ClientProtocolSessionState:
    protocol_id: int
    unit_id: int
    datalogger_serial: str
    announced: bool = False

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

    last_announce_time: float = 0.0
    last_data_time: float = 0.0
    last_ping_time: float = 0.0

    def is_announced(self) -> bool:
        return self.announced

    def announce(self, message: GrowattAckMessage) -> None:
        self.announced = message.ack

    def get_transaction_id(self, function_code: FunctionCode) -> int:
        """Get a new transaction ID for a given function code to use in outgoing messages."""
        self.last_transaction_id[function_code] += 1
        return self.last_transaction_id[function_code]

    def set_transaction_id(self, header: MBAPHeader) -> None:
        """Update the transaction ID for a given function code from incoming message."""
        self.last_transaction_id[header.function_code] = header.transaction_id
