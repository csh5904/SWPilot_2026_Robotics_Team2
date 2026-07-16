import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math

class circle_drive_node(Node):
    def __init__(self):
        super().__init__('circle_drive_node')
        
        # 1. /joint_states 토픽을 발행할 Publisher 생성
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        
        # 2. 0.1초(10Hz)마다 토픽을 발행할 타이머 생성
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        # 관절 제어를 위한 임시 변수 (가상으로 움직임을 주기 위함)
        self.pose = 0.0

    def timer_callback(self):
        # 3. JointState 메시지 객체 생성
        msg = JointState()
        
        # 4. 현재 시간 타임스탬프 설정 (TF 매칭을 위해 필수!)
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # 5. URDF에 적힌 정확한 관절 이름 매칭
        msg.name = ['right_back_wheel_joint', 'left_back_wheel_joint']
        msg.position = [self.pose, self.pose]
        # 7. 메시지 발행
        self.joint_pub.publish(msg)
        self.get_logger().info(f'Publishing Joint States: {msg.position}')
        


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