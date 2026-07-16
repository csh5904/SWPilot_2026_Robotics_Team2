import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

class TurtlePoseNode(Node):
    def __init__(self):
        super().__init__('turtle_pose_node')
        self.subscription = self.create_subscription(
            Pose,
            'turtle1/pose',
            self.pose_callback,
            10
        )
        self.subscription  # prevent unused variable warning

    def pose_callback(self, msg):
        self.get_logger().info(f"Turtle Pose - x: {msg.x}, y: {msg.y}, theta: {msg.theta}")

def main(args=None):
    rclpy.init(args=args)
    turtle_pose_node = TurtlePoseNode()

    try:
        rclpy.spin(turtle_pose_node)
    except KeyboardInterrupt:
        turtle_pose_node.get_logger().info("사용자에 의해 거북이 위치 노드가 안전하게 종료됩니다.")
    finally:
        turtle_pose_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    
if __name__ == '__main__':
    main()