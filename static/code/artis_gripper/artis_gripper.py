from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional

from .arduino_palm import ArduinoPalm
from .config import ArtisConfig, load_config
from .dynamixel_bus import DynamixelBus


class ArtisGripper:
    """High-level Python API for the ARTiS gripper.

    Joint naming convention:
      j0_base: symmetric base rotation about the gripper axis
      j1_center_axis, j2_left_axis, j3_right_axis: finger-axis orientation joints
      j4_center_4bar, j5_left_4bar, j6_right_4bar: four-bar closing joints
    """

    def __init__(self, config: str | Path | ArtisConfig):
        self.config = load_config(config) if not isinstance(config, ArtisConfig) else config
        self.bus = DynamixelBus(
            self.config.serial.dynamixel_port,
            self.config.serial.dynamixel_baudrate,
            self.config.serial.dynamixel_protocol,
        )
        self.palm = ArduinoPalm(
            self.config.serial.arduino_port,
            self.config.serial.arduino_baudrate,
            self.config.serial.arduino_timeout_s,
        )

    @property
    def dxl_ids(self) -> list[int]:
        return [m.dxl_id for m in self.config.motors.values()]

    def connect(self, enable_torque: bool = True) -> None:
        self.bus.open()
        self.palm.open()
        if enable_torque:
            self.enable_torque(True)

    def close(self, disable_torque: bool = True) -> None:
        try:
            if disable_torque:
                self.enable_torque(False)
        finally:
            self.palm.close()
            self.bus.close()

    def __enter__(self) -> "ArtisGripper":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def enable_torque(self, enabled: bool = True) -> None:
        self.bus.enable_torque(self.dxl_ids, enabled)

    def move_joint_ticks(self, joint_name: str, tick: int, speed: Optional[int] = None) -> None:
        m = self.config.motors[joint_name]
        self.bus.set_goal_position(m.dxl_id, m.clamp(tick), speed if speed is not None else m.default_speed)

    def move_ticks(self, positions: Dict[str, int], speeds: Optional[Dict[str, int]] = None) -> None:
        for joint_name, tick in positions.items():
            speed = speeds.get(joint_name) if speeds else None
            self.move_joint_ticks(joint_name, tick, speed)

    def read_joint_ticks(self, joint_names: Optional[Iterable[str]] = None) -> Dict[str, int]:
        names = list(joint_names) if joint_names is not None else list(self.config.motors.keys())
        return {name: self.bus.read_position(self.config.motors[name].dxl_id) for name in names}

    def apply_preset(self, name: str) -> None:
        if name not in self.config.presets:
            raise KeyError(f"Unknown preset '{name}'. Available presets: {list(self.config.presets)}")
        preset = self.config.presets[name]
        positions = {joint: int(v["tick"]) for joint, v in preset.items()}
        speeds = {joint: int(v.get("speed", self.config.motors[joint].default_speed)) for joint, v in preset.items()}
        self.move_ticks(positions, speeds)

    def jam_on(self) -> None:
        self.palm.jam_on()

    def jam_off(self) -> None:
        self.palm.jam_off()

    def set_jamming(self, enabled: bool) -> None:
        self.palm.set_jamming(enabled)
