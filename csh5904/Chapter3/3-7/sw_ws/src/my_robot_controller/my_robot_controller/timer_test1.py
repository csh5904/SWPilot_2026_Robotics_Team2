import rclpy
from rclpy.node import Node

class TimerTestNode(Node):
    def __init__(self):
        super().__init__('timer_node')
        
        self.timer_period = 2.0
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    def timer_callback(self):
        self.get_logger().info("2 seconds passed")

def main(args=None):
    rclpy.init(args=args)
    node = TimerTestNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("사용자에 의해 타이머 노드가 종료됩니다.")
    finally:
        node.destroy_node()
        if rclpy.ok(): 
            rclpy.shutdown()

if __name__ == '__main__':
    main()
