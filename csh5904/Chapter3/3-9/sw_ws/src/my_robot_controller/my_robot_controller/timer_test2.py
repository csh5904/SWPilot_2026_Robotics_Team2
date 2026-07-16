import rclpy
from rclpy.node import Node

class MultiTimerNode(Node):
    def __init__(self):
        super().__init__('timer_node2')
        
        self.counter = 0
        
        self.increase_timer = self.create_timer(2.0, self.increase_callback)
        

        self.decrease_timer = self.create_timer(3.0, self.decrease_callback)


    def increase_callback(self):
        self.counter += 1
        self.get_logger().info(f"2 seconds passed :{self.counter}")

    def decrease_callback(self):
        self.counter -= 1
        self.get_logger().info(f"3 seconds passed :{self.counter}")

def main(args=None):
    rclpy.init(args=args)
    node = MultiTimerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("사용자 요청으로 멀티 타이머 동작을 안정적으로 종료합니다.")
    finally:
        node.destroy_node()
        if rclpy.ok(): 
            rclpy.shutdown()

if __name__ == '__main__':
    main()