import math
import time

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster


def quaternion_from_axis(axis, angle):
    """Quaternion (x, y, z, w) for a rotation of `angle` about a unit axis."""
    half = angle / 2.0
    s = math.sin(half)
    c = math.cos(half)
    if axis == 'x':
        return s, 0.0, 0.0, c
    if axis == 'y':
        return 0.0, s, 0.0, c
    return 0.0, 0.0, s, c


class StatePublisher(Node):

    def __init__(self):
        super().__init__('state_publisher')
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # the four moving joints, in the order used below
        self.joint_names = ['l1_connect', 'l2_connect', 'tilt', 'periscope']
        self.joint_positions = [0.0, 0.0, 0.0, 0.0]

        self.start_time = self.get_clock().now()

    def publish_joint_states(self, stamp):
        msg = JointState()
        msg.header.stamp = stamp
        msg.name = self.joint_names
        msg.position = self.joint_positions
        self.joint_pub.publish(msg)

    def send_transform(self, stamp, parent, child, xyz, axis=None, angle=0.0):
        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id = parent
        t.child_frame_id = child
        t.transform.translation.x = float(xyz[0])
        t.transform.translation.y = float(xyz[1])
        t.transform.translation.z = float(xyz[2])
        if axis is None:
            t.transform.rotation.w = 1.0
        else:
            qx, qy, qz, qw = quaternion_from_axis(axis, angle)
            t.transform.rotation.x = qx
            t.transform.rotation.y = qy
            t.transform.rotation.z = qz
            t.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(t)

    def publish_tf(self, stamp):
        q = self.joint_positions
        # keep these numbers in sync with r2d2.urdf
        self.send_transform(stamp, 'axis', 'leg1',
                            (0.0, 0.34, 0.55), 'y', q[0])
        self.send_transform(stamp, 'axis', 'leg2',
                            (0.0, -0.34, 0.55), 'y', q[1])
        self.send_transform(stamp, 'axis', 'body',
                            (0.0, 0.0, 0.4))
        self.send_transform(stamp, 'body', 'head',
                            (0.0, 0.0, 0.7), 'x', q[2])
        self.send_transform(stamp, 'head', 'rod',
                            (0.0, 0.0, 0.5), 'z', q[3])
        self.send_transform(stamp, 'head', 'box',
                            (0.0, -0.24, 0.25))

    def run(self):
        period = 1.0 / 30.0
        while rclpy.ok():
            now = self.get_clock().now()
            t = (now - self.start_time).nanoseconds / 1e9

            self.joint_positions[0] = 0.3 * math.sin(t)        # leg 1 swing
            self.joint_positions[1] = -0.3 * math.sin(t)       # leg 2, mirrored
            self.joint_positions[2] = 0.5 * math.sin(2.0 * t)  # head nod
            self.joint_positions[3] = 0.8 * math.sin(0.5 * t)  # rod spin

            stamp = now.to_msg()
            self.publish_joint_states(stamp)
            self.publish_tf(stamp)

            time.sleep(period)


def main(args=None):
    rclpy.init(args=args)
    node = StatePublisher()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
