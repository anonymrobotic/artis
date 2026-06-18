from __future__ import annotations

import time
from typing import Optional

import serial


class ArduinoPalm:
    """Serial interface for the ARTiS jamming palm relay.

    Protocol expected by arduino/Arduino_communication.ino:
      '1' -> jamming ON / vacuum relay energized
      '0' -> jamming OFF / relay released
      '?' -> report state
    """

    def __init__(self, port: Optional[str], baudrate: int = 9600, timeout_s: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout_s = timeout_s
        self.serial: Optional[serial.Serial] = None

    def open(self) -> None:
        if not self.port:
            return
        self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout_s)
        time.sleep(2.0)

    def close(self) -> None:
        if self.serial:
            self.serial.close()
            self.serial = None

    def __enter__(self) -> "ArduinoPalm":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def set_jamming(self, enabled: bool) -> None:
        if self.serial is None:
            raise RuntimeError("Arduino palm serial port is not open. Set arduino_port in the config.")
        self.serial.write(b"1" if enabled else b"0")
        self.serial.flush()

    def jam_on(self) -> None:
        self.set_jamming(True)

    def jam_off(self) -> None:
        self.set_jamming(False)
