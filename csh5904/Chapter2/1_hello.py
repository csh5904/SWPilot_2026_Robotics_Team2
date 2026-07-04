import os

target_dir = "/test"
file_path = os.path.join("/test", "hello.txt")

try:
   
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f" {target_dir} 디렉토리를 생성했습니다.")

    with open(file_path, "w") as f:
        f.write("Hello Linux")
        
    print(f" {file_path} 파일에 'Hello Linux'를 기록했습니다.")

except PermissionError:
    print(" 권한이 없습니다! 명령어 앞에 'sudo'를 붙여서 실행했는지 확인하세요.")
