
---

# 1. URDF의 `<collision>` 및 `<inertial>` 태그와 물리학적 개념

시뮬레이터(Gazebo)가 로봇을 실제 물리 법칙에 따라 계산하려면 시각적 형태(`<visual>`) 외에 **충돌 영역**과 **질량 분포** 정보가 반드시 필요합니다.

### 1) 충돌 속성: `<collision>`

* **개념**: 로봇이 주변 환경(바닥, 장애물)이나 다른 링크와 부딪힐 때 계산되는 물리적 외형입니다.
* **팁**: 계산 복잡도를 줄이기 위해 `<visual>` 태그에는 복잡한 Mesh(STL/DAE)를 쓰더라도, `<collision>` 태그에는 Box, Cylinder, Sphere 같은 기본 기하학 형태(Primitive Shapes)를 사용하는 것이 시뮬레이션 성능에 좋습니다.

### 2) 관성 속성: `<inertial>`

Gazebo의 물리 엔진(ODE 등)이 뉴턴-오일러 방정식을 풀기 위해 요구하는 필수 데이터입니다.

* **질량 (`<mass value="..." />`)**: 링크의 무게(kg 단위)입니다.
* **관성 텐서 (`<inertia>`)**: 물체가 회전 운동에 얼마나 저항하는지를 나타내는 $3 \times 3$ 대칭 행렬입니다. URDF에서는 대칭성을 이용해 6개의 성분만 정의합니다.

$$I = \begin{bmatrix} ixx & ixy & ixz \\ ixy & iyy & iyz \\ ixz & iyz & izz \end{bmatrix}$$


* 일반적으로 주요 축이 질량 중심과 일치한다고 가정하면 교차 관성 성분($ixy, ixz, iyz$)은 `0`으로 설정합니다.


* **질량 중심 (`<origin xyz="..." rpy="..." />`)**: 링크의 기하학적 중심이 아닌, 실제 무게 중심(CoM)의 위치입니다.

#### 💡 적당히 현실적인 주요 형상별 관성 모멘트 공식 ($ixx, iyy, izz$)

* **상자 (Box)** (가로 $w$, 세로 $d$, 높이 $h$, 질량 $m$):
* $ixx = \frac{1}{12}m(d^2 + h^2)$
* $iyy = \frac{1}{12}m(w^2 + h^2)$
* $izz = \frac{1}{12}m(w^2 + d^2)$


* **원기둥 (Cylinder)** (반지름 $r$, 높이 $h$, 질량 $m$, 축이 $z$ 방향일 때):
* $ixx = iyy = \frac{1}{12}m(3r^2 + h^2)$
* $izz = \frac{1}{2}mr^2$



---

# 2. URDF 태그 추가 가이드 (구조 템플릿)

기존에 작성하신 간단한 로봇 모델(예: 바디와 바퀴)에 아래와 같은 형태로 태그를 확장해야 합니다.

```xml
<link name="base_link">
  <visual>
    <geometry><box size="0.5 0.3 0.1"/></geometry>
  </visual>
  
  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry><box size="0.5 0.3 0.1"/></geometry>
  </collision>
  
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="5.0"/> <inertia ixx="0.0416" ixy="0.0" ixz="0.0" iyy="0.1083" iyz="0.0" izz="0.1333"/>
  </inertial>
</link>

```

---

# 3. ROS 2와 Gazebo의 연동 방식 및 로봇 배치 (Spawn)

### 1) 연동 아키텍처

ROS 2와 Gazebo는 `gazebo_ros_pkgs`라는 메타 패키지를 통해 통신합니다.

* Gazebo는 독립적인 물리 시뮬레이터이며, 내부 인터페이스 채널을 가지고 있습니다.
* `gazebo_ros` 패키지에 포함된 **전용 플러그인들**이 Gazebo 내부 데이터(센서 값, 조인트 상태)를 ROS 2 토픽(`/odom`, `/scan`, `/tf` 등)으로 변환하고, ROS 2의 제어 명령(`/cmd_vel`)을 Gazebo 물리 엔진으로 전달합니다.

### 2) 로봇 배치 (Spawning)

ROS 2 시스템에서 Gazebo에 로봇을 생성할 때는 보통 다음과 같은 흐름을 가집니다.

1. `robot_state_publisher` 노드가 URDF(또는 xacro)를 읽어 `robot_description` 토픽으로 발행합니다.
2. `gazebo_ros` 패키지의 **`spawn_entity.py`** 노드를 실행하면서 해당 토픽 내용(또는 파일 경로)을 파라미터로 넘겨줍니다.

---

# 4. Gazebo 플러그인과 `diff_drive_controller`

### 1) Gazebo 플러그인이란? 왜 쓰는가?

Gazebo 플러그인은 시뮬레이터 기능(물리 바인딩, 센서 데이터 생성, 모터 제어 등)을 동적으로 확장할 수 있는 C++ 플러그인입니다.
URDF 내부에 `<gazebo>` 태그를 이용해 선언하며, 이를 사용하지 않으면 URDF 모델은 시뮬레이터 안에서 단순한 '인형'에 불과합니다. **바퀴를 굴리거나 센서 값을 ROS로 받아오려면 반드시 플러그인이 필요합니다.**

### 2) 차동 구동 컨트롤러 (`libgazebo_ros_diff_drive.so`)

두 개의 구동 바퀴(Left/Right Wheel)를 가진 모바일 로봇을 제어하기 위한 표준 플러그인입니다. ROS 2의 `geometry_msgs/msg/Twist` 타입 메시지인 **`/cmd_vel`** 토픽을 구독하여 로봇을 움직입니다.

#### 🛠️ URDF 내 플러그인 삽입 예시 구조

URDF 최하단(또는 별도 xacro 파일)에 아래 매개변수들을 현실적으로 맞춰 지정해야 합니다.

```xml
<gazebo>
  <plugin name="differential_drive_controller" filename="libgazebo_ros_diff_drive.so">
    <update_rate>30</update_rate>
    
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    
    <wheel_separation>0.35</wheel_separation> 
    <wheel_diameter>0.15</wheel_diameter>   
    <max_wheel_torque>20</max_wheel_torque>
    <max_wheel_acceleration>1.0</max_wheel_acceleration>
    
    <command_topic>cmd_vel</command_topic>
    <odometry_topic>odom</odometry_topic>
    <odometry_frame>odom</odometry_frame>
    <robot_base_frame>base_footprint</robot_base_frame>
    
    <publish_odom>true</publish_odom>
    <publish_odom_tf>true</publish_odom_tf>
    <publish_wheel_tf>true</publish_wheel_tf>
  </plugin>
</gazebo>

```

---
