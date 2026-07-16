#!/usr/bin/env python3
"""트랙형 로봇을 Gazebo(Classic)에 스폰하는 ROS2 런치 파일.

사용법:
  ros2 launch tracked_robot gazebo.launch.py
(패키지로 안 만들었을 경우: ros2 launch ./gazebo.launch.py 로도 실행 가능하나,
 아래 urdf 경로를 절대경로로 맞춰주세요)
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # 패키지로 설치했다면 share 경로 사용, 아니면 이 파일 기준 상대 경로 사용
    try:
        pkg_share = get_package_share_directory('tracked_robot')
        urdf_path = os.path.join(pkg_share, 'urdf', 'tracked_robot.urdf')
    except Exception:
        urdf_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'urdf', 'tracked_robot.urdf')

    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('gazebo_ros'),
            'launch', 'gazebo.launch.py')),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'tracked_robot',
            '-z', '0.03',
        ],
        output='screen',
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
    ])
