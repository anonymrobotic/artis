from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .teaching import TeachingPlayer, TeachingSequence


@dataclass
class AutonomousResult:
    success: bool
    message: str


class ArtisAutonomousToolController:
    """Finite-state controller skeleton for autonomous ARTiS tool acquisition, use, and release.

    The robot, vision, and force-torque objects are intentionally interface-like. This lets the API be integrated
    with ROS 2, MoveIt, custom robot drivers, RGB-D pipelines, or imitation-learning stacks.
    """

    def __init__(self, gripper, robot=None, vision=None, ft_sensor=None):
        self.gripper = gripper
        self.robot = robot
        self.vision = vision
        self.ft_sensor = ft_sensor
        self.player = TeachingPlayer(gripper)

    def execute_taught_tool_grasp(self, sequence_path: str, release_area=None) -> AutonomousResult:
        seq = TeachingSequence.load(sequence_path)

        tool = self.vision.detect_tool() if self.vision else None
        if self.vision and tool is None:
            return AutonomousResult(False, "No tool detected")

        self.gripper.jam_off()
        self.gripper.clear_palm_workspace()
        self.gripper.open_fourbar_fingers()

        if self.robot and self.vision:
            tool_pose = self.vision.estimate_tool_pose(tool)
            approach_pose = self.robot.plan_palm_approach_pose(tool_pose)
            self.robot.move_to_pose(approach_pose)
            self._press_tool_into_palm_with_ft()

        # Replay demonstrated gripper part after palm positioning.
        self.player.replay(seq)

        if self.robot:
            self.robot.lift_small()
        if self.vision and self.vision.detect_tool_slip(tool):
            return AutonomousResult(False, "Tool slipped after taught sequence playback")

        return AutonomousResult(True, "Taught ARTiS tool sequence completed")

    def _press_tool_into_palm_with_ft(self) -> None:
        if not self.robot or not self.ft_sensor:
            return
        desired_fz = 8.0
        max_fz = 20.0
        for _ in range(200):
            wrench = self.ft_sensor.read_wrench()
            fz = abs(wrench[2])
            if fz >= desired_fz:
                break
            if fz > max_fz:
                raise RuntimeError("Excessive force during palm contact")
            self.robot.move_incremental(z=-0.0005)
