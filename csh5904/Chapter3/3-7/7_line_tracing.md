
# 7_line_tracing.md

## 1. URDF 조인트(Joint) 추가 사양

### A. 바퀴 조인트 (모터 및 엔코더 역할)
별도의 복잡한 액추에이터 태그 없이, `continuous` 타입의 조인트를 좌우에 각각 배치합니다. Gazebo의 차동 구동 플러그인이 이 조인트를 직접 굴리고(모터 기능), 회전 값을 읽어와 상태를 발행(엔코더 기능)합니다. 바퀴의 회전 방향과 각속도는 이 조인트의 회전축(`axis`)을 기준으로 동일하게 매칭됩니다.

```xml
<joint name="left_wheel_joint" type="continuous">
  <parent link="base_link"/>
  <child link="left_wheel_link"/>
  <origin xyz="0 0.15 0" rpy="-1.5708 0 0"/>
  <axis xyz="0 0 1"/>
</joint>

<joint name="right_wheel_joint" type="continuous">
  <parent link="base_link"/>
  <child link="right_wheel_link"/>
  <origin xyz="0 -0.15 0" rpy="-1.5708 0 0"/>
  <axis xyz="0 0 1"/>
</joint>

```

### B. IR 센서 고정 조인트 3개 (Left, Center, Right)

로봇 전면 하단부에서 바닥면을 수직으로 바라보도록 피치(Pitch) 값을 조정(`rpy="0 1.5708 0"`)한 고정형(`fixed`) 조인트 3개를 추가합니다.

```xml
<joint name="ir_left_joint" type="fixed">
  <parent link="base_link"/>
  <child link="ir_left_link"/>
  <origin xyz="0.2 0.05 0.01" rpy="0 1.5708 0"/>
</joint>

<joint name="ir_center_joint" type="fixed">
  <parent link="base_link"/>
  <child link="ir_center_link"/>
  <origin xyz="0.2 0.0 0.01" rpy="0 1.5708 0"/>
</joint>

<joint name="ir_right_joint" type="fixed">
  <parent link="base_link"/>
  <child link="ir_right_link"/>
  <origin xyz="0.2 -0.05 0.01" rpy="0 1.5708 0"/>
</joint>

```

---

## 2. Gazebo 시뮬레이션 플러그인 조사

가제보 환경에서 물리 연산 및 ROS 2 토픽 연동을 담당하는 표준 플러그인 사양입니다.

### A. 차동 주행 및 엔코더 플러그인 (`libgazebo_ros_diff_drive.so`)

* **역할:** 모터와 엔코더 하드웨어를 소프트웨어적으로 통합 대체하는 핵심 플러그인입니다.
* **상세 기능:**
* **모터 모사:** ROS 2의 `/cmd_vel` 토픽(선속도, 각속도)을 구독하여 URDF에 정의된 `left_wheel_joint`와 `right_wheel_joint`에 물리적인 회전력을 인가합니다.
* **엔코더 모사:** 바퀴 조인트가 실제로 회전한 물리적 각도 및 속도를 실시간으로 역산하여 로봇의 현재 추정 위치인 오도메트리 토픽(`/odom`)과 바퀴 조인트 상태 데이터(`/joint_states`)를 발행합니다.



### B. 레이저 기반 IR 센서 플러그인 (`libgazebo_ros_ray_sensor.so`)

* **역할:** 물리적인 적외선 반사형 IR 센서를 가제보의 단거리 레이저 빔(`Ray`)을 통해 모사합니다.
* **상세 기능:**
* 각 IR 센서 조인트(`ir_left_joint` 등) 위치에서 바닥 방향으로 얇은 단일 가상 레이저 빔을 쏘아 거리를 측정합니다.
* 가제보 월드 바닥면에 표현된 라인(특정 텍스처 또는 레이어)의 유무에 따라 감지되는 물리적 거리 값이 미세하게 변하는 특성을 이용해, 라인 정합 상태 데이터를 정수 배열 형태나 센서 토픽으로 변환하여 발행합니다.



```
