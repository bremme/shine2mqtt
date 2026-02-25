import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from shine2mqtt.protocol.frame.header.header import FunctionCode, MBAPHeader
from shine2mqtt.util.logger import logger


@dataclass
class CapturedFrame:
    frame: bytes
    header: MBAPHeader
    payload: bytes


class FrameCapturer(ABC):
    @abstractmethod
    def capture(self, frame: CapturedFrame) -> None:
        pass


class FileFrameCapturer(FrameCapturer):
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, frame: CapturedFrame) -> None:
        filename = self._get_filename(frame)
        filepath = self.output_dir / filename

        data = {"frames": [], "headers": [], "payloads": []}

        if filepath.exists():
            with open(filepath) as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    logger.warning(
                        f"Failed to decode existing capture file {filepath}, starting with empty data"
                    )

        data["frames"].append(frame.frame.hex())
        data["headers"].append(frame.header.asdict())
        data["payloads"].append(frame.payload.hex())

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def _get_filename(self, frame: CapturedFrame) -> str:
        function_code = frame.header.function_code
        function_name = frame.header.function_code.name.lower()

        match function_code:
            case (
                FunctionCode.ANNOUNCE
                | FunctionCode.DATA
                | FunctionCode.BUFFERED_DATA
                | FunctionCode.PING
            ):
                return f"{function_name}_message.json"
            case (
                FunctionCode.SET_CONFIG
                | FunctionCode.GET_CONFIG
                | FunctionCode.READ_MULTIPLE_HOLDING_REGISTERS
                | FunctionCode.WRITE_SINGLE_HOLDING_REGISTER
                | FunctionCode.WRITE_MULTIPLE_HOLDING_REGISTERS
            ):
                return f"{function_name}_response.json"
            case _:
                return f"function_{function_code.value:02x}_message.json"
