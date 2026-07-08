
# [ROS 2] Launch File 및 파이썬 기반 자동화 가이드

## 1. ROS 2 Launch File 개요
로봇 시스템이 커지면 센서 드라이버, 슬램(SLAM), 네비게이션, 모터 제어 등 수많은 노드를 각각 다른 터미널에서 `ros2 run`으로 일일이 켜는 것이 불가능해집니다.
**Launch File**은 여러 개의 노드를 **하나의 명령어(스크립트)로 한방에 실행, 관리, 파라미터 주입**까지 제어할 수 있게 해주는 마스터 스크립트입니다.

ROS 2에서는 Python, XML, YAML 형식을 지원하지만, 복잡한 조건문이나 동적 제어가 가능한 **파이썬(Python) 방식**이 가장 널리 쓰입니다.

---

## 2. 파이썬 기반 Launch File 작성법
파이썬 기반 Launch 파일은 통상 패키지 내부의 `launch/` 폴더 안에 `*.launch.py`라는 이름으로 저장합니다.

### 📝 예시 파일: `turtlesim_swim.launch.py`
아래는 거북이 시뮬레이터(`turtlesim_node`)와 우리가 이전 단계에서 만든 제어 노드(`turtle_move_control_node`)를 한 번에 묶어서 켜주는 예제 스크립트입니다.

```python
# [ROS 2] 파이썬 기반 Launch File 표준 전체 양식


```python
import os
# ROS 2 Launch 시스템의 뼈대를 구성하는 핵심 라이브러리
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

# ROS 2 노드를 실행하기 위해 필요한 핵심 라이브러리
from launch_ros.actions import Node
# 빌드된 패키지의 설치 경로(share 디렉토리)를 동적으로 찾아오기 위한 도구
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    """
    ROS 2 Launch 시스템이 파일 실행 시 자동으로 호출하는 마스터 함수입니다.
    이 함수가 반환하는 LaunchDescription 객체 내부의 모든 액션들이 실행됩니다.
    """
    
    # 1. 패키지 경로 동적 획득 (패키지 내 설정 파일이나 YAML을 로드해야 할 때 활용)
    # 여기서는 본인의 제어 패키지 이름을 정확히 기입해야 합니다.
    my_package_dir = get_package_share_directory('my_turtle_control')
    
    # [참고] 만약 외부 YAML 설정 파일을 쓰고 싶다면 아래와 같이 경로 조립에 사용합니다.
    # example_param_path = os.path.join(my_package_dir, 'config', 'params.yaml')

    # 2. 첫 번째 노드 설정: turtlesim 시뮬레이터 본체
    turtlesim_node = Node(
        package='turtlesim',          # 실행 파일이 위치한 ROS 2 패키지 이름 (필수)
        executable='turtlesim_node',  # package.xml 및 빌드 스크립트에 등록된 실행 파일 이름 (필수)
        name='turtlesim_simulator',   # 런타임에 노드에 부여할 고유 이름 (동일 노드 다중 실행 시 분리용)
        namespace='',                 # 노드가 사용하는 토픽/서비스 앞에 붙을 그룹 네임스페이스 (기본값은 빈 문자열)
        parameters=[],                # 노드에 주입할 파라미터 리스트 (딕셔너리 또는 YAML 파일 경로)
        remappings=[],                # 토픽이나 서비스의 이름을 강제로 리다이렉션할 때 사용 (예: [('/old', '/new')])
        arguments=[],                 # 실행 파일 전달용 로우(Raw) 명령행 인자 매개변수
        output='screen'               # 노드의 로그 및 표준 출력(print)을 터미널 창에 실시간 출력 (필수 세팅)
    )

    # 3. 두 번째 노드 설정: 사용자 정의 거북이 이동 제어 노드 (/quit 서버 및 /kill 클라이언트 내장)
    control_node = Node(
        package='my_turtle_control',   # ⚠️ 생성한 파이썬 패키지 이름과 완벽히 일치해야 함 (필수)
        executable='turtle_move_control', # setup.py의 console_scripts에 기입한 키값 명칭 (필수)
        name='custom_move_controller',
        namespace='',
        parameters=[],                # 예: [{'target_speed': 2.0}] 구조로 주입 가능
        remappings=[],
        arguments=[],
        output='screen'               # 제어 노드의 상태 로그(get_logger)를 화면으로 모니터링하기 위해 필수 설정
    )

    # 4. 최종 실행할 액션들의 리스트를 생성자에 담아 LaunchDescription 객체 반환
    # 배열 내부에 선언된 순서대로 Launch 시스템이 스레드를 생성하여 실행을 트리거합니다.
    return LaunchDescription([
        turtlesim_node,
        control_node
    ])

```

---

## 3. `setup.py` 파일 수정 (빌드 연동)

파이썬 기반 ROS 2 패키지에서 Launch 파일을 인식하고 빌드 후 배포 디렉토리(`install/`)로 정상 복사하려면, 패키지 루트에 있는 `setup.py`를 수정해야 합니다.

이 설정을 빼먹으면 `ros2 launch` 명령어가 내 launch 파일을 찾지 못합니다.

### 🛠️ `setup.py` 수정 예시

```python
import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_turtle_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # 💡 [핵심 추가 부분] launch 폴더 내의 모든 .launch.py 파일을 빌드 결과물에 포함시킵니다.
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@test.com',
    description='ROS 2 Launch and Control Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 제어 프로그램 실행 스크립트 등록 정보
            'turtle_move_control = my_turtle_control.turtle_move_control:main',
        ],
    },
)

```

---

## 4. `ros2 launch` 명령어 사용법

빌드 및 환경 반영이 완료된 후 터미널에서 다음 명령 구조로 Launch 파일을 실행합니다.

###  명령어 구조

```bash
ros2 launch <패키지_이름> <launch_파일_이름.launch.py>

```

### 💻 실제 실행 예시

```bash
# 1. 워크스페이스 빌드 및 환경 로드
cd ~/ros2_ws
colcon build --packages-select my_turtle_control
source install/local_setup.bash

# 2. Launch 파일을 이용하여 여러 노드 한 번에 켜기
ros2 launch my_turtle_control turtlesim_swim.launch.py

```

* Launch 파일이 실행되면 터미널 창 하나에 `turtlesim` 창이 뜨면서 내가 만든 제어 노드의 출력 로그가 통합되어 출력됩니다.
* 종료할 때는 해당 터미널에서 **Ctrl+C**를 누르면 Launch 시스템이 실행했던 모든 노드를 순차적으로 안전하게 동시 종료(`Clean Shutdown`)시킵니다.

