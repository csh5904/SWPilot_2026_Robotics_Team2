
---


# ROS 2 Python 서브스크라이버 구현 및 turtlesim 인터페이스 조사

본 문서는 ROS 2(Humble) 환경에서 `turtlesim` 노드의 거북이 위치 데이터(`/turtle1/pose`)를 조사하고, 이를 파이썬 기반의 서브스크라이버 노드로 구현하는 과정을 담고 있습니다.

---

## 1. 파이썬 기반 ROS 2 서브스크라이버 구현 메커니즘
ROS 2에서 파이썬(`rclpy`)을 사용하여 토픽을 구독(Subscribe)하는 노드를 만들 때는 다음과 같은 객체지향적 구조를 따릅니다.

1. **`rclpy.node.Node` 상속:** 사용자 정의 클래스를 만들어 ROS 2 노드의 기능을 확장합니다.
2. **`create_subscription()` 호출:** 클래스의 생성자(`__init__`) 내부에서 서브스크라이버 객체를 생성합니다. 이때 필요한 4대 요소는 다음과 같습니다.
   * **인터페이스 타입(Message Type):** 구독할 토픽의 데이터 종류
   * **토픽 이름(Topic Name):** 구독 대상 토픽 경로 (예: `/turtle1/pose`)
   * **콜백 함수(Callback Function):** 메시지가 수신될 때마다 실행할 메서드
   * **QoS Depth (큐 사이즈):** 데이터가 밀릴 때 버퍼에 보관할 최대 메시지 개수
3. **콜백 함수 정의:** 수신된 메시지 객체를 파라미터로 받아 원하는 로직(출력, 제어 등)을 처리합니다.
4. **`rclpy.spin()` 실행:** 노드가 종료되지 않고 계속해서 들어오는 메시지를 대기(이벤트 루프)하도록 만듭니다.


## 2. turtlesim 토픽 목록 및 `/turtle1/pose` 조사

터틀심 노드(`ros2 run turtlesim turtlesim_node`)를 실행한 상태에서 토픽 환경을 조사합니다.

### ① 토픽 목록 확인
현재 활성화된 전체 토픽 리스트를 출력합니다.
```bash
ros2 topic list

```

**출력 결과:**

```text
/parameter_events
/rosout
/turtle1/cmd_vel
/turtle1/color_sensor
/turtle1/pose

```

### ② `/turtle1/pose` 토픽 정보 및 메시지 유형 확인

해당 토픽이 어떤 형태의 데이터(인터페이스)를 사용하는지 정보를 조회합니다.

```bash
ros2 topic info /turtle1/pose

```

**출력 결과:**

```text
Type: turtlesim/msg/Pose
Publisher count: 1
Subscription count: 0

```

* 해당 토픽의 메시지 유형(Type)은 **`turtlesim/msg/Pose`** 임을 확인할 수 있습니다.

---

## 3. `ros2 interface show` 명령 및 메시지 구성 확인

### ① `ros2 interface show` 명령어 조사

* **정의:** ROS 2 시스템 내에 정의된 메시지(`msg`), 서비스(`srv`), 액션(`action`) 등의 인터페이스 구조(내부 데이터 타입과 변수명)를 터미널에 시각적으로 보여주는 명령어입니다.
* **사용 문법:** `ros2 interface show <패키지명>/<인터페이스종류>/<타입이름>`

### ② `/turtle1/pose` 메시지 구성 확인

위에서 알아낸 `turtlesim/msg/Pose` 타입을 통해 데이터 필드를 조회합니다.

```bash
ros2 interface show turtlesim/msg/Pose

```

**출력 결과:**

```text
float32 x
float32 y
float32 theta
float32 linear_velocity
float32 angular_velocity

```

* **구조 분석:** 거북이의 위치 정보를 나타내는 $x, y$ 좌표, 회전 방향($\theta$), 그리고 현재 움직이는 선속도(linear)와 각속도(angular)가 모두 32비트 부동소수점(`float32`) 형태로 구성되어 있습니다.

---

## 4. `turtle_pose.py` 파이썬 서브스크라이버 구현

위의 조사 내용을 바탕으로 거북이의 위치 정보를 실시간으로 구독하여 터미널에 정밀하게 출력하는 소스코드입니다.

```python
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

class TurtlePoseNode(Node):
    def __init__(self):
        super().__init__('turtle_pose_node')
        self.subscription = self.create_subscription(
            Pose,
            'turtle1/pose',
            self.pose_callback,
            10
        )
        self.subscription  # prevent unused variable warning

    def pose_callback(self, msg):
        self.get_logger().info(f"Turtle Pose - x: {msg.x}, y: {msg.y}, theta: {msg.theta}")

def main(args=None):
    rclpy.init(args=args)
    turtle_pose_node = TurtlePoseNode()

    try:
        rclpy.spin(turtle_pose_node)
    except KeyboardInterrupt:
        turtle_pose_node.get_logger().info("사용자에 의해 거북이 위치 노드가 안전하게 종료됩니다.")
    finally:
        turtle_pose_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    
if __name__ == '__main__':
    main()

```

```

```
