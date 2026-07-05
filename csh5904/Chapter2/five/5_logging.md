이전 대화에서 파일 생성 완료 메시지와 함께 들어갔던 PDF/HTML 다운로드 안내 문구를 깔끔하게 지웠다.

아래 마크다운 내용을 그대로 복사해서 `5_ros2_logging.md` 파일로 저장하면 된다.

---

# 📄 5_ros2_logging.md

## 1. rclpy 기반 ROS 2 노드 프로그래밍 구조 개요

### 1.1 `rclpy.node.Node` 클래스 상속 및 정의

ROS 2의 모든 실행 단위를 구성하는 노드(Node)는 최신 로봇 프레임워크 설계에 따라 객체 지향 방식으로 작성됩니다. 파이썬 환경에서는 `rclpy.node` 모듈의 `Node` 클래스를 상속받아 고유의 클래스를 정의합니다.

* 클래스의 생성자(`__init__`) 내부에서 부모 클래스의 생성자 `super().__init__('노드명')`을 명시적으로 호출해야만 ROS 2 그래프 상에 노드가 공식 등록됩니다.



### 1.2 노드 객체 생성 및 핵심 라이프사이클 함수 (`init`, `spin`, `shutdown`)

파이썬 스크립트가 실행될 때, ROS 2 노드를 메모리에 적재하고 구동하기 위해 아래의 핵심 라이브러리 함수가 사용됩니다.

* **`rclpy.init(args=None)`:** 현재 프로세스의 ROS 2 파이썬 통신 시스템(RMW)을 초기화합니다. 노드를 생성하기 전 반드시 최우선으로 실행되어야 합니다.


* **`rclpy.spin(node)`:** 인자로 전달된 노드 객체를 무한 루프 상태로 실행시킵니다. 노드가 꺼지지 않고 활성화되어 타이머 이벤트, 토픽 메시지 수신(Callback), 서비스 요청 등을 지속적으로 처리할 수 있도록 스레드를 대기 상태로 유지합니다.


* **`rclpy.shutdown()`:** `spin` 상태가 해제(Ctrl+C 등)되었을 때 통신 자원을 안전하게 파괴하고 시스템을 종료합니다.



---

## 2. ROS 2 로깅 시스템 및 확인 방법

### 2.1 ROS 2 노드에서 로그 남기는 방법

로봇 시스템은 디스플레이 화면이 없는 경우가 많으므로 일반 `print()` 대신 레벨별 로깅(Logging) 메서드를 사용합니다. `Node` 클래스는 자체적으로 `get_logger()` 객체를 내장하고 있어 아래와 같이 세분화된 로그를 발생시킵니다.

* `self.get_logger().debug()` : 개발 단계의 디버깅 메시지


* `self.get_logger().info()` : 시스템의 일반 정보 레포트 (기본 출력 등)


* `self.get_logger().warn()` : 주의가 필요한 경고 상황


* `self.get_logger().error()` : 오류 발생 및 오작동 알림


* `self.get_logger().fatal()` : 시스템 구동이 불가능한 치명적 결함



### 2.2 생성된 로그 확인 방법

* **터미널 콘솔 출력:** 노드가 실행 중인 터미널 창에 실시간으로 시간(Timestamp), 로그 레벨, 노드 이름과 함께 텍스트 포맷으로 즉시 출력됩니다.


* **`rqt_console` 활용:** GUI 기반 모니터링 툴인 `ros2 run rqt_console rqt_console` 명령어를 실행하면, 노드들이 뿜어내는 로그를 레벨별/노드별로 필터링하여 직관적인 그래픽 인터페이스로 검출할 수 있습니다.


* **로컬 로그 파일 시스템:** 빌드 시 자동으로 워크스페이스 루트 아래에 생성된 `~/.ros/log` 또는 `~/ros2_ws/log/` 디렉토리에 텍스트와 데이터 스트림 파일(`.log`) 형태로 날짜별로 영구 기록됩니다.



---

## 3. `logging.py` 노드 소스 코드 구현

지정된 명세(노드 실행 시 정보 수준 로그 남기기, 실행 상태 영구 유지)를 충족하는 파이썬 제어 노드 프로그램입니다.

* **파일명:** `logging.py`

* **위치:** `~/ros2_ws/src/my_robot_controller/my_robot_controller/logging.py`


```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class LoggingNode(Node):
    def __init__(self):
        # 1. 'logging_node'라는 이름으로 노드 생성 및 초기화
        super().__init__('logging_node')[cite: 1]
        
        # 2. 노드 이름을 정보(INFO) 수준의 로그로 출력
        node_name = self.get_name()[cite: 1]
        self.get_logger().info(f"노드가 성공적으로 시작되었습니다. 노드 이름: '{node_name}'")[cite: 1]

def main(args=None):
    # ROS2 통신 초기화
    rclpy.init(args=args)[cite: 1]
    
    # 노드 인스턴스 객체 생성
    node = LoggingNode()[cite: 1]
    
    try:
        # 로봇 구동 상태처럼 무한 대기하며 실행 유지
        rclpy.spin(node)[cite: 1]
    except KeyboardInterrupt:
        node.get_logger().info("사용자에 의해 노드가 안전하게 종료됩니다.")[cite: 1]
    finally:
        # 리소스 해제 및 완전 종료
        node.destroy_node()[cite: 1]
        rclpy.shutdown()[cite: 1]

if __name__ == '__main__':
    main()

```

---

## 4. 빌드 및 배포 절차 설정 (setup.py 및 colcon)

### 4.1 `setup.py` 파일의 수정 및 매핑 등록

터미널에서 `ros2 run`으로 실행할 수 있도록 진입점(Entry Point)을 설정합니다. `~/ros2_ws/src/my_robot_controller/setup.py` 파일을 열고 `entry_points` 섹션을 아래와 같이 수정합니다.

```python
    entry_points={
        'console_scripts': [
            'test_node = my_robot_controller.my_robot_node:main', # 기존 예시가 있다면 유지
            'logging_node = my_robot_controller.logging:main'     # <--- 이 라인 추가!
        ],
    },

```

* **구조 해석:** `[터미널에서 호출할 실행이름] = [패키지명].[파이썬파일명]:[실행할함수명]` 구조로 연결됩니다.



### 4.2 빌드 방법 및 옵션 확장 분석 (`--symlink-install`, `--packages-select`)

워크스페이스 루트로 이동해 전용 빌드 명령어를 실행합니다. 파이썬 코드 개발 및 작업 효율화를 위해 아래 옵션들을 결합하여 빌드합니다.

```bash
$ cd ~/ros2_ws

# 방법 A: 워크스페이스 내 전체 패키지 빌드
$ colcon build --symlink-install

# 방법 B: 특정 패키지(예: my_robot_controller)만 지정해서 빌드
$ colcon build --symlink-install --packages-select my_robot_controller

```

* **`--symlink-install` 옵션의 역할:** 기본 빌드를 수행하면 파이썬 코드가 `install` 폴더로 복사됩니다. 이 경우 소스 코드를 단 한 줄만 수정해도 매번 빌드를 새로 해야 바뀐 코드가 적용됩니다. 하지만 이 옵션을 쓰면 소스 파일과 `install` 디렉토리 사이에 심볼릭 링크가 생성되어, **이후 `src` 내의 파이썬 코드를 수정하고 저장하는 즉시 재빌드 없이 변경 사항이 즉각 반영**됩니다.


* **`--packages-select [패키지명]` 옵션의 역할:** 워크스페이스 내에 패키지가 여러 개 존재할 경우, 전체를 빌드하면 시간이 오래 걸립니다. 이 옵션을 사용하면 **지정한 특정 패키지만 골라서 빌드**하므로 빌드 시간을 획기적으로 단축할 수 있습니다.

### 4.3 환경 동기화 적용 및 제어 노드 실행

새로 빌드된 결과물과 바이너리 실행 경로를 현재 실행 중인 리눅스 터미널 세션에 인식시키기 위해 `source` 명령어로 오버레이 환경 설정을 동기화합니다.

```bash
# 1. 빌드 완료 후 워크스페이스 환경 변수 로드 (동기화)
$ source ~/ros2_ws/install/setup.bash

# 2. 패키지명과 setup.py에 지정한 스크립트 실행명으로 노드 구동
$ ros2 run my_robot_controller logging_node

```

#### [실행 결과 화면 예시]

```text
[INFO] [1719941157.123456789] [logging_node]: 노드가 성공적으로 시작되었습니다. 노드 이름: 'logging_node'
^C[INFO] [1719941165.987654321] [logging_node]: 사용자에 의해 노드가 안전하게 종료됩니다.

```
