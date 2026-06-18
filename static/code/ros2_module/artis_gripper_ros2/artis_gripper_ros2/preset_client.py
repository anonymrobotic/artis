from __future__ import annotations

import sys

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class PresetClient(Node):
    def __init__(self):
        super().__init__("artis_preset_client")
        self.pub = self.create_publisher(String, "/artis_gripper/preset", 10)

    def send(self, preset: str) -> None:
        msg = String()
        msg.data = preset
        self.pub.publish(msg)
        self.get_logger().info(f"Published ARTiS preset: {preset}")


def main(args=None):
    rclpy.init(args=args)
    node = PresetClient()
    preset = sys.argv[1] if len(sys.argv) > 1 else "z"
    for _ in range(3):
        node.send(preset)
        rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
