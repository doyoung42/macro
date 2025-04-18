# 마우스 키보드 매크로 프로그램 (Windows)

Windows 환경에서 PyQt6로 개발된 마우스/키보드 자동화 매크로 프로그램입니다.

## 설치 방법 (Windows)

```bash
# Conda 환경 생성
conda env create -f env.yml

# 환경 활성화
conda activate macro-env

# 프로그램 실행
python main.py
```

## 실행 파일 컴파일 방법

```bash
# PyInstaller 설치 (이미 설치되어 있다면 생략)
conda activate macro-env
pip install pyinstaller

# 실행 파일 컴파일 (이미 main.spec 파일이 있는 경우)
pyinstaller main.spec --clean
```

컴파일 완료 후 `dist` 폴더에 실행 파일이 생성됩니다.

## 주요 기능

- 마우스 이동, 클릭, 드래그 & 드롭
- 키보드 텍스트 입력 및 키 조합 입력
- 텍스트 리스트 순차 입력
- 클립보드 내용 자동 저장
- 새 폴더 감지 및 클립보드 내용 저장
- 매크로 동작 편집 및 순서 조정
- 반복 실행 및 무한 반복 옵션