import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_robot_sim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'world'), glob('world/*.world')),
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
            'joint_state_publisher=my_robot_sim.joint_state_publisher:main',
            'circle_drive_node = my_robot_sim.circle_drive_node:main',
            'motor_encoder_node = my_robot_sim.motor_encoder:main',
            'scan_node = my_robot_sim.scan:main',
            'line_tracking_node=my_robot_sim.line_tracking:main',
            'line_tracking_pid_node=my_robot_sim.line_tracking_pid:main'
        ],
    },
)
