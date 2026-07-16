import rclpy
from rclpy.node import Node


class LoggingNode(Node):
    def __init__(self):
        super().__init__('logging_node')

        self.count = 0
        node_name = self.get_name()
        self.get_logger().info(f"노드가 성공적으로 시작되었습니다. 노드 이름: '{node_name}'")
        self.hellotimer = self.create_timer(1.0, self.hellotimercallback)

    def hellotimercallback(self):
        self.count += 1
        self.get_logger().info(f'타이머 작동 {self.count}')


def main(args=None):
    rclpy.init(args=args)

    node = LoggingNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("사용자에 의해 노드가 안전하게 종료됩니다.")
    finally:
        node.destroy_node()
        if rclpy.ok():
          rclpy.shutdown()


if __name__ == '__main__':
    main()