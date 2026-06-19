import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from std_srvs.srv import SetBool, Trigger

from artis_gripper import ArtisGripper


class ArtisNode(Node):
    def __init__(self):
        super().__init__("artis_gripper")
        self.declare_parameter("config", "configs/artis_default.yaml")
        config = self.get_parameter("config").get_parameter_value().string_value
        self.gripper = ArtisGripper(config)
        self.gripper.connect()

        self.create_subscription(String, "artis_gripper/preset", self.on_preset, 10)
        self.create_subscription(JointState, "artis_gripper/joint_command_ticks", self.on_joint_ticks, 10)
        self.create_service(SetBool, "artis_gripper/set_jamming", self.on_set_jamming)
        self.create_service(Trigger, "artis_gripper/read_state", self.on_read_state)
        self.pub_state = self.create_publisher(JointState, "artis_gripper/joint_states", 10)
        self.timer = self.create_timer(0.1, self.publish_state)
        self.get_logger().info("ARTiS gripper node started")

    def on_preset(self, msg):
        try:
            self.gripper.apply_preset(msg.data)
        except Exception as exc:
            self.get_logger().error(str(exc))

    def on_joint_ticks(self, msg):
        try:
            targets = {name: int(pos) for name, pos in zip(msg.name, msg.position)}
            self.gripper.move_to_ticks(targets)
        except Exception as exc:
            self.get_logger().error(str(exc))

    def on_set_jamming(self, request, response):
        try:
            self.gripper.jam_on() if request.data else self.gripper.jam_off()
            response.success = True
            response.message = "JAM_ON" if request.data else "JAM_OFF"
        except Exception as exc:
            response.success = False
            response.message = str(exc)
        return response

    def on_read_state(self, request, response):
        try:
            response.success = True
            response.message = str(self.gripper.read_joint_ticks())
        except Exception as exc:
            response.success = False
            response.message = str(exc)
        return response

    def publish_state(self):
        try:
            ticks = self.gripper.read_joint_ticks()
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = list(ticks.keys())
            msg.position = [float(v) for v in ticks.values()]
            self.pub_state.publish(msg)
        except Exception as exc:
            self.get_logger().warn(str(exc))

    def destroy_node(self):
        self.gripper.shutdown()
        super().destroy_node()


def main():
    rclpy.init()
    node = ArtisNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
