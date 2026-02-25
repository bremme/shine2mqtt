#!/usr/bin/env python3
import json
import sys

from shine2mqtt.protocol.frame.header.header import MBAPHeader


def load_capture_file(file_path: str) -> tuple[list[bytes], list[MBAPHeader], list[bytes]]:
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    frames = [bytes.fromhex(f) for f in data["frames"]]
    headers = [MBAPHeader.fromdict(header) for header in data["headers"]]
    payloads = [bytes.fromhex(p) for p in data["payloads"]]

    return frames, headers, payloads


def display_capture(
    frames: list[bytes], headers: list[MBAPHeader], payloads: list[bytes], message_type: str
) -> None:
    for i, (frame, header, payload) in enumerate(zip(frames, headers, payloads, strict=True)):
        print(f"Frame {i}: {frame}\n")

        print(f"Header {i}: {header}\n")
        display_message_payload(payload, message_type)


def display_message_payload(payload: bytes, message_type: str) -> None:
    if message_type == "announce":
        print("Announce message: header\n")

        print(
            "{reg:3}\t{idx:3}\t{bytes:<12}\t{u16:>5}".format(
                reg="Reg", idx="Idx", bytes="Bytes", u16="U16"
            )
        )

        for register, index in enumerate(range(0, 71, 2)):
            u16 = int.from_bytes(payload[index : index + 2], byteorder="big")
            print(f"{register:3}\t{index:3}\t{str(payload[index : index + 2]):<12}\t{u16:>5}")
        print()

        print("Announce message: holding registers\n")
        print(
            "{reg:3}\t{idx:3}\t{bytes:<12}\t{u16:>5}".format(
                reg="Reg", idx="Idx", bytes="Bytes", u16="U16"
            )
        )
        for register, index in enumerate(range(71, len(payload), 2)):
            u16 = int.from_bytes(payload[index : index + 2], byteorder="big")
            print(f"{register:3}\t{index:3}\t{str(payload[index : index + 2]):<12}\t{u16:>5}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run analyze_captures.py <json_file>")
        sys.exit(1)

    message_type = sys.argv[1].split("/")[-1].split("_message.json")[0]
    print(message_type)

    frames, headers, payloads = load_capture_file(sys.argv[1])
    display_capture(frames, headers, payloads, message_type)


if __name__ == "__main__":
    main()
