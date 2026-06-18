from __future__ import annotations

from typing import Iterable, Optional

from dynamixel_sdk import PacketHandler, PortHandler

# MX-series, Protocol 1.0 control table addresses
ADDR_TORQUE_ENABLE = 24
ADDR_GOAL_POSITION = 30
ADDR_MOVING_SPEED = 32
ADDR_PRESENT_POSITION = 36

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0


class DynamixelBus:
    def __init__(self, port: str, baudrate: int = 57600, protocol: float = 1.0):
        self.port_name = port
        self.baudrate = baudrate
        self.protocol = protocol
        self.port = PortHandler(port)
        self.packet = PacketHandler(protocol)
        self.is_open = False

    def open(self) -> None:
        if not self.port.openPort():
            raise RuntimeError(f"Failed to open Dynamixel port: {self.port_name}")
        if not self.port.setBaudRate(self.baudrate):
            raise RuntimeError(f"Failed to set Dynamixel baudrate: {self.baudrate}")
        self.is_open = True

    def close(self) -> None:
        if self.is_open:
            self.port.closePort()
            self.is_open = False

    def __enter__(self) -> "DynamixelBus":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _check(self, dxl_id: int, result: int, error: int, action: str) -> None:
        if result != 0:
            raise RuntimeError(f"Dynamixel {dxl_id}: {action} failed: {self.packet.getTxRxResult(result)}")
        if error != 0:
            raise RuntimeError(f"Dynamixel {dxl_id}: {action} error: {self.packet.getRxPacketError(error)}")

    def enable_torque(self, dxl_ids: Iterable[int], enabled: bool = True) -> None:
        value = TORQUE_ENABLE if enabled else TORQUE_DISABLE
        for dxl_id in dxl_ids:
            result, error = self.packet.write1ByteTxRx(self.port, dxl_id, ADDR_TORQUE_ENABLE, value)
            self._check(dxl_id, result, error, "enable_torque" if enabled else "disable_torque")

    def set_speed(self, dxl_id: int, speed: int) -> None:
        result, error = self.packet.write2ByteTxRx(self.port, dxl_id, ADDR_MOVING_SPEED, int(speed))
        self._check(dxl_id, result, error, "set_speed")

    def set_goal_position(self, dxl_id: int, tick: int, speed: Optional[int] = None) -> None:
        if speed is not None:
            self.set_speed(dxl_id, speed)
        result, error = self.packet.write2ByteTxRx(self.port, dxl_id, ADDR_GOAL_POSITION, int(tick))
        self._check(dxl_id, result, error, "set_goal_position")

    def read_position(self, dxl_id: int) -> int:
        value, result, error = self.packet.read2ByteTxRx(self.port, dxl_id, ADDR_PRESENT_POSITION)
        self._check(dxl_id, result, error, "read_position")
        return int(value)
