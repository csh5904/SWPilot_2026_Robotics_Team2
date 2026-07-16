# 6_gazebo_world.md

## 1. Gazebo 환경(World) 파일 개요

Gazebo 시뮬레이터에서 로봇이 움직이는 가상 공간(지면, 조명, 빌딩, 장애물 등)을 정의하는 파일을 **환경 파일 또는 월드(World) 파일**이라고 합니다.

* **파일 형식:** XML 기반의 **SDF(Simulation Description Format)** 형식을 사용하며, 확장자는 `.world`입니다.
* **주요 구성 요소:**
* **물리 엔진 설정 (`<physics>`):** 중력 방향 및 크기($-9.81\text{m/s}^2$), 타임 스텝 세밀도 등
* **조명 (`<light>`):** 태양광(Directional), 포인트 조명 등 시뮬레이션 내 광원
* **기반 환경 (`<include>`):** 기본 지면(`ground_plane`) 및 외부 SDF 모델 호출
* **플러그인 (`<plugin>`):** 월드 전체의 상태를 제어하거나 모니터링하는 기능 스크립트



---

## 2. 시뮬레이션 환경(World) 구축 방법

Gazebo 월드 파일은 가상 공간의 복잡도와 작업 목적에 따라 여러 가지 방법으로 생성할 수 있습니다.

| 방법 | 특징 및 장단점 | 주요 용도 |
| --- | --- | --- |
| **텍스트 에디터 직접 작성** | VS Code, NeoVim 등을 이용해 XML(SDF) 코드를 직접 하드코딩하는 방식. 미세한 수치 조정과 물리 엔진 설정을 완벽하게 제어할 수 있으나 시각적 배치가 어려움. | 정밀한 물리 특성 제어, 빈 월드(`empty.world`) 생성 |
| **Gazebo GUI 도구 활용** | Gazebo 창 내에서 제공하는 `Building Editor`나 `Model Editor`를 사용하여 마우스 드래그 앤 드롭으로 벽을 세우고 창문을 배치하는 방식. 직관적이고 빠름. | 실내 지도(Floor Plan), 미로 및 방 구조물 설계 |
| **3D 모델링 툴 연동 (Blender 등)** | Blender, Maya, CAD 등으로 정교한 3D 환경을 디자인한 후, 이를 `.dae(Collada)` 나 `.stl` 파일로 내보내어 Gazebo SDF 모델로 감싸는 방식. | 복잡한 지형, 실제 도시 환경, 정교한 가구 배치 |
| **알고리즘 기반 자동 생성 (Procedural)** | Python 스크립트 등을 이용해 장애물의 위치나 지형을 무작위 또는 특정 규칙(격자형, 랜덤 배치 등)에 따라 코드로 자동 생성하는 방식. | SLAM/내비게이션 학습용 랜덤 맵, 데이터셋 수집 환경 |

---

## 3. 월드 좌표계(World Coordinate)와 로컬 좌표계(Local Coordinate)

ROS 2 및 Gazebo 시뮬레이션에서는 위치와 자세를 정확히 표현하기 위해 여러 개의 좌표계를 계층적으로 사용합니다.

### 3.1. 월드 좌표계 (World / Global Coordinate System)

* **개념:** 시뮬레이션 가상 공간 전체의 **절대적인 기준**이 되는 고정 좌표계입니다.
* **특징:** 절대 변하지 않는 원점 $(0, 0, 0)$을 가지며, 북쪽/남쪽/하늘 방향 등 맵 전체의 절대 방향을 정의합니다. Gazebo 플러그인 등에서 로봇의 실제 절대 위치(Odometry Ground Truth)를 파악할 때 기준이 됩니다.

### 3.2. 로컬 좌표계 (Local / Body Coordinate System)

* **개념:** 로봇 본체 또는 특정 링크(예: `base_link`, `sensor_link`)의 **중심을 원점으로 삼는 상대적 좌표계**입니다.
* **특징:** 로봇이 이동하거나 회전하면 로봇의 로컬 좌표계도 함께 움직입니다.
* 로봇 기준의 방향 정의 표준 (ROS 규격): **X축(앞방향), Y축(왼쪽방향), Z축(하늘방향)**



### 3.3. 두 좌표계의 관계 (동차 변환, Homogeneous Transformation)

로봇이 월드 좌표계 안에서 이동할 때, 로컬 좌표계와 월드 좌표계 사이의 관계는 이동(Translation)과 **회전(Rotation)** 행렬의 조합으로 계산됩니다.

* **좌표 변환:** 로봇에 장착된 라이다(LiDAR) 센서가 로컬 좌표계 기준으로 장애물을 탐지하면, 시뮬레이터는 현재 로봇의 상태(Pose)를 기반으로 변환 행렬을 곱하여 월드 좌표계 기준의 절대 위치로 변환합니다.
* **표현 방식:** 위치는 $x, y, z$ 데이터로 표현하며, 회전 정보는 관절 뒤틀림(Gimbal Lock) 현상을 방지하기 위해 주로 **쿼터니언(Quaternion, 사원수)** 포맷($x, y, z, w$)을 사용하여 월드 좌표계 대비 로봇의 자세를 정의합니다.

---

## 4. 환경 파일과 함께 시뮬레이터 실행하는 방법

ROS 2(Humble 기준)에서 작성한 `.world` 환경 파일을 포함하여 Gazebo를 실행하는 방법은 크게 두 가지가 있습니다.

### 방법 1. CLI(터미널)에서 직접 실행

Gazebo 서버를 구동할 때 인자값으로 월드 파일의 경로를 직접 넘겨주는 방식입니다.

```bash
# 기본 제공되는 empty.world 실행 예시
gazebo /usr/share/gazebo-11/worlds/empty.world

# 내가 만든 custom.world 실행 예시 (verbose 옵션으로 에러 로그 확인 가능)
gazebo --verbose /path/to/your_workspace/src/my_package/worlds/custom.world

```

### 방법 2. ROS 2 Launch 스크립트를 통한 실행 (권장)

`gazebo_ros` 패키지에서 제공하는 `gzserver`와 `gzclient` 노드를 활용하여, 런치 파일 실행 시 커스텀 월드 경로를 아규먼트(Argument)로 전달하는 방식입니다. 파이썬 launch 스크립트 내부에 주로 다음과 같이 작성합니다.

```python
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # 1. 패키지 경로 및 월드 파일 경로 설정
    pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')
    pkg_my_robot = FindPackageShare(package='my_robot_sim').find('my_robot_sim')
    world_path = os.path.join(pkg_my_robot, 'worlds', 'custom.world')

    # 2. Gazebo 서버 실행 정의 (월드 파일 경로 주입)
    start_gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world_path}.items()
    )

    # 3. Gazebo 클라이언트(GUI 창) 실행 정의
    start_gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py'))
    )

    return LaunchDescription([
        start_gazebo_server,
        start_gazebo_client
    ])

```