from dataclasses import dataclass, field

from shine2mqtt.domain.models.datalogger import DataLogger
from shine2mqtt.domain.models.inverter import Inverter
from shine2mqtt.protocol.frame.header.header import FunctionCode, MBAPHeader


@dataclass
class TransactionIdTracker:
    last_transaction_id: dict[FunctionCode, int] = field(
        default_factory=lambda: dict.fromkeys(FunctionCode, 0)
    )

    def get_next_transaction_id(self, function_code: FunctionCode) -> int:
        self.last_transaction_id[function_code] += 1
        return self.last_transaction_id[function_code]

    def set_incoming_transaction_id(self, header: MBAPHeader) -> None:
        self.last_transaction_id[header.function_code] = header.transaction_id


@dataclass
class ServerProtocolSessionState:
    protocol_id: int
    unit_id: int
    datalogger: DataLogger
    inverter: Inverter
    transaction_id_tracker: TransactionIdTracker

    def get_next_transaction_id(self, function_code: FunctionCode) -> int:
        return self.transaction_id_tracker.get_next_transaction_id(function_code)

    def set_incoming_transaction_id(self, header: MBAPHeader) -> None:
        self.transaction_id_tracker.set_incoming_transaction_id(header)

    # _announced: bool = False

    # last_transaction_id: dict[FunctionCode, int] = field(
    #     default_factory=lambda: dict.fromkeys(FunctionCode, 0)
    # )

    # def is_announced(self) -> bool:
    #     return self._announced

    # def announce(self, message: GrowattAnnounceMessage) -> None:
    #     self._announced = True
    #     self.protocol_id = message.header.protocol_id
    #     self.unit_id = message.header.unit_id
    #     self.datalogger_serial = message.datalogger_serial

    # def get_next_transaction_id(self, function_code: FunctionCode) -> int:
    #     self.last_transaction_id[function_code] += 1
    #     return self.last_transaction_id[function_code]

    # def set_incoming_transaction_id(self, header: MBAPHeader) -> None:
    #     self.last_transaction_id[header.function_code] = header.transaction_id
