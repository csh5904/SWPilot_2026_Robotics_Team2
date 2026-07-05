
---

# 📄 8_publisher.md

## 1. 노드 간 퍼블리시(Publish) - 서브스크라이브(Subscribe) 관계

### 1.1 `turtlesim` 예제를 통한 게시와 구독 개념 정리

ROS 2의 토픽 통신은 정보를 일방적으로 보내는 쪽과 받는 쪽이 철저하게 분리되어 작동합니다.

* **`turtle_teleop_key` (게시자 / Publisher):** 사용자가 키보드를 누를 때마다 그에 맞는 속도 명령 데이터를 생성하여 `/turtle1/cmd_vel`이라는 토픽 채널에 일방적으로 쏘아 보냅니다.


* **`turtlesim_node` (구독자 / Subscription):** `/turtle1/cmd_vel` 채널을 계속 지켜보고 있다가, 명령어가 들어오는 즉시 그 값을 수신하여 화면에 거북이의 움직임으로 표현합니다.



### 1.2 토픽 유형(`geometry_msgs/msg/Twist`)과 개별 값의 의미

두 노드가 주고받는 토픽의 데이터 타입은 `geometry_msgs/msg/Twist`입니다. 이 상자 내부 구조는 3차원 공간상의 움직임을 표현하기 위해 크게 두 가지 벡터 데이터로 쪼개져 있습니다.

* **`linear` (선속도, 직진 성분):**
* `x`: 앞뒤 이동 속도 (값이 양수면 전진, 음수면 후진)
* `y`: 좌우 이동 속도 (일반적인 휠 로봇이나 거북이는 게걸음이 불가능하므로 보통 `0.0`)
* `z`: 위아래 이동 속도 (드론 같은 비행체가 아니므로 평면 로봇은 무조건 `0.0`)


* **`angular` (각속도, 회전 성분):**
* `x`: Roll (앞뒤 축 기준 회전, 일반 로봇은 `0.0`)
* `y`: Pitch (좌우 축 기준 회전, 일반 로봇은 `0.0`)
* `z`: Yaw (제자리 회전 속도, 값이 양수면 반시계 방향 회전, 음수면 시계 방향 회전)



---

## 2. 파이썬 기반 ROS 2 퍼블리셔 작성법 및 소스 코드


* **파일명:** `circle_turtle.py`
* **위치:** `~/sw_ws/src/my_robot_controller/my_robot_controller/circle_turtle.py`

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CircleTurtle(Node):
    def __init__(self):
        super().__init__('circle_turtle_node')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 1.0  
        msg.angular.z = 1.0  
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg)

def main(args=None):
    rclpy.init(args=args)
    circle_turtle_node = CircleTurtle()

    try:
        rclpy.spin(circle_turtle_node)
    except KeyboardInterrupt:
        circle_turtle_node.get_logger().info("사용자에 의해 원형 이동 노드가 안전하게 종료됩니다.")
    finally:
        circle_turtle_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()

```

---

## 3. 의존성 추가 설정 (`package.xml`)

'''xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_robot_controller</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="cdu5904@todo.todo">cdu5904</maintainer>
  <license>Apache-2.0</license>

  <depend>rclpy</depend>
  <depend>geometry_msgs</depend>
  <depend>turtlesim</depend>
  
  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
'''


### 3.1 의존성을 추가한다는 말의 의미

쉽게 말해 이 패키지를 빌드하고 실행할 때 "외부에 있는 어떤 다른 패키지나 기능 라이브러리를 빌려와서 쓸 것인가?"를 명시하는 것입니다. 스마트폰 앱을 만들 때 외부 오픈소스 라이브러리를 가져다 쓰겠다고 빌드 도구에 허락을 구하는 것과 같습니다.

### 3.2 위의 두 의존성을 추가하는 이유

* **`geometry_msgs`:** 우리가 작성한 파이썬 코드 내부에서 속도 데이터 규격인 `Twist` 클래스를 가져와 사용(`from geometry_msgs.msg import Twist`)하고 있으므로, 빌드 시스템에 이 데이터 포맷 라이브러리가 필수적으로 필요하다고 알려주기 위해 추가합니다.


* **`turtlesim`:** 원 그리기 노드가 최종적으로 제어하고 상호작용하려는 대상 시뮬레이터 노드가 `turtlesim` 패키지 소속이므로, 패키지 간의 구동 종속 관계를 명확히 구조화하기 위해 추가합니다.



---

## 4. 빌드 및 배포 세팅 (`setup.py`)

`~/sw_ws/src/my_robot_controller/setup.py` 파일을 열고 새로 만든 `circle_turtle.py`를 실행할 수 있도록 `entry_points` 섹션에 등록합니다.

```python
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
            'circle_turtle=my_robot_controller.circle_turtle:main'
        ],
    },
)

```
