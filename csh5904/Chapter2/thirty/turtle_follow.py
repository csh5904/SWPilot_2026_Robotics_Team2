import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_srvs.srv import Empty
from turtlesim.srv import Kill
from turtlesim.srv import Spawn
import numpy as np
import random as random

class TurtleLidarFollow(Node):
    def __init__(self):
        super().__init__('turtle_follow_node')
        self.publisher_1 = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.publisher_2 = self.create_publisher(Twist, 'turtle2/cmd_vel', 10)
        self.subscription1 = self.create_subscription(
            Pose,
            'turtle1/pose',
            self.pose_callback1,
            10
        )
        self.subscription2 = self.create_subscription(
            Pose,
            'turtle2/pose',
            self.pose_callback2,
            10
        )
        
        self.create_service(Empty, 'quit', self.quit_callback)
        self.kill_client = self.create_client(Kill, 'kill')
        self.spawn_client = self.create_client(Spawn, 'spawn')
        self.should_shutdown = False

    def pose_callback1(self, msg):
        if self.should_shutdown:
            return

        twist_msg = Twist()
        
        x, y, theta = msg.x, msg.y, msg.theta
        self.turtle1_pose = [x, y, theta]

        theta30 = theta + np.radians(30)
        theta_m30 = theta - np.radians(30)

        front_laser_distance_front = self.get_min_distance_to_wall(x, y, theta, twist_msg)
        front_laser_distance_30 = self.get_min_distance_to_wall(x, y, theta30, twist_msg)
        front_laser_distance_m30 = self.get_min_distance_to_wall(x, y, theta_m30, twist_msg)

        front_laser_distance = min(front_laser_distance_front, front_laser_distance_30, front_laser_distance_m30)

        safe_wall_distance = 2.0

        if front_laser_distance > safe_wall_distance:
            twist_msg.linear.x = 2.0
            twist_msg.angular.z = 0.0
        else:
            twist_msg.linear.x = 0.5 * (safe_wall_distance - front_laser_distance)
            twist_msg.angular.z = 2.0

        self.publisher_1.publish(twist_msg)
    def pose_callback2(self, msg):
        if self.should_shutdown:
            return

        twist_msg = Twist()
        
        x, y, theta = msg.x, msg.y, msg.theta
        self.turtle2_pose = [x, y, theta]

        theta30 = theta + np.radians(30)
        theta_m30 = theta - np.radians(30)

        front_laser_distance_front = self.get_min_distance_to_wall(x, y, theta, twist_msg)
        front_laser_distance_30 = self.get_min_distance_to_wall(x, y, theta30, twist_msg)
        front_laser_distance_m30 = self.get_min_distance_to_wall(x, y, theta_m30, twist_msg)

        front_laser_distance = min(front_laser_distance_front, front_laser_distance_30, front_laser_distance_m30)

        safe_wall_distance = 2.0

        if front_laser_distance > safe_wall_distance:
            twist_msg.linear.x = 2.0
            twist_msg.angular.z = 0.0
        else:
            twist_msg.linear.x = 0.5 * (safe_wall_distance - front_laser_distance)
            twist_msg.angular.z = 2.0

        self.turtle_kill_pose()
        self.publisher_2.publish(twist_msg)

    def turtle_kill_pose(self):
        if self.turtle1_pose is not None and self.turtle2_pose is not None:
            dist_sq = (
                (self.turtle1_pose[0] - self.turtle2_pose[0]) ** 2
                + (self.turtle1_pose[1] - self.turtle2_pose[1]) ** 2
            )

            if dist_sq < 1.0:
                kill_req1 = Kill.Request()
                kill_req1.name = 'turtle1'
                kill_req2 = Kill.Request()
                kill_req2.name = 'turtle2'
                future1 = self.kill_client.call_async(kill_req1)
                future2 = self.kill_client.call_async(kill_req2)
                future2.add_done_callback(self.kill_response_callback)

    def get_min_distance_to_wall(self, x, y, theta, twist_msg):
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        if cos_t > 0:
            dist_x = (11.0 - x) / cos_t  # 우측 벽
        elif cos_t < 0:
            dist_x = (0.0 - x) / cos_t   # 좌측 벽
        else:
            dist_x = float('inf')
            twist_msg.angular.z = 0.001        # 평행할 때
        # Y축 방향 벽까지의 거리 계산
        if sin_t > 0:
            dist_y = (11.0 - y) / sin_t  # 상단 벽
        elif sin_t < 0:
            dist_y = (0.0 - y) / sin_t   # 하단 벽
        else:
            dist_y = float('inf')        # 평행할 때
            twist_msg.angular.z = 0.001        # 평행할 때
        return min(dist_x, dist_y)

    
    def spawn_turtle(self, x=None, y=None, theta=None):
        spawn_req = Spawn.Request()
        spawn_req.x = random.uniform(0.0, 11.0) if x is None else x
        spawn_req.y = random.uniform(0.0, 11.0) if y is None else y
        spawn_req.theta = random.uniform(0.0, 2 * np.pi) if theta is None else theta
        spawn_req.name = 'turtle2'

        future = self.spawn_client.call_async(spawn_req)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            self.get_logger().info(
                f"Turtle spawned at ({spawn_req.x}, {spawn_req.y}) with theta={spawn_req.theta}."
            )
        else:
            self.get_logger().error("Failed to spawn turtle.")

    def quit_callback(self, request, response):
        self.get_logger().info('삭제')
        kill_req = Kill.Request()
        kill_req.name = 'turtle1'
        self.future = self.kill_client.call_async(kill_req)
        kill_req2 = Kill.Request()
        kill_req2.name = 'turtle2'
        self.future2 = self.kill_client.call_async(kill_req2)
        self.future2.add_done_callback(self.kill_response_callback)
        return response

    def kill_response_callback(self, future):
        try:
            future.result()
            self.get_logger().info('거북이가 삭제되었습니다.')
        except Exception as e:
            self.get_logger().error(f'삭제 실패: {e}')
        finally:
            self.should_shutdown = True

def main(args=None):
    rclpy.init(args=args)
    node = TurtleLidarFollow()
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            if node.should_shutdown:
                break
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()