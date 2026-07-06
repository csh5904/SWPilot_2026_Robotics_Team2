
---

# `2_urdf_xacro.md`

## 1. URDF (Unified Robot Description Format) 개념 개요

URDF는 ROS(Robot Operating System)에서 **로봇의 물리적 구조, 외형, 기하학적 특성을 설명하기 위해 사용하는 XML 기반의 파일 포맷**입니다. 시뮬레이터(RViz, Gazebo)나 연산 라이브러리가 이 파일을 읽어 로봇을 화면에 그리고 3D 물리 연산을 수행합니다.

### 1) URDF의 핵심 구조 요소

* **`<robot>`**: URDF 파일의 최상위 태그로, 로봇의 이름을 정의합니다.


* **`<link>`**: 로봇의 독립된 부품(뼈대, 살점)을 정의합니다.


* **`<joint>`**: 링크와 링크 사이를 연결하는 관절(움직임 방식)을 정의합니다.


* **`<material>`**: 색상 및 투명도를 정의하는 재질 태그입니다.



---

## 2. 링크(Link)와 조인트(Joint)란?

### 1) 링크 (Link)

로봇의 **강체(Rigid Body) 부품** 자체를 의미합니다. 각 링크는 고유의 로컬 좌표계를 가집니다.

* **`<visual>`**: 눈에 보이는 외형(상자, 원기둥, 구, 3D 메쉬 파일 등)과 색상을 정의합니다.


* **`<collision>`**: 물리 엔진이 충돌을 감지하는 가상의 충돌 영역을 정의합니다.
* **`<inertial>`**: 질량(mass)과 관성 모멘트(inertia)를 정의하여 실제 물리 법칙이 적용되게 합니다.



### 2) 조인트 (Joint)

부모 링크(Parent)와 자식 링크(Child)를 연결하여 **어떻게 움직일지 관절의 특성을 정의**합니다. 조인트의 위치(`origin`)는 부모 링크의 중심 좌표계를 기준으로 결정됩니다.

* **관절 타입 (`type`)**:
* `fixed`: 움직이지 않고 완전히 고정된 관절.


* `continuous`: 축을 중심으로 제한 없이 무한 회전하는 관절 (예: 바퀴).


* `revolute`: 최소/최대 각도 제한이 있는 회전 관절 (예: 로봇 팔).
* `prismatic`: 선형 직선 운동을 하는 슬라이딩 관절.


* **`<axis>`**: 관절이 회전하거나 움직이는 기준 축을 지정합니다.



---


### 1) URDF 소스 코드



```xml
<?xml version="1.0"?>
<robot name="materials">

  <material name="blue">
    <color rgba="0 0 0.8 1"/>
  </material>

  <material name="white">
    <color rgba="1 1 1 1"/>
  </material>
  
  <material name="black">
    <color rgba="0 0 0 1"/>
  </material>

  <link name="base_link">
    <visual>
      <geometry>
        <cylinder length="1.0" radius="0.4"/>
      </geometry>
      <origin xyz="0 0 0.1" rpy="0 1.570796 0"/>
      <material name="white"/>
    </visual>
    <inertial>
      <mass value="10"/>
      <inertia ixx="1e-3" ixy="0.0" ixz="0.0" iyy="1e-3" iyz="0.0" izz="1e-3"/>
    </inertial>
  </link>
    
  <link name="right_wheel">
    <visual>
      <geometry>
        <cylinder length="0.1" radius="0.5"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <material name="black"/>
    </visual>
    <inertial>
      <mass value="1"/>
      <inertia ixx="1e-3" ixy="0.0" ixz="0.0" iyy="1e-3" iyz="0.0" izz="1e-3"/>
    </inertial>
  </link>

  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder length="0.1" radius="0.5"/>
      </geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <material name="black"/>
    </visual>
    <inertial>
      <mass value="1"/>
      <inertia ixx="1e-3" ixy="0.0" ixz="0.0" iyy="1e-3" iyz="0.0" izz="1e-3"/>
    </inertial>
  </link>

  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 0.5 0" rpy="1.570796 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 -0.5 0" rpy="-1.570796 0 0"/>
    <axis xyz="0 0 -1"/>
  </joint>
</robot>

```




---

---


## 1. Xacro (XML Macros) 개념 및 용도

Xacro는 순수 URDF의 가독성 저하와 코드 중복 문제를 해결하기 위해 도입된 마크로 변환 도구(프로그래밍 확장판)입니다.

### 1) Xacro의 주요 용도와 특징

* **변수 사용 (`<xacro:property>`)**: 상수 값을 상단에 한 번만 선언하고 코드 전체에서 재사용할 수 있어 치수 변경이 쉽습니다.


* **매크로 함수 (`<xacro:macro>`)**: 반복되는 부품(바퀴, 다리 등)을 함수처럼 묶어서 컴팩트하게 생성할 수 있습니다.


* **수학 연산 가능**: `${width + body_high}`와 같은 사칙연산을 코드 내부에서 직접 수행할 수 있습니다.



---


### 1) Xacro 소스 코드



```xml
<?xml version="1.0"?>
<robot name="materials" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- 변수 선언 영역 -->
  <xacro:property name="width" value="0.4" />       <!-- 로봇 몸통 반지름 -->
  <xacro:property name="length" value="1.0" />      <!-- 로봇 몸통 길이 -->
  <xacro:property name="wheel_length" value="0.1" /> <!-- 바퀴 두께 -->
  <xacro:property name="body_high" value="0.1" />    <!-- 바퀴 위치 오프셋 치수 -->
  <xacro:property name="wheelrad" value="${body_high+width}" />  <!-- 바퀴 반지름 자동 연산 -->

  <material name="blue"><color rgba="0 0 0.8 1"/></material>
  <material name="white"><color rgba="1 1 1 1"/></material>
  <material name="black"><color rgba="0 0 0 1"/></material>

  <!-- 매크로: 공통 관성 데이터 정의 -->
  <xacro:macro name="default_inertial" params="mass">
    <inertial>
      <mass value="${mass}" />
      <inertia ixx="1e-3" ixy="0.0" ixz="0.0" iyy="1e-3" iyz="0.0" izz="1e-3" />
    </inertial>
  </xacro:macro>

  <!-- 매크로: 바퀴 관절 정의 (좌우 대칭 연산 포함) -->
  <xacro:macro name="wheel" params="prefix reflect">
    <joint name="${prefix}_wheel_joint" type="continuous">
      <axis xyz="0 0 ${reflect*1}"/>
      <parent link="base_link"/>  
      <child link="${prefix}_wheel"/> 
      <!-- reflect 변수 값(1 또는 -1)을 활용해 방향과 위치를 수학적으로 자동 배치 -->
      <origin xyz="0 ${reflect*(body_high+width)} 0" rpy="${reflect*1.570796} 0 0"/>
    </joint>
  </xacro:macro>

  <!-- 몸통 링크 생성 -->
  <link name="base_link">
    <visual>
      <geometry><cylinder length="${length}" radius="${width}"/></geometry>
      <origin xyz="0 0 ${body_high}" rpy="0 1.570796 0"/>
      <material name="white"/>
    </visual>
    <xacro:default_inertial mass="10"/>
  </link>
    
  <!-- 오른쪽 바퀴 링크 생성 -->
  <link name="right_wheel">
    <visual>
      <geometry><cylinder length="${wheel_length}" radius="${wheelrad}"/></geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <material name="black"/>
    </visual>
    <xacro:default_inertial mass="1"/>
  </link>

  <!-- 왼쪽 바퀴 링크 생성 -->
  <link name="left_wheel">
    <visual>
      <geometry><cylinder length="${wheel_length}" radius="${wheelrad}"/></geometry>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <material name="black"/>
    </visual>
    <xacro:default_inertial mass="1"/>
  </link>

  <!-- 매크로 함수 호출: 4줄이 넘어갈 관절 코드를 단 2줄로 압축 조립 -->
  <xacro:wheel prefix="right" reflect="1"/>
  <xacro:wheel prefix="left" reflect="-1"/>
</robot>

```
