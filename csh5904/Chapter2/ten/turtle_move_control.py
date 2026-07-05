import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class TurtleMoveControl(Node):
    def __init__(self):
        super().__init__('turtle_move_control_node')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose,
            'turtle1/pose',
            self.pose_callback,
            10
        )
        self.subscription  # prevent unused variable warning

    def pose_callback(self, msg):
        twist_msg = Twist()
        if (abs(msg.x -5.544445) < 4.5) and (abs(msg.y -5.544445) < 4.5):
            twist_msg.linear.x = 1.0
        else:
         twist_msg.linear.x = 0.4  
         twist_msg.angular.z = 1.0  
        self.publisher_.publish(twist_msg)
        self.get_logger().info(f"Publishing: linear.x={twist_msg.linear.x}, angular.z={twist_msg.angular.z}")

def main(args=None):
    rclpy.init(args=args)
    turtle_move_control_node = TurtleMoveControl()

    try:
        rclpy.spin(turtle_move_control_node)
    except KeyboardInterrupt:
        turtle_move_control_node.get_logger().info("사용자에 의해 거북이 이동 제어 노드가 안전하게 종료됩니다.")
    finally:
        turtle_move_control_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()