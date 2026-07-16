# 트랙형 이동 로봇 URDF v4 + Gazebo (ROS2 Humble)

2차 실측값(USB 허브, 카메라 마운트 체인, 라이다 받침, 다이나믹셀 위치, 전체 외곽 치수)과 제품 스펙(로보티즈 캐터필러/와플플레이트/휠셋, RPLIDAR A1M8, RealSense D435, XC430)을 반영한 버전입니다. 물리 구동 구조(트랙 중앙 숨김 구동륜 2개 디퍼렌셜 드라이브 + 마찰0 캐스터)는 v2/v3과 동일합니다.

## v4에서 확정된 수직 구조 (지면 기준)

2차 실측을 교차 검증한 결과, 1층 받침대는 트랙 위가 아니라 트랙 사이 바닥 가까이(밑면 지면 +2cm)에 있는 낮은 섀시 플로어입니다. 이렇게 두면 전체 높이 25cm = 천장 윗면 18cm + 라이다 받침 4.6cm + 회전부 2.4cm가 정확히 성립하고, 카메라 중심 높이도 15cm로 계산되어 기존 URDF(14.38cm)와 거의 일치합니다. 검증 수치: 천장 윗면 18.0, 라이다 받침 22.6, 라이다 꼭대기 25.0, 2층 윗면 10.0, 전장 21.1, 전폭 19.5 — 전부 실측과 일치. 총질량은 제품 스펙 기반 약 2.7kg (AGX Xavier 개발킷 630g, 보조배터리 0.5kg 추정, XC430 65g x2, A1M8 0.19kg, D435 72g, 플라스틱 플레이트류). 실물 총 무게를 재서 알려주면 비례 보정 가능. 정지 시 미끄러짐은 max_wheel_acceleration 1.5→10.0으로 수정되어 실물처럼 즉시 정지함.

받침대들은 후방 트랙 끝~카메라 앞면 21cm 실측으로 역산해 앞으로 1.5cm 시프트되어 있습니다. 카메라는 볼마운트(지름 2.5cm, 2층 앞끝에서 0.5cm 뒤) 위 지면 15cm, 앞으로 0.314rad 기울어짐 — 이 값은 실측 체인과 기존 URDF가 서로 교차 검증됩니다. 뒷바퀴가 XC430 구동, 앞바퀴는 아이들러이며 모터 2개가 시각으로 표현됩니다.

## 실행

```bash
killall -9 gzserver gzclient   # 좀비 서버 정리 (중요)
cp -r tracked_robot ~/sw_ws/src/   # 기존 폴더 교체
cd ~/sw_ws
rm -rf build/tracked_robot install/tracked_robot
colcon build --packages-select tracked_robot
source install/setup.bash
ros2 launch tracked_robot gazebo.launch.py
```

새 터미널에서 `ros2 run teleop_twist_keyboard teleop_twist_keyboard` 실행 후 i/j/l/k로 조종.

**주행 안 될 때 체크**: (1) Gazebo 하단 Real Time Factor가 0이고 ▶ 버튼이 보이면 일시정지 상태 → ▶ 눌러 재생. (2) teleop speed가 0.2~1.0인지 확인, 수만 단위면 teleop 재시작. (3) `Entity already exists` 에러가 뜨면 killall로 좀비 gzserver 정리 후 재실행.

토픽: /cmd_vel, /odom, /scan, /imu, /camera/image_raw, /camera/depth/image_raw

## 확인이 필요한 값 (실측 간 충돌)

README 하단 참고 — 대화에서 질문드린 값들(천장 받침대 실측 높이, 천장 세로 길이 vs 라이다 거리 합, OpenCR 상하 방향, 카메라 렌즈 지면 높이)을 확인해주시면 해당 수치만 조정하면 됩니다.
