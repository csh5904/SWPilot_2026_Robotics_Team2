import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_robot_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', 'turtle.launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='cdu5904',
    maintainer_email='cdu5904@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'logging_node=my_robot_controller.logging:main',
            'timer_node1=my_robot_controller.timer_test1:main',
            'timer_node2=my_robot_controller.timer_test2:main',
            'circle_turtle_node=my_robot_controller.circle_turtle:main',
            'turtle_pose_node = my_robot_controller.turtle_pose:main',
            'turtle_move_control_node = my_robot_controller.turtle_move_control:main',
            'turtle_move_control_service_node = my_robot_controller.turtle_move_control_service:main',
            'turtle_follow_node = my_robot_controller.turtle_follow:main'
        ],
    },
)
