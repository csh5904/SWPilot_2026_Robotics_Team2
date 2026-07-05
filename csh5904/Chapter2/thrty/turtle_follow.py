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
        self.turtle1_pose = None
        self.turtle2_pose = None

        # [수정 1] 타이머 객체를 self.spawn_timer 변수에 올바르게 할당합니다.
        self.spawn_timer = self.create_timer(1.0, self.spawn_initial_turtle)

    def pose_callback1(self, msg):
        if self.should_shutdown:
            return

        twist_msg = Twist()
        x, y, theta = msg.x, msg.y, msg.theta
        self.turtle1_pose = [x, y, theta]

        if self.turtle1_pose is not None and self.turtle2_pose is not None:
            twist_msg.angular.z = 2.0 * (np.arctan2(self.turtle2_pose[1]-y, self.turtle2_pose[0]-x) - theta)
            twist_msg.linear.x = 2.0
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
            twist_msg.linear.x = 3.0
            twist_msg.angular.z = 0.0
        else:
            twist_msg.linear.x = 1.0 * (safe_wall_distance - front_laser_distance)
            twist_msg.angular.z = 3.0

        self.turtle_kill_pose()
        self.publisher_2.publish(twist_msg)

    def turtle_kill_pose(self):
        if self.turtle1_pose is not None and self.turtle2_pose is not None:
            dist_sq = (
                (self.turtle1_pose[0] - self.turtle2_pose[0]) ** 2
                + (self.turtle1_pose[1] - self.turtle2_pose[1]) ** 2
            )

            if dist_sq < 0.5**2:
                kill_req1 = Kill.Request()
                kill_req1.name = 'turtle1'
                kill_req2 = Kill.Request()
                kill_req2.name = 'turtle2'
                self.kill_client.call_async(kill_req1)
                future2 = self.kill_client.call_async(kill_req2)
                future2.add_done_callback(self.kill_response_callback)

    def get_min_distance_to_wall(self, x, y, theta, twist_msg):
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        if cos_t > 0:
            dist_x = (11.0 - x) / cos_t
        elif cos_t < 0:
            dist_x = (0.0 - x) / cos_t
        else:
            dist_x = float('inf')
            twist_msg.angular.z = 0.001
        
        if sin_t > 0:
            dist_y = (11.0 - y) / sin_t
        elif sin_t < 0:
            dist_y = (0.0 - y) / sin_t
        else:
            dist_y = float('inf')
            twist_msg.angular.z = 0.001
        return min(dist_x, dist_y)

    def spawn_initial_turtle(self):
        if not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Spawn service not available yet.')
            return
        
        # [수정 2] 이제 변수가 안전하게 등록되어 있으므로 정상 작동합니다.
        self.spawn_timer.destroy()
        self.spawn_turtle()

    def spawn_turtle(self, x=None, y=None, theta=None):
        if not self.spawn_client.service_is_ready():
            self.get_logger().warn('Spawn service is not ready yet.')
            return

        spawn_req = Spawn.Request()
        spawn_req.x = random.uniform(1.0, 10.0) if x is None else x  # 벽에 끼지 않게 최소 마진 확보
        spawn_req.y = random.uniform(1.0, 10.0) if y is None else y
        spawn_req.theta = random.uniform(0.0, 2 * np.pi) if theta is None else theta
        spawn_req.name = 'turtle2'

        future = self.spawn_client.call_async(spawn_req)
        future.add_done_callback(lambda fut: self.spawn_response_callback(fut, spawn_req))


    def spawn_response_callback(self, future, request):
        try:
            response = future.result()
            self.get_logger().info(
                f"Turtle spawned at ({request.x:.2f}, {request.y:.2f}) with name '{response.name}'."
            )
        except Exception as e:
            self.get_logger().error(f'Failed to spawn turtle: {e}')

    def quit_callback(self, request, response):
        self.get_logger().info('삭제')
        kill_req = Kill.Request()
        kill_req.name = 'turtle1'
        self.kill_client.call_async(kill_req)
        
        kill_req2 = Kill.Request()
        kill_req2.name = 'turtle2'
        future2 = self.kill_client.call_async(kill_req2)
        future2.add_done_callback(self.kill_response_callback)
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
