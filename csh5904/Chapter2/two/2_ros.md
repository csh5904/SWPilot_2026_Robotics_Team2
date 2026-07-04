요청하신 내용을 과제나 문서(Markdown)로 제출하시기 좋게 구조화하여 깔끔하게 정리해 드립니다. 아래 내용을 복사해서 `.md` 파일로 저장하여 사용하시면 됩니다.

---

# 📄 2_1_ros2_basics.md

## 1. 로봇 운영체제(ROS)의 개념

* **정의:** 로봇 운영체제(Robot Operating System, ROS)는 전통적인 의미의 하드웨어 제어용 운영체제(Windows, Linux 등)라기보다는, 기존 운영체제 위에서 작동하는 **로봇 전용 미들웨어(Middleware)이자 소프트웨어 프레임워크**입니다.
* **목적:** 로봇 개발에 필요한 하드웨어 추상화, 하위 디바이스 제어, 로봇 프로세스(노드) 간의 메시지 패싱, 패키지 관리, 개발 환경 도구(시각화, 디버깅 등)를 종합적으로 제공하여 로봇 소프트웨어의 재사용성을 극대화하는 것을 목적으로 합니다.

---

## 2. 운영체제 사용 유무에 따른 로봇의 차이

| 구분 | 운영체제(ROS 등)를 사용하는 로봇 | 운영체제(ROS)를 사용하지 않는 로봇 |
| --- | --- | --- |
| **제어 방식** | 고성능 프로세서(AP, 싱글보드 컴퓨터) 위에서 프로세스 단위로 분산 제어 | 마이크로컨트롤러(MCU, 예: Arduino, AVR 등) 기반의 펌웨어(Firmware) 제어 |
| **소프트웨어 구조** | 여러 개의 독립된 프로그램(노드)이 실시간으로 메시지를 주고받으며 유기적으로 작동 | 하나의 커다란 메인 루프(`while(1)`) 안에서 센서 입력과 모터 출력이 순차적으로 처리됨 |
| **확장성 및 재사용성** | 이미 검증된 내비게이션(Nav2), 시각 센서 처리(OpenCV) 등의 패키지를 쉽게 가져다 쓸 수 있어 확장성이 매우 높음 | 새로운 센서나 기능을 추가하려면 하드웨어 의존적인 코드를 일일이 수정하고 다시 빌드해야 하므로 재사용성이 낮음 |
| **주요 활용 분야** | 자율주행 로봇(AMR), 서비스 로봇, 매니퓰레이터, 드론 등 고차원 연산이 필요한 로봇 | 청소기, 단순 라인트레이서, 공장 내 단순 반복 자동화 기기 등 단일 목적의 임베디드 시스템 |

---

## 3. 우분투 리눅스(Ubuntu 22.04)에 ROS2 Humble 설치 방법

ROS2 Humble Hawksbill은 Ubuntu 22.04 LTS 버전에 최적화되어 있습니다. 데스크톱 풀 버전(Desktop Install) 설치 기준 절차는 다음과 같습니다.

### Step 1: 로케일(Locale) 설정 (UTF-8 환경 설정)

```bash
sudo apt update && sudo apt install locales
sudo locale-gen ko_KR ko_KR.UTF-8
sudo update-locale LC_ALL=ko_KR.UTF-8 LANG=ko_KR.UTF-8
export LANG=ko_KR.UTF-8

```

### Step 2: 우분투 Universe 저장소 추가 및 APT 키 등록

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

```

### Step 3: ROS2 저장소(Repository)를 소스 리스트에 추가

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/announces/apt/sources.list.d/ros2.list > /dev/null

```

### Step 4: ROS2 Humble 데스크톱 버전 설치

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install ros-humble-desktop -y

```

### Step 5: 환경 변수 등록 및 설정 자동화

터미널을 켤 때마다 자동으로 ROS2 환경이 로드되도록 `~/.bashrc`에 등록합니다.

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

```

---

## 4. ROS2 패키지(Package)와 노드(Node)의 관계

ROS2 아키텍처를 이해하는 가장 기본 단위로, 파일 시스템 단위와 실행 단위로 구분할 수 있습니다.

* **노드 (Node):**
* **정의:** 실제 특정 작업(센서 데이터 읽기, 모터 제어, 알고리즘 연산 등)을 수행하는 **최소 실행 단위의 프로그램**입니다.
* **특징:** 하나의 로봇 시스템은 독립적으로 작동하는 수많은 노드들의 집합으로 이루어집니다.


* **패키지 (Package):**
* **정의:** 하나 이상의 노드와 이를 실행하기 위한 설정 파일, 데이터, 빌드 규칙 등을 모아놓은 소프트웨어 컨테이너(폴더 단위)입니다.
* **특징:** ROS2 소프트웨어를 배포하고 빌드하는 기본 단위가 됩니다.


* **둘의 관계:**
* **"패키지는 노드의 가방(Container)이다."** 개발자는 코드를 관리하고 배포할 때 패키지 단위로 묶어서 관리하며, 실제 로봇 시스템이 구동될 때는 그 패키지 안에 들어있는 여러 노드들을 각각 프로세스로 실행시켜 동작시킵니다.



---

## 5. `ros2 run` 명령어의 사용법과 토커/리스너 데모

ROS2에서 특정 패키지 안에 포함된 노드를 실행할 때 사용하는 핵심 명령어가 `ros2 run`입니다.

### 명령어 기본 구조

```bash
ros2 run <패키지_이름> <노드(실행파일)_이름>

```

### Talker(토커)와 Listener(리스너) 데모 실행 예시

ROS2가 정상 설치되었는지 확인하는 가장 단순한 데이터 송수신 데모 프로그램입니다.

1. **첫 번째 터미널 (Talker 노드 실행):** 메시지를 발행(Publish)하는 노드입니다.
```bash
ros2 run demo_nodes_cpp talker

```


*실행 시 터미널에 `[INFO]: Publishing: "Hello World: 1"`과 같은 로그가 출력됩니다.*
2. **두 번째 터미널 (Listener 노드 실행):** 토커가 보낸 메시지를 수신(Subscribe)하는 노드입니다.
```bash
ros2 run demo_nodes_cpp listener

```


*실행 시 토커가 보낸 메시지를 실시간으로 받아 `[INFO]: I heard: [Hello World: 1]`과 같이 출력하는 것을 확인할 수 있습니다.*
