import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class circle_drive_node(Node):
    def __init__(self):
        super().__init__('circle_drive_node')
        
        # 1. /joint_states 토픽을 발행할 Publisher 생성
        self.wheel_pub = self.create_publisher(Twist, '/cmd_vel', 30)
        
        # 2. 0.1초(10Hz)마다 토픽을 발행할 타이머 생성
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        # 관절 제어를 위한 임시 변수 (가상으로 움직임을 주기 위함)
        self.pose = 0.0

    def timer_callback(self):
        msg=Twist()
        msg.linear.x = 1.0  
        msg.angular.z = 0.55
        self.wheel_pub.publish(msg)
        

        


def main(args=None):
    rclpy.init(args=args)
    node = circle_drive_node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()