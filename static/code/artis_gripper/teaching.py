from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TeachingSequence:
    name: str
    tool_type: str = "unknown"
    grasp_method: str = "tool_holding"
    metadata: Dict[str, Any] = field(default_factory=dict)
    steps: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": "ARTiS_teaching_sequence_v1",
            "name": self.name,
            "tool_type": self.tool_type,
            "grasp_method": self.grasp_method,
            "metadata": self.metadata,
            "steps": self.steps,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TeachingSequence":
        return cls(
            name=data.get("name", "unnamed_sequence"),
            tool_type=data.get("tool_type", "unknown"),
            grasp_method=data.get("grasp_method", "tool_holding"),
            metadata=data.get("metadata", {}),
            steps=data.get("steps", []),
        )

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "TeachingSequence":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


class TeachingRecorder:
    """Record manually positioned ARTiS states for later playback.

    Typical use:
      1. Disable torque for manual adjustment.
      2. Move the gripper by hand.
      3. Enable torque briefly and record current positions.
      4. Repeat for each task stage.
    """

    def __init__(self, gripper, sequence_name: str, tool_type: str = "unknown", grasp_method: str = "tool_holding"):
        self.gripper = gripper
        self.sequence = TeachingSequence(sequence_name, tool_type=tool_type, grasp_method=grasp_method)
        self._last_record_time = time.time()

    def record_step(self, name: str, duration_s: Optional[float] = None, description: str = "", extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        now = time.time()
        if duration_s is None:
            duration_s = max(0.1, now - self._last_record_time)
        self._last_record_time = now

        step = {
            "name": name,
            "time_s": now,
            "duration_s": float(duration_s),
            "joint_ticks": self.gripper.read_joint_ticks(),
            "joint_angles_deg": self.gripper.read_joint_angles(),
            "jamming": self.gripper.read_jamming_state(),
            "description": description,
        }
        if extra:
            step["extra"] = extra
        self.sequence.steps.append(step)
        return step

    def save(self, path: str | Path) -> None:
        self.sequence.save(path)


class TeachingPlayer:
    """Replay ARTiS teaching sequences saved by TeachingRecorder."""

    def __init__(self, gripper):
        self.gripper = gripper

    def replay_step(self, step: Dict[str, Any], speed_scale: float = 1.0, use_ticks: bool = True) -> None:
        duration_s = float(step.get("duration_s", 1.0)) / max(float(speed_scale), 1e-6)
        joint_ticks = step.get("joint_ticks", {})
        joint_angles = step.get("joint_angles_deg", {})

        if use_ticks and joint_ticks:
            self.gripper.move_to_ticks(joint_ticks)
        elif joint_angles:
            self.gripper.move_to_angles(joint_angles)

        if bool(step.get("jamming", False)):
            self.gripper.jam_on()
        else:
            self.gripper.jam_off()

        time.sleep(duration_s)

    def replay(self, sequence: TeachingSequence | str | Path, speed_scale: float = 1.0, use_ticks: bool = True) -> None:
        if not isinstance(sequence, TeachingSequence):
            sequence = TeachingSequence.load(sequence)
        for step in sequence.steps:
            self.replay_step(step, speed_scale=speed_scale, use_ticks=use_ticks)
