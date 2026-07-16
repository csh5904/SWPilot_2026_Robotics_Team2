import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. 패키지 및 xacro 파일 경로 설정
    pkg_share = get_package_share_directory('my_robot_sim')
    xacro_file = os.path.join(pkg_share, 'urdf', 'my_first_robot_encoder_motor.urdf.xacro')

    # 2. Xacro 파싱 및 XML 변환
    robot_description_config = xacro.process_file(xacro_file)
    robot_desc = robot_description_config.toxml()

    # 💡 [여기가 핵심 추가 부분] 내 패키지의 worlds 폴더 안에 있는 월드 파일 경로 설정
    # 파일명이 만약 다르면 아래 'custom.world' 부분을 실제 형 파일 이름으로 바꿔주면 돼!
    world_file_path = os.path.join(pkg_share, 'world', 'circle_world.world')

    # 3. gazebo_ros 패키지에서 가제보 월드를 켜는 Launch 가져오기 (내 월드 경로 주입)
    gazebo_ros_share = get_package_share_directory('gazebo_ros')
    launch_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_share, 'launch', 'gazebo.launch.py')
        ),
        # 💡 launch_arguments를 통해 내 커스텀 월드 파일을 가제보에 넘겨줌
        launch_arguments={'world': world_file_path}.items()
    )

    # 5. Gazebo 시뮬레이터에 로봇을 생성(Spawn)하는 노드
    node_spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_robot_entity',
        output='screen',
        arguments=[
            '-topic', 'robot_description',  # robot_state_publisher가 내보내는 토픽을 받음
            '-entity', 'my_first_robot',    # 가제보 월드 내에서 불릴 로봇 이름
            '-x', '0.5', '-y', '2.0', '-z', '0.1' # 스폰할 초기 위치 좌표(Z축을 살짝 띄움)
        ]
    )

    # robot_state_publisher 노드 설정
    state_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    motor_encoder_node = Node(
        package='my_robot_sim',
        executable='motor_encoder_node',  # setup.py의 entry_points에 등록한 이름과 일치 필수
        name='motor_encoder_node',
        output='screen'
    )
    scan_node = Node(
        package='my_robot_sim',
        executable='scan_node',
        name='scan_node',
        output='screen'
    )
    line_tracking_pid_node = Node(
        package='my_robot_sim',
        executable='line_tracking_pid_node',
        name='line_tracking_pid_node',
        output='screen'
    )

    # LaunchDescription에 선언한 프로세스 및 노드들을 순서대로 담아서 반환
    return LaunchDescription([
        launch_gazebo,               # 1순위: 내 커스텀 월드가 담긴 가제보가 먼저 켜짐
        state_node,
        node_spawn_entity,           # 3순위: 설계도를 가제보에 던져서 로봇을 출현시킴
        motor_encoder_node,
        scan_node,
        line_tracking_pid_node
    ])