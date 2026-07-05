
---

# 📄 7_topic.md

## 1. ROS 2 토픽(Topic) 개념 및 `demo_nodes_cpp` 기반 시각화 분석

### 1.1 토픽의 정의 및 연결의 방향성

* **개념:** ROS 2에서 노드 간에 데이터를 주고받는 가장 기본적인 **단방향 비동기식 통신 메커니즘**입니다.


* **방향성:** 데이터를 발행하는 게시자(Publisher)에서 데이터를 수신하는 **구독자(Subscription)** 방향으로만 데이터가 흐르는 일방통행 구조를 가집니다. `rqt_graph` 상에서 모드를 `Nodes/Topics (active)`로 변경하면 타원형의 `/talker` 노드에서 시작된 화살표가 사각형의 `/chatter` 토픽을 거쳐 오른쪽의 `/listener` 노드로 단방향 유입되는 것을 육안으로 확인할 수 있습니다.



---

## 2. ROS 2 토픽 CLI 명령어 기능 및 실행 결과 수록

`talker`와 `listener`가 정상 통신 중인 상태에서 별도의 터미널을 통해 유입 데이터를 가로채고 진단한 표준 결과 파일입니다.

### 2.1 `ros2 topic list`

현재 ROS 2 네트워크 환경에서 개설되어 활성화된 모든 토픽의 식별자 목록을 출력합니다.

```text
/chatter
/parameter_events
/rosout

```

### 2.2 `ros2 topic info /chatter`

해당 토픽의 메시지 인터페이스 타입과, 현재 이 채널에 결합된 송수신 노드의 연결 개수를 진단합니다.

```text
Type: std_msgs/msg/String
Publisher count: 1
Subscription count: 1

```

### 2.3 `ros2 topic echo /chatter`

네트워크 버스를 통과하고 있는 메시지의 실제 내용(raw data)을 터미널에 실시간으로 출력합니다.

```text
data: "Hello World: 1"
---
data: "Hello World: 2"
---

```

---

## 3. ROS 2 기본 메시지(Message) 유형 조사

토픽 인터페이스 명세에서 확인된 `std_msgs/msg/String`은 ROS 2의 표준 내장 패키지인 `std_msgs`에 정의된 데이터 구조입니다. 대표적인 프리미티브(Primitive) 메시지 유형은 다음과 같습니다.

| 메시지 타입 명칭 | 데이터 구조 및 용도 |
| --- | --- |
| `std_msgs/msg/Bool` | 논리형 데이터 (`True` 또는 `False`) 전송

 |
| `std_msgs/msg/Int32` / `Int64` | 32비트 / 64비트 부호 있는 정수형 데이터 구조

 |
| `std_msgs/msg/Float32` / `Float64` | 센서나 정밀 연산에 사용되는 부동 소수점 실수형 데이터

 |
| `std_msgs/msg/String` | 일반 텍스트 문자열 데이터 송수신

 |
| `geometry_msgs/msg/Twist` | 로봇 공학의 이동 제어 표준 메시지. 선속도(Linear) 및 각속도(Angular) 3차원 벡터 구조

 |

---

## 4. 토픽 다자간 통신(1:N, N:1, N:M) 실험 데이터 및 기술적 의미

터미널을 추가하여 노드의 구동 개수를 인위적으로 변동시켰을 때, `ros2 topic info /chatter` 명령어가 검출한 가변 데이터 링크 결과입니다.

### 4.1 상황별 게시자(Publisher) 및 구독자(Subscription) 수 변화

1. **Talker 1개, Listener 2개 구동 상황**
```text
Type: std_msgs/msg/String
Publisher count: 1
Subscription count: 2

```


2. **Talker 2개, Listener 1개 구동 상황**
```text
Type: std_msgs/msg/String
Publisher count: 2
Subscription count: 1

```


3. **Talker 2개, Listener 2개 구동 상황**
```text
Type: std_msgs/msg/String
Publisher count: 2
Subscription count: 2

```



### 4.2 다자간 통신 구조가 가지는 구조적 의의

토픽 통신은 익명성(Anonymity)과 느슨한 결합(Loose Coupling)을 극대화한 네트워크 아키텍처입니다. 발행자는 수신자가 누구인지 전혀 모른 채 채널에 메시지를 던지기만 하며, 구독자 역시 송신 노드의 상태와 무관하게 토픽 이름만 일치하면 유입되는 모든 데이터를 받아 처리합니다. 이 덕분에 시스템 확장 시 기존 코드를 수정하지 않고 새 노드를 유연하게 연동할 수 있습니다.

---

## 5. `turtlesim` 패키지를 이용한 멀티 노드 토픽 통신 정밀 분석


### 5.1 `/turtle1/cmd_vel` 토픽 정보 상세 명세

#### ① 게시자와 구독자의 수

```text
Type: geometry_msgs/msg/Twist
Publisher count: 1       # (키보드 조종기 노드: turtle_teleop_key)
Subscription count: 2    # (두 개의 시뮬레이터 노드)

```

#### ② 토픽 형태의 정보 (인터페이스 타입)

* **메시지 타입:** `geometry_msgs/msg/Twist`

* **세부 구조:** 3차원 공간상의 병진 운동 속도를 지시하는 `linear`(x, y, z) 벡터 데이터와 회전 운동 속도를 지시하는 `angular`(x, y, z) 벡터 데이터 필드로 구성되어 있습니다.



#### ③ 토픽 내용 데이터 캡처 (`ros2 topic echo /turtle1/cmd_vel`)



---

## 6. 결론: 세 개의 노드 사이에서 벌어지고 있는 일 총정리

현재 `turtlesim` 다중 노드 환경은 **1:2 (1개의 Publisher 대 2개의 Subscription) 구조의 비동기 브로드캐스팅 통신**이 완벽히 성립된 상태입니다.

1. **명령 생성:** `turtle_teleop_key` 노드는 사용자 키보드 입력을 평면 선속도 및 각속도로 변환하여 `geometry_msgs/msg/Twist` 패킷을 빌드합니다.


2. **토픽 발행:** 빌드된 메시지는 네트워크 버스의 `/turtle1/cmd_vel`이라는 하나의 공용 식별자 채널로 전송(Publish)됩니다.


3. **비동기 동시 제어:** 이 채널을 구독하며 대기 상태를 유지하던 두 개의 독립적인 시뮬레이터 노드들은, 데이터가 유입되는 순간 각자의 수신 콜백 함수를 비동기적으로 실행하여 동일한 명령어를 메모리에 적재합니다.



따라서 물리적·하드웨어적으로 완전히 격리된 두 거북이 시뮬레이터 프로세스가 **동일한 채널에서 동일한 제어 연산 값(`Twist`)을 수신하여 독립적으로 화면을 렌더링하기 때문에, 단 하나의 조종 명령만으로도 두 마리의 거북이가 한 몸처럼 기하학적 동기화 거동을 수행**하게 되는 것입니다.

---

