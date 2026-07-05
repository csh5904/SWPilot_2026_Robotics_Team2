
---

# 📄 4_ros2_package.md

## 1. ROS 2 워크스페이스 및 패키지 생성 절차

### 1.1 워크스페이스 및 소스(src) 디렉토리 생성

ROS 2 애플리케이션 개발을 위한 작업 공간(Workspace)과 소스 코드가 위치할 디렉토리를 생성합니다. 실습 시 반드시 아래의 경로명일 필요는 없으나, 일반적으로 `~/ros2_ws`를 워크스페이스 디렉토리, 그 하위의 `src`를 소스 디렉토리라고 칭합니다.

```bash
$ mkdir -p ~/ros2_ws/src
$ cd ~/ros2_ws

```

### 1.2 colcon build를 통한 최초 빌드

워크스페이스 루트 디렉토리(`~/ros2_ws`)에서 `colcon` 빌드 시스템을 사용해 빈 워크스페이스를 최초로 빌드합니다.

```bash
$ colcon build

```

* **오류 발생 시 대처:** 만약 `colcon: command not found` 에러가 발생한다면, ROS 2 환경 설정 파일 바인딩이나 colcon 설치가 누락된 것입니다. `source /opt/ros/humble/setup.bash` (Humble 버전 기준)를 통해 ROS 2 환경을 현재 터미널에 로드하거나, `sudo apt install python3-colcon-common-extensions` 명령어로 colcon 패키지를 설치한 후 다시 시도해야 합니다.

### 1.3 `my_robot_controller` 패키지 생성

파이썬 빌드 시스템과 ROS 2 파이썬 클라이언트 라이브러리 의존성을 포함하여 패키지를 생성합니다. 패키지 생성 명령은 반드시 `src` 디렉토리 내부로 이동한 뒤 수행해야 합니다.

```bash
$ cd ~/ros2_ws/src
$ ros2 pkg create my_robot_controller --build-type ament_python --dependencies rclpy

```

---

## 2. ROS 2 핵심 개념 및 빌드 시스템 조사

### 2.1 colcon 명령어 개요

* **정의:** colcon(collective construction)은 ROS 2에서 공식적으로 채택하여 사용하는 명령행 빌드 툴(Build Tool)입니다.
* **역할:** 워크스페이스 내부의 여러 패키지를 종속성에 맞추어 순서대로 빌드, 테스트, 설치해 주는 역할을 합니다. 빌드가 완료되면 워크스페이스 루트에 `build`(빌드 중간 과정 저장), `install`(실행 파일 및 스크립트 설치), `log`(빌드 로그 저장) 디렉토리가 자동으로 생성됩니다.

### 2.2 ament_python 빌드 시스템

* **정의:** ROS 2에서 파이썬 패키지를 빌드, 패키징, 배포하기 위해 사용하는 파이썬 전용 빌드 시스템입니다.
* **특징:** C++ 기반 패키지에서 사용하는 `ament_cmake`와 달리, 내부적으로 파이썬 표준 배포 도구인 `setuptools`를 기반으로 구동됩니다. 컴파일 과정 없이 스크립트 파일을 `install` 디렉토리로 복사하고 환경을 매핑하는 형태로 빌드가 수행됩니다.

### 2.3 rclpy (ROS 2 Client Library for Python)

* **정의:** ROS 2의 핵심 기능을 파이썬 API로 구현한 **파이썬용 ROS 2 클라이언트 라이브러리**입니다.
* **용도:** 파이썬 개발자가 ROS 2 환경 위에서 노드(Node)를 생성하고, 토픽(Topic) 통신을 위한 퍼블리셔/서브스크라이버를 구현하며, 서비스(Service), 액션(Action), 파라미터(Parameter) 등 ROS 2의 핵심 통신 메커니즘을 제어하는 제어 프로그램을 작성할 수 있게 돕는 핵심 API 패키지입니다.

---

## 3. 워크스페이스 구조 확인 (tree 실행 결과)

`tree` 도구를 설치하고 패키지 및 워크스페이스를 생성한 후, 루트 디렉토리에서 구조를 조회한 결과 레포트입니다.

```bash
# tree 프로그램 설치
$ sudo apt update && sudo apt install -y tree

# 워크스페이스 루트에서 구조 확인
$ tree

```

### [tree 실행 결과 구조도]

```text
.
├── build
│   └── COLCON_IGNORE
├── install
│   ├── COLCON_IGNORE
│   ├── local_setup.bash
│   ├── local_setup.ps1
│   ├── local_setup.sh
│   ├── _local_setup_util_ps1.py
│   ├── _local_setup_util_sh.py
│   ├── local_setup.zsh
│   ├── setup.bash
│   ├── setup.ps1
│   ├── setup.sh
│   └── setup.zsh
├── log
│   ├── build_2026-07-05_02-25-57
│   │   ├── events.log
│   │   └── logger_all.log
│   ├── COLCON_IGNORE
│   ├── latest -> latest_build
│   └── latest_build -> build_2026-07-05_02-25-57
└── src
    └── my_robot_controller
        ├── LICENSE
        ├── my_robot_controller
        │   └── __init__.py
        ├── package.xml
        ├── resource
        │   └── my_robot_controller
        ├── setup.cfg
        ├── setup.py
        └── test
            ├── test_copyright.py
            ├── test_flake8.py
            └── test_pep257.py

```

---

## 4. 핵심 설정 파일의 역할 및 구조 분석

### 4.1 `package.xml`

* **역할:** 패키지의 이름, 버전, 작성자 정보, 라이선스 및 **의존성(Dependency) 정보를 관리하는 XML 형식의 메타데이터 파일**입니다.
* **구성 요소 및 구조:**
* `<name>`, `<version>`, `<description>`: 패키지의 기본 식별 정보 기술.
* `<maintainer>`, `<license>`: 유지보수자 및 오픈소스 라이선스 명시.
* `<buildtool_depend>`: 빌드 시 필요한 도구 지정 (파이썬의 경우 `ament_python`).
* `<depend>` / `<exec_depend>`: 실행 및 개발 환경에 필요한 외부 ROS 2 패키지 기술 (예: `rclpy` 생성 시 추가된 종속성이 여기에 기재됨).



### 4.2 `setup.py`

* **역할:** 파이썬 `setuptools`를 이용하여 패키지의 **설치, 배포, 노드 실행 파일(Entry Point)의 실행 경로를 정의하는 빌드 설정 파일**입니다.
* **구성 요소 및 구조:**
* `data_files`: `package.xml`이나 리소스 파일들이 복사되어 설치될 시스템 경로 지정.
* `entry_points`: **가장 중요한 옵션 항목**으로, 사용자가 터미널에서 `ros2 run [패키지명] [노드명]`을 실행했을 때 실제 구동될 파이썬 스크립트의 특정 함수(주로 `main`)를 매핑하는 `console_scripts` 배열 구조로 이루어져 있습니다.



---

## 5. 💡 ROS 2 워크스페이스 압축 및 백업 방법

작업한 소스 코드와 워크스페이스 환경을 다른 PC로 옮기거나 백업할 때는, 용량만 차지하고 재빌드 시 새로 생성되는 **`build`, `install`, `log` 디렉토리를 제외하고 `src` 폴더만 깔끔하게 압축**하는 것이 정석입니다.

### 방법 1: 불필요한 디렉토리를 제외하고 tar.gz로 압축 (가장 권장)

워크스페이스 바깥 경로(`~`)로 이동한 뒤, 빌드 잔재들을 배제하고 `src` 폴더와 필수 파일만 압축 파일로 묶는 방법입니다.

```bash
$ cd ~
$ tar -czvf ros2_ws_backup.tar.gz --exclude='ros2_ws/build' --exclude='ros2_ws/install' --exclude='ros2_ws/log' ros2_ws/

```

### 방법 2: 빌드 파일 초기화 후 zip으로 압축

만약 윈도우 환경 등으로 복사하기 위해 일반 `.zip` 구조가 필요하다면, 워크스페이스 내부의 빌드 폴더를 깨끗하게 지운 뒤 전체를 압축합니다.

```bash
# 1. 워크스페이스로 이동하여 빌드/설치 디렉토리 완전 삭제 (초기화)
$ cd ~/ros2_ws
$ rm -rf build install log

# 2. 상위 디렉토리로 이동하여 zip 압축 수행
$ cd ~
$ zip -r ros2_ws_backup.zip ros2_ws/

```

*백업 파일을 복원한 컴퓨터에서는 다시 `cd ~/ros2_ws && colcon build`를 입력하면 환경에 맞게 디렉토리들이 재구성됩니다.*
