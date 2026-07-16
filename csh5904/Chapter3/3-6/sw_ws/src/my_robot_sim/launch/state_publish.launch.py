import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot_sim')
    xacro_file = os.path.join(pkg_share, 'urdf', 'my_first_robot.urdf.xacro')

    # Xacro 파싱 및 XML 변환
    robot_description_config = xacro.process_file(xacro_file)
    robot_desc = robot_description_config.toxml()

    return LaunchDescription([
        # 1. URDF 설계도를 주입받아 기구학 변환(/tf)을 뿜어내는 노드
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),
        
        # 2. 질문자님이 작성한 /joint_states 발행 노드
        Node(
            package='my_robot_sim',
            executable='joint_state_publisher',
            name='custom_joint_state_publisher',
            output='screen'
        ),
        
        # 3. [완벽 수정] 괄호나 콤마 없이 공백과 등호(=)로만 파싱하는 RViz2 인라인 주입 문법
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen'
        )
    ])