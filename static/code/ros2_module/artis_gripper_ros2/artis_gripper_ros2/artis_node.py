from __future__ import annotations

from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, String
from std_srvs.srv import SetBool, Trigger

from artis_gripper import ArtisGripper, load_config


class ArtisNode(Node):
    def __init__(self):
        super().__init__("artis_gripper")
        self.declare_parameter("config", "configs/artis_default.yaml")
        self.declare_parameter("publish_rate_hz", 20.0)
        self.declare_parameter("connect_on_start", True)

        config_path = Path(self.get_parameter("config").value)
        self.config = load_config(config_path)
        self.joint_names = list(self.config.motors.keys())
        self.gripper = ArtisGripper(self.config)

        if bool(self.get_parameter("connect_on_start").value):
            self.gripper.connect(enable_torque=True)
            self.get_logger().info(f"Connected to ARTiS using config: {config_path}")

        self.joint_pub = self.create_publisher(JointState, "~/joint_states", 10)
        self.create_subscription(JointState, "~/joint_command_ticks", self.on_joint_command, 10)
        self.create_subscription(String, "~/preset", self.on_preset, 10)
        self.create_subscription(Bool, "~/jamming", self.on_jamming, 10)

        self.create_service(SetBool, "~/set_jamming", self.set_jamming_srv)
        self.create_service(Trigger, "~/torque_enable", self.torque_enable_srv)
        self.create_service(Trigger, "~/torque_disable", self.torque_disable_srv)

        period = 1.0 / float(self.get_parameter("publish_rate_hz").value)
        self.timer = self.create_timer(period, self.publish_state)

    def on_joint_command(self, msg: JointState) -> None:
        positions = {name: int(pos) for name, pos in zip(msg.name, msg.position) if name in self.config.motors}
        if positions:
            self.gripper.move_ticks(positions)

    def on_preset(self, msg: String) -> None:
        try:
            self.gripper.apply_preset(msg.data.strip())
        except Exception as exc:
            self.get_logger().error(str(exc))

    def on_jamming(self, msg: Bool) -> None:
        self.gripper.set_jamming(bool(msg.data))

    def set_jamming_srv(self, request: SetBool.Request, response: SetBool.Response) -> SetBool.Response:
        try:
            self.gripper.set_jamming(bool(request.data))
            response.success = True
            response.message = "Jamming palm ON" if request.data else "Jamming palm OFF"
        except Exception as exc:
            response.success = False
            response.message = str(exc)
        return response

    def torque_enable_srv(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        self.gripper.enable_torque(True)
        response.success = True
        response.message = "Torque enabled"
        return response

    def torque_disable_srv(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        self.gripper.enable_torque(False)
        response.success = True
        response.message = "Torque disabled"
        return response

    def publish_state(self) -> None:
        try:
            ticks = self.gripper.read_joint_ticks(self.joint_names)
        except Exception as exc:
            self.get_logger().warn(f"Could not read joint state: {exc}")
            return
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [float(ticks[name]) for name in self.joint_names]
        self.joint_pub.publish(msg)

    def destroy_node(self) -> bool:
        try:
            self.gripper.close(disable_torque=True)
        finally:
            return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ArtisNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
