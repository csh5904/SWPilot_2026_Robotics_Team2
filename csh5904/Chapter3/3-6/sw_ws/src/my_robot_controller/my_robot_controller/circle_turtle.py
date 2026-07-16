import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CircleTurtle(Node):
    def __init__(self):
        super().__init__('circle_turtle_node')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 1.0  
        msg.angular.z = 1.0  
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg)

def main(args=None):
    rclpy.init(args=args)
    circle_turtle_node = CircleTurtle()

    try:
        rclpy.spin(circle_turtle_node)
    except KeyboardInterrupt:
        circle_turtle_node.get_logger().info("사용자에 의해 원형 이동 노드가 안전하게 종료됩니다.")
    finally:
        circle_turtle_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()