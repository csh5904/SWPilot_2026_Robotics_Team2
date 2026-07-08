# 📄 6_callback.md

## 1. ROS 2 타이머 및 콜백 함수 개념 조사

### 1.1 ROS 2 타이머(Timer)의 개념 및 구동 방식

* **개념:** ROS 2 타이머는 개발자가 지정한 **특정 시간 주기(Period)마다 특정 이벤트나 함수를 반복적으로 자동 실행**해 주는 시스템 소프트웨어 기능입니다.
* **사용 이유:** 로봇 제어 시스템은 센서 데이터 처리, 모터 제어 명령 하달, 상태 모니터링 등 주기적인 반복 태스크가 필수적입니다. 무한 루프(`while True`) 내에 `time.sleep()`을 걸어 처리하면 통신이 마비되거나 CPU 자원을 비효율적으로 소모하게 되므로, ROS 2에서는 스레드를 안전하게 관리하는 전용 타이머 인터페이스를 제공합니다.


* **생성 방법:** `Node` 클래스 내부에 정의된 `create_timer(timer_period, callback_function)` 메서드를 사용하여 생성하며, 생성과 동시에 ROS 2 실행기(Executor)의 관리 스케줄러에 등록됩니다.



### 1.2 프로그래밍에서의 콜백(Callback) 함수 개념

* **정의:** 콜백 함수는 개발자가 시스템에 "이 함수 실행해 줘" 하고 직접 호출하는 것이 아니라, 특정 조건(이벤트)이 발생했을 때 시스템이 개발자가 등록해 둔 함수를 대신 호출(Call back)하는 프로그래밍 디자인 패턴입니다.
* **ROS 2에서의 역할:** ROS 2는 비동기 이벤트 기반(Event-driven) 프레임워크입니다. 타이머 시간이 도래하거나, 외부에서 토픽 메시지가 전송되어 오거나, 서비스 요청이 들어오는 등 '특정 신호'가 감지되면 시스템(실행기)이 등록된 콜백 함수를 찔러 실행시킵니다. `rclpy.spin(node)` 함수가 바로 이 콜백 함수들이 제시간에 실행될 수 있도록 터미널을 붙잡고 감시해 주는 매니저 역할을 수행하는 것입니다.



---

## 2. 1단계 : 2초 주기 기본 타이머 노드

지정된 명세(2초에 한 번씩 "2 seconds passed" 로그 기록)를 충족하는 기초 타이머 노드 소스 코드입니다.

* **파일명:** `timer_test.py`
* **위치:** `~/sw_ws/src/my_robot_controller/my_robot_controller/timer_test1.py`

```python

import rclpy
from rclpy.node import Node

class TimerTestNode(Node):
    def __init__(self):
        super().__init__('timer_node')
        
        self.timer_period = 2.0
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    def timer_callback(self):
        self.get_logger().info("2 seconds passed")

def main(args=None):
    rclpy.init(args=args)
    node = TimerTestNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("사용자에 의해 타이머 노드가 종료됩니다.")
    finally:
        node.destroy_node()
        if rclpy.ok(): 
            rclpy.shutdown()

if __name__ == '__main__':
    main()

```

---

## 3. 2단계: 멀티 타이머 변수 제어 노드

클래스 속성 변수 `counter`(초기값 0)를 두고, **2초 주기 타이머는 값을 1씩 증가**시키고, **3초 주기 타이머는 값을 1씩 감소**시키며 각각 현재 변수 상태를 출력하는 확장 코드입니다.

* **파일명:** `timer_test.py` (동일 파일 덮어쓰기 또는 교체용)
* **위치:** `~/sw_ws/src/my_robot_controller/my_robot_controller/timer_test2.py`

```python
import rclpy
from rclpy.node import Node

class MultiTimerNode(Node):
    def __init__(self):
        super().__init__('timer_node')
        
        self.counter = 0
        

        self.increase_timer = self.create_timer(2.0, self.increase_callback)
        

        self.decrease_timer = self.create_timer(3.0, self.decrease_callback)


    def increase_callback(self):
        self.counter += 1
        self.get_logger().info(f"2 seconds passed :{self.counter}")

    def decrease_callback(self):
        self.counter -= 1
        self.get_logger().info(f"3 seconds passed :{self.counter}")

def main(args=None):
    rclpy.init(args=args)
    node = MultiTimerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("사용자 요청으로 멀티 타이머 동작을 안정적으로 종료합니다.")
    finally:
        node.destroy_node()
        if rclpy.ok():  # 런타임 context 강제셧다운 추적 에러 방지 방어 코드
            rclpy.shutdown()

if __name__ == '__main__':
    main()

```

## 4.setup.py
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
            'timer_node2=my_robot_controller.timer_test2:main'
        ],
    },
)

```




