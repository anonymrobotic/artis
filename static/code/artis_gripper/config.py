from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml


@dataclass(frozen=True)
class MotorConfig:
    name: str
    dxl_id: int
    min_tick: int = 0
    max_tick: int = 4095
    zero_tick: int = 2048
    direction: int = 1
    default_speed: int = 80

    def clamp(self, tick: int) -> int:
        return max(self.min_tick, min(self.max_tick, int(tick)))


@dataclass(frozen=True)
class SerialConfig:
    dynamixel_port: str
    dynamixel_baudrate: int = 57600
    dynamixel_protocol: float = 1.0
    arduino_port: Optional[str] = None
    arduino_baudrate: int = 9600
    arduino_timeout_s: float = 1.0


@dataclass(frozen=True)
class ArtisConfig:
    serial: SerialConfig
    motors: Dict[str, MotorConfig]
    presets: Dict[str, Dict[str, Dict[str, int]]]


def load_config(path: str | Path) -> ArtisConfig:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    serial_raw = raw.get("serial", {})
    serial = SerialConfig(
        dynamixel_port=serial_raw.get("dynamixel_port", "/dev/ttyUSB1"),
        dynamixel_baudrate=int(serial_raw.get("dynamixel_baudrate", 57600)),
        dynamixel_protocol=float(serial_raw.get("dynamixel_protocol", 1.0)),
        arduino_port=serial_raw.get("arduino_port"),
        arduino_baudrate=int(serial_raw.get("arduino_baudrate", 9600)),
        arduino_timeout_s=float(serial_raw.get("arduino_timeout_s", 1.0)),
    )

    motors = {}
    for name, m in raw.get("motors", {}).items():
        motors[name] = MotorConfig(
            name=name,
            dxl_id=int(m["id"]),
            min_tick=int(m.get("min_tick", 0)),
            max_tick=int(m.get("max_tick", 4095)),
            zero_tick=int(m.get("zero_tick", 2048)),
            direction=int(m.get("direction", 1)),
            default_speed=int(m.get("default_speed", 80)),
        )

    return ArtisConfig(serial=serial, motors=motors, presets=raw.get("presets", {}))
