from dataclasses import dataclass, field

from shine2mqtt.growatt.protocol.ack.ack import GrowattAckMessage
from shine2mqtt.growatt.protocol.constants import FunctionCode
from shine2mqtt.growatt.protocol.header.header import MBAPHeader


@dataclass
class ClientProtocolSessionState:
    protocol_id: int
    unit_id: int
    datalogger_serial: str

    _announced: bool = False
    _transaction_id: dict[FunctionCode, int] = field(
        default_factory=lambda: {
            FunctionCode.PING: 0,
            FunctionCode.ANNOUNCE: 0,
            FunctionCode.DATA: 0,
            FunctionCode.BUFFERED_DATA: 0,
            FunctionCode.SET_CONFIG: 0,
            FunctionCode.GET_CONFIG: 0,
        }
    )
    _last_send_time: dict[FunctionCode, float | None] = field(
        default_factory=lambda: {
            FunctionCode.PING: None,
            FunctionCode.ANNOUNCE: None,
            FunctionCode.DATA: None,
            FunctionCode.BUFFERED_DATA: None,
            FunctionCode.SET_CONFIG: None,
            FunctionCode.GET_CONFIG: None,
        }
    )

    def get_last_send(self, function_code: FunctionCode) -> float | None:
        return self._last_send_time[function_code]

    def update_last_send(self, function_code: FunctionCode, timestamp: float) -> None:
        self._last_send_time[function_code] = timestamp

    def is_announced(self) -> bool:
        return self._announced

    def announce(self, message: GrowattAckMessage) -> None:
        self._announced = message.ack

    def get_next_transaction_id(self, function_code: FunctionCode) -> int:
        """Get a new transaction ID for a given function code to use in outgoing messages."""
        self._transaction_id[function_code] += 1
        return self._transaction_id[function_code]

    def set_incoming_transaction_id(self, header: MBAPHeader) -> None:
        """Update the transaction ID for a given function code from incoming message."""
        self._transaction_id[header.function_code] = header.transaction_id
