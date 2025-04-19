import os
import glob

def merge_python_files(output_file="merged_code.txt"):
    """
    지정된 디렉토리에서 Python 파일을 읽어서 하나의 파일로 병합합니다.
    제외 폴더: dist, build, logs
    제외 파일: __init__.py
    포함 파일: main.py, core/*.py, ui/*.py, utils/*.py
    """
    # 제외할 디렉토리 및 파일
    exclude_dirs = ["dist", "build", "logs"]
    exclude_files = ["__init__.py"]
    
    # 결과를 저장할 파일 생성
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # main.py 파일 추가
        if os.path.exists("main.py"):
            outfile.write("# ========== main.py ==========\n")
            with open("main.py", 'r', encoding='utf-8') as f:
                outfile.write(f.read())
            outfile.write("\n\n")
        
        # 코어 디렉토리의 Python 파일
        process_directory("core", outfile, exclude_dirs, exclude_files)
        
        # UI 디렉토리의 Python 파일
        process_directory("ui", outfile, exclude_dirs, exclude_files)
        
        # 유틸리티 디렉토리의 Python 파일
        process_directory("utils", outfile, exclude_dirs, exclude_files)
    
    print(f"모든 코드가 {output_file} 파일로 병합되었습니다.")

def process_directory(directory, outfile, exclude_dirs, exclude_files):
    """
    지정된 디렉토리의 Python 파일을 처리합니다.
    """
    if not os.path.exists(directory) or directory in exclude_dirs:
        return
    
    # 디렉토리 내의 모든 Python 파일 찾기
    py_files = glob.glob(f"{directory}/*.py")
    
    for file_path in py_files:
        file_name = os.path.basename(file_path)
        
        # 제외할 파일인지 확인
        if file_name in exclude_files:
            continue
        
        # 파일 내용 추가
        outfile.write(f"# ========== {directory}/{file_name} ==========\n")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                outfile.write(f.read())
            outfile.write("\n\n")
        except Exception as e:
            outfile.write(f"# 파일 읽기 오류: {str(e)}\n\n")

if __name__ == "__main__":
    merge_python_files()
    print("작업이 완료되었습니다.")