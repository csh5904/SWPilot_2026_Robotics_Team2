import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
 
    my_package_dir = get_package_share_directory('my_robot_controller')  
    
    turtlesim_node = Node(
        package='turtlesim',          
        executable='turtlesim_node',  
        name='turtlesim_simulator',   
        namespace='',                 
        output='screen'             
    )

   
    control_node = Node(
        package='my_robot_controller',   # ⚠️ 생성한 파이썬 패키지 이름과 완벽히 일치해야 함 (필수)
        executable='turtle_follow_node', # setup.py의 console_scripts에 기입한 키값 명칭 (필수)
        name='turtle_follow_node',
        namespace='',
        output='screen'         
    )    

    
    return LaunchDescription([
        turtlesim_node,
        control_node
    ])