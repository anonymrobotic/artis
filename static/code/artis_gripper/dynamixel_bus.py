from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

from dynamixel_sdk import PacketHandler, PortHandler


@dataclass(frozen=True)
class MXProtocol1:
    torque_enable: int = 24
    goal_position: int = 30
    moving_speed: int = 32
    torque_limit: int = 34
    present_position: int = 36
    present_speed: int = 38
    present_load: int = 40
    present_voltage: int = 42
    present_temperature: int = 43


class DynamixelBus:
    """Small wrapper for MX-series Dynamixel servos using Protocol 1.0."""

    def __init__(self, port: str, baudrate: int = 57600, protocol_version: float = 1.0):
        self.port_name = port
        self.baudrate = int(baudrate)
        self.protocol_version = float(protocol_version)
        self.addr = MXProtocol1()
        self.port_handler = PortHandler(self.port_name)
        self.packet_handler = PacketHandler(self.protocol_version)
        self.is_open = False

    def open(self) -> None:
        if not self.port_handler.openPort():
            raise RuntimeError(f"Failed to open Dynamixel port: {self.port_name}")
        if not self.port_handler.setBaudRate(self.baudrate):
            self.port_handler.closePort()
            raise RuntimeError(f"Failed to set Dynamixel baudrate: {self.baudrate}")
        self.is_open = True

    def close(self) -> None:
        if self.is_open:
            self.port_handler.closePort()
            self.is_open = False

    def _check(self, dxl_id: int, comm_result: int, error: int, operation: str) -> None:
        if comm_result != 0:
            msg = self.packet_handler.getTxRxResult(comm_result)
            raise RuntimeError(f"Dynamixel {dxl_id}: {operation} communication failed: {msg}")
        if error != 0:
            msg = self.packet_handler.getRxPacketError(error)
            raise RuntimeError(f"Dynamixel {dxl_id}: {operation} packet error: {msg}")

    def write1(self, dxl_id: int, address: int, value: int) -> None:
        comm, err = self.packet_handler.write1ByteTxRx(self.port_handler, int(dxl_id), int(address), int(value))
        self._check(dxl_id, comm, err, f"write1 address {address}")

    def write2(self, dxl_id: int, address: int, value: int) -> None:
        comm, err = self.packet_handler.write2ByteTxRx(self.port_handler, int(dxl_id), int(address), int(value))
        self._check(dxl_id, comm, err, f"write2 address {address}")

    def read1(self, dxl_id: int, address: int) -> int:
        value, comm, err = self.packet_handler.read1ByteTxRx(self.port_handler, int(dxl_id), int(address))
        self._check(dxl_id, comm, err, f"read1 address {address}")
        return int(value)

    def read2(self, dxl_id: int, address: int) -> int:
        value, comm, err = self.packet_handler.read2ByteTxRx(self.port_handler, int(dxl_id), int(address))
        self._check(dxl_id, comm, err, f"read2 address {address}")
        return int(value)

    def enable_torque(self, dxl_ids: Iterable[int], enabled: bool = True) -> None:
        value = 1 if enabled else 0
        for dxl_id in dxl_ids:
            self.write1(dxl_id, self.addr.torque_enable, value)

    def set_torque_limit(self, dxl_id: int, limit: int) -> None:
        self.write2(dxl_id, self.addr.torque_limit, max(0, min(1023, int(limit))))

    def set_speed(self, dxl_id: int, speed: int) -> None:
        self.write2(dxl_id, self.addr.moving_speed, max(0, min(1023, int(speed))))

    def set_goal_position(self, dxl_id: int, ticks: int, speed: Optional[int] = None) -> None:
        if speed is not None:
            self.set_speed(dxl_id, speed)
        self.write2(dxl_id, self.addr.goal_position, max(0, min(4095, int(ticks))))

    def read_position(self, dxl_id: int) -> int:
        return self.read2(dxl_id, self.addr.present_position)

    def read_positions(self, ids_by_joint: Dict[str, int]) -> Dict[str, int]:
        return {joint: self.read_position(dxl_id) for joint, dxl_id in ids_by_joint.items()}
