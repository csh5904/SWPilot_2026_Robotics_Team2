
---

## 1. ROS 2 서비스(Service)와 서버-클라이언트 구조

ROS 2의 서비스(Service)는 **동기식(Synchronous) 또는 비동기식(Asynchronous) 양방향 통신** 방식입니다. 일방적으로 데이터를 발행하는 토픽(Topic)과 달리, **요청(Request)과 응답(Response)** 구조로 동작합니다.

* **서버 (Server):** 특정 서비스를 제공하며, 클라이언트의 요청이 들어올 때까지 대기합니다. 요청이 오면 지정된 콜백 함수를 실행하여 결과를 계산하고 응답을 보냅니다.
* **클라이언트 (Client):** 필요한 시점에 서버에 요청을 보냅니다. 응답이 올 때까지 기다리거나(동기), 다른 작업을 수행하며 기다립니다(비동기).

> **💡 쉽게 이해하기 (웹 구조와의 비교)**
> 웹 브라우저(클라이언트)가 URL 주소로 네이버 서버(서버)에 페이지를 요청하면, 네이버 서버가 화면 데이터를 응답하는 구조와 완벽히 동일합니다.

---

## 2. CLI(명령행)를 이용한 서비스 확인 및 실행 (add_two_ints_server 예제)

### ① 서비스 서버 노드 실행

먼저 터미널을 열고 `demo_nodes_cpp` 패키지의 정수 2개를 더해주는 서버 노드를 실행합니다.

```bash
ros2 run demo_nodes_cpp add_two_ints_server

```

### ② 서비스 목록 확인

새 터미널을 열고 현재 활성화된 서비스 목록을 확인합니다.

```bash
ros2 service list

```

* 출력 결과 중 `/add_two_ints`라는 서비스가 보일 것입니다.

### ③ 서비스 타입(정보) 확인

해당 서비스가 어떤 데이터 구조(요청/응답 변수)를 사용하는지 타입을 확인합니다.

```bash
ros2 service type /add_two_ints

```

* 출력: `example_interfaces/srv/AddTwoInts`

해당 인터페이스의 실제 내부 구조(변수명)를 확인하려면 아래 명령어를 씁니다.

```bash
ros2 interface show example_interfaces/srv/AddTwoInts

```

* 출력 구조:
```text
int64 a
int64 b
---
int64 sum

```


(`---`를 기준으로 윗부분은 **요청(Request)**, 아랫부분은 **응답(Response)** 데이터입니다.)

### ④ 명령행에서 서비스 호출 (Call)

`a=10`, `b=20`을 더하도록 서버에 직접 요청을 보냅니다. 데이터는 YAML 형식으로 작성합니다.

```bash
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 10, b: 20}"

```

* **결과 반환:** `response: example_interfaces.srv.AddTwoInts_Response(sum=30)` 메시지가 출력됩니다.

---

## 3. 프로그램의 정상 종료 및 예외 처리 (Clean Shutdown)

ROS 2 프로그램(특히 파이썬)을 처리되지 않은 예외(Uncaught Exception) 없이 정상적으로 종료하려면 `KeyboardInterrupt` (Ctrl+C) 예외를 안전하게 잡아내고 리소스를 해제해야 합니다.

* **해결 방법:** 코드 전체를 `try-except` 블록으로 감싸고, `finally` 구문에서 노드를 명시적으로 파괴(`destroy_node()`)한 뒤 ROS 2 컨텍스트를 종료(`shutdown()`)합니다. 이렇게 하면 터미널 창에 붉은색 에러 로그가 도배되는 것을 막을 수 있습니다.

---

## 4. 파이썬 비동기(Asynchronous) 처리 방식의 필요성

ROS 2에서 클라이언트가 서버에 서비스를 요청할 때 동기식(Synchronous)으로 기다리면(`call()`), 응답이 올 때까지 전체 노드의 스레드가 블로킹(멈춤)됩니다. 만약 같은 노드 내에서 토픽을 발행(Publish)하거나 타이머 콜백을 돌리고 있었다면, 서비스 응답을 받을 때까지 그 모든 동작이 마비됩니다.

이를 방지하기 위해 ROS 2 파이썬(`rclpy`)에서는 비동기식 호출(`call_async()`)을 사용합니다.

* `call_async()`는 즉시 `Future` 객체를 반환하며 스레드를 차단하지 않습니다.
* `Future` 객체에 "응답이 오면 실행할 콜백 함수"를 등록하여, 응답이 도착한 순간 다른 코드를 방해하지 않고 부드럽게 결과를 처리합니다.

---

## 5. ROS 2 파이썬 서비스 서버 / 클라이언트 예제 코드

`example_interfaces/srv/AddTwoInts` 서비스를 사용하는 완벽한 서버와 클라이언트 예제 코드입니다. 각 핵심 함수의 역할과 매개변수를 주석으로 상세히 풀어냈습니다.

### 🏢 서비스 서버 (Service Server)

```python
import rclpy
from rclpy.node import Node
# 두 정수를 입력받아 합을 반환하는 서비스 인터페이스 임포트
from example_interfaces.srv import AddTwoInts 

class MinimalServiceServer(Node):

    def __init__(self):
        # Node 클래스의 생성자를 호출하여 노드 이름을 'service_server_node'로 설정
        super().__init__('service_server_node')
        
        # 💡 create_service(서비스_타입, '서비스_이름', 콜백_함수)
        # 클라이언트로부터 요청이 들어오면 지정된 콜백 함수가 자동으로 실행됩니다.
        self.srv = self.create_service(
            AddTwoInts, 
            'add_two_ints', 
            self.add_two_ints_callback
        )
        self.get_logger().info('정수 덧셈 서비스 서버가 준비되었습니다.')

    def add_two_ints_callback(self, request, response):
        """
        클라이언트의 요청을 처리하는 콜백 함수
        :param request: 클라이언트가 보낸 요청 데이터 (a, b 변수 포함)
        :param response: 클라이언트에게 돌려줄 응답 데이터 (sum 변수 포함)
        """
        # 요청받은 두 정수를 더해 응답 객체에 저장
        response.sum = request.a + request.b
        
        # 터미널에 수신 및 연산 로그 출력
        self.get_logger().info(f'요청 수신: a = {request.a}, b = {request.b}')
        self.get_logger().info(f'응답 송신: sum = {response.sum}')
        
        # 구성된 응답 객체를 반드시 반환해야 함
        return response

def main(args=None):
    # ROS 2 통신을 위한 초기화
    rclpy.init(args=args)
    
    # 서버 노드 생성
    service_server = MinimalServiceServer()

    try:
        # 💡 rclpy.spin(): 노드를 활성화 상태로 유지하며 콜백(요청 수신)을 대기 및 처리
        rclpy.spin(service_server)
    except KeyboardInterrupt:
        # Ctrl+C 입력 시 예외를 잡아내어 깔끔하게 종료 프로세스로 진입
        service_server.get_logger().info('사용자에 의해 노드가 종료됩니다.')
    finally:
        # 💡 destroy_node(): 노드가 사용하던 메모리와 자원을 시스템에 반환
        service_server.destroy_node()
        # 💡 shutdown(): ROS 2 클라이언트 라이브러리 컨텍스트를 안전하게 공식 종료
        rclpy.shutdown()

if __name__ == '__main__':
    main()

```

---

### 💻 서비스 클라이언트 (Service Client - 비동기 방식)

```python
import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class MinimalServiceClient(Node):

    def __init__(self):
        # 노드 이름을 'service_client_node'로 설정
        super().__init__('service_client_node')
        
        # 💡 create_client(서비스_타입, '서비스_이름')
        # 호출하고자 하는 서버의 서비스 이름 및 타입과 일치해야 합니다.
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        
        # 💡 wait_for_service(timeout_sec): 서비스 서버가 네트워크에 나타날 때까지 대기
        # 서버가 켜지지 않았다면 1초 간격으로 체크하며 켜질 때까지 루프를 돕니다.
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('서비스 서버가 아직 활성화되지 않았습니다. 대기 중...')
            
        # 요청에 사용할 데이터 구조체(인스턴스) 생성
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        """요청을 생성하고 서버에 비동기식으로 전달하는 함수"""
        self.req.a = a
        self.req.b = b
        
        # 💡 call_async(요청_데이터): 서비스를 비동기적으로 호출하고 Future 객체를 즉시 반환
        # 이 함수는 서버가 응답을 줄 때까지 코드 전체를 멈추지(blocking) 않습니다.
        self.future = self.cli.call_async(self.req)
        
        # 💡 add_done_callback(콜백_함수): Future 객체에 연산 완료 시 실행할 콜백을 연결
        # 서버로부터 응답이 수신되는 순간, 지정한 함수가 비동기적으로 실행됩니다.
        self.future.add_done_callback(self.response_callback)

    def response_callback(self, future):
        """서버로부터 응답이 성공적으로 도착했을 때 실행되는 콜백 함수"""
        try:
            # 💡 future.result(): Future 객체로부터 실제 서버가 보낸 response 결과물을 추출
            response = future.result()
            self.get_logger().info(f'결과 반환 성공: {self.req.a} + {self.req.b} = {response.sum}')
        except Exception as e:
            # 서비스 호출 중 에러 발생 시 예외 처리
            self.get_logger().error(f'서비스 호출 실패: {e}')

def main(args=None):
    rclpy.init(args=args)
    
    # 클라이언트 노드 생성
    service_client = MinimalServiceClient()
    
    # 시스템 인자(Argument)로 입력된 2개의 숫자를 파싱하여 요청 보냄 (기본값: 41, 1)
    a = int(sys.argv[1]) if len(sys.argv) > 1 else 41
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    service_client.send_request(a, b)

    try:
        # 비동기 콜백(response_callback)이 구동될 수 있도록 스핀 실행
        rclpy.spin(service_client)
    except KeyboardInterrupt:
        service_client.get_logger().info('사용자에 의해 클라이언트가 종료됩니다.')
    finally:
        # 자원 해제 및 종료
        service_client.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

```
