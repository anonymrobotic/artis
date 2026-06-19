from __future__ import annotations

import time
from typing import Optional

import serial


class ArduinoPalm:
    """Serial protocol for the ARTiS jamming-palm relay and optional teaching buttons."""

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.1, on_command: str = "1", off_command: str = "0"):
        self.port = port
        self.baudrate = int(baudrate)
        self.timeout = float(timeout)
        self.on_command = str(on_command)
        self.off_command = str(off_command)
        self.serial: Optional[serial.Serial] = None
        self._jammed = False

    def open(self) -> None:
        self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        time.sleep(2.0)

    def close(self) -> None:
        if self.serial is not None:
            self.serial.close()
            self.serial = None

    def _write(self, command: str) -> None:
        if self.serial is None:
            raise RuntimeError("Arduino serial port is not open")
        self.serial.write(str(command).encode("ascii"))
        self.serial.flush()

    def jam_on(self) -> None:
        self._write(self.on_command)
        self._jammed = True

    def jam_off(self) -> None:
        self._write(self.off_command)
        self._jammed = False

    def read_jamming_state(self) -> bool:
        return self._jammed

    def read_button_line(self) -> Optional[str]:
        if self.serial is None:
            return None
        if self.serial.in_waiting <= 0:
            return None
        line = self.serial.readline().decode("utf-8", errors="ignore").strip()
        return line or None
