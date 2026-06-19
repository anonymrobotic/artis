from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Mapping, Optional

import yaml

from .arduino_palm import ArduinoPalm
from .dynamixel_bus import DynamixelBus


class ArtisGripper:
    """High-level hardware abstraction for ARTiS.

    Joint names used by the API:
        J0: base rotation about gripper axis
        J1: center finger-axis orientation
        J2: left finger-axis orientation
        J3: right finger-axis orientation
        J4: center four-bar mechanism
        J5: left four-bar mechanism
        J6: right four-bar mechanism
    """

    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        serial_cfg = self.config.get("serial", {})
        self.bus = DynamixelBus(
            port=serial_cfg.get("dynamixel_port", "/dev/ttyUSB0"),
            baudrate=serial_cfg.get("dynamixel_baudrate", 57600),
            protocol_version=serial_cfg.get("protocol_version", 1.0),
        )
        palm_cfg = self.config.get("palm", {})
        self.palm = ArduinoPalm(
            port=serial_cfg.get("arduino_port", "/dev/ttyACM0"),
            baudrate=serial_cfg.get("arduino_baudrate", 9600),
            on_command=palm_cfg.get("on_command", "1"),
            off_command=palm_cfg.get("off_command", "0"),
        )
        self.joint_ids: Dict[str, int] = {k: int(v["id"]) for k, v in self.config["joints"].items()}
        self.default_speed = int(self.config.get("default_speed", 70))
        self.presets = self.config.get("presets", {})
        self.connected = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.shutdown()

    def connect(self, enable_torque: bool = True) -> None:
        self.bus.open()
        self.palm.open()
        self.connected = True
        if enable_torque:
            self.enable_torque(True)

    def shutdown(self, disable_torque: bool = True, jam_off: bool = True) -> None:
        if jam_off:
            try:
                self.jam_off()
            except Exception:
                pass
        if disable_torque:
            try:
                self.enable_torque(False)
            except Exception:
                pass
        self.palm.close()
        self.bus.close()
        self.connected = False

    def enable_torque(self, enabled: bool = True, joints: Optional[list[str]] = None) -> None:
        ids = [self.joint_ids[j] for j in joints] if joints else list(self.joint_ids.values())
        self.bus.enable_torque(ids, enabled)

    def read_joint_ticks(self) -> Dict[str, int]:
        return self.bus.read_positions(self.joint_ids)

    def read_joint_angles(self) -> Dict[str, float]:
        ticks = self.read_joint_ticks()
        return {joint: self.ticks_to_deg(joint, pos) for joint, pos in ticks.items()}

    def read_jamming_state(self) -> bool:
        return self.palm.read_jamming_state()

    def jam_on(self) -> None:
        self.palm.jam_on()

    def jam_off(self) -> None:
        self.palm.jam_off()

    def ticks_to_deg(self, joint: str, ticks: int) -> float:
        cfg = self.config["joints"][joint]
        center = float(cfg.get("center_ticks", 2048))
        scale = float(cfg.get("ticks_per_degree", 4096.0 / 360.0))
        sign = float(cfg.get("direction", 1.0))
        return sign * (float(ticks) - center) / scale

    def deg_to_ticks(self, joint: str, deg: float) -> int:
        cfg = self.config["joints"][joint]
        center = float(cfg.get("center_ticks", 2048))
        scale = float(cfg.get("ticks_per_degree", 4096.0 / 360.0))
        sign = float(cfg.get("direction", 1.0))
        ticks = int(round(center + sign * float(deg) * scale))
        min_ticks = int(cfg.get("min_ticks", 0))
        max_ticks = int(cfg.get("max_ticks", 4095))
        return max(min_ticks, min(max_ticks, ticks))

    def set_joint_ticks(self, joint: str, ticks: int, speed: Optional[int] = None) -> None:
        self.bus.set_goal_position(self.joint_ids[joint], ticks, speed if speed is not None else self.default_speed)

    def set_joint_angle(self, joint: str, deg: float, speed: Optional[int] = None) -> None:
        self.set_joint_ticks(joint, self.deg_to_ticks(joint, deg), speed=speed)

    def move_to_ticks(self, targets: Mapping[str, int], speeds: Optional[Mapping[str, int]] = None) -> None:
        for joint, ticks in targets.items():
            speed = speeds.get(joint, self.default_speed) if speeds else self.default_speed
            self.set_joint_ticks(joint, ticks, speed=speed)

    def move_to_angles(self, targets: Mapping[str, float], speeds: Optional[Mapping[str, int]] = None) -> None:
        for joint, deg in targets.items():
            speed = speeds.get(joint, self.default_speed) if speeds else self.default_speed
            self.set_joint_angle(joint, deg, speed=speed)

    def apply_preset(self, preset_name: str) -> None:
        if preset_name not in self.presets:
            raise KeyError(f"Unknown preset '{preset_name}'. Available: {list(self.presets)}")
        preset = self.presets[preset_name]
        targets = preset.get("ticks", preset)
        speeds = preset.get("speeds", None)
        self.move_to_ticks(targets, speeds=speeds)
        if "jamming" in preset:
            self.jam_on() if bool(preset["jamming"]) else self.jam_off()

    def open_fourbar_fingers(self) -> None:
        if "open_fourbar" in self.presets:
            self.apply_preset("open_fourbar")

    def clear_palm_workspace(self) -> None:
        if "clear_palm_workspace" in self.presets:
            self.apply_preset("clear_palm_workspace")

    def read_button_line(self):
        return self.palm.read_button_line()

    def wait(self, seconds: float) -> None:
        time.sleep(float(seconds))
