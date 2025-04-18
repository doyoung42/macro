#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow
from utils.logger import app_logger


# 실행 파일 또는 스크립트의 디렉토리를 기준으로 경로 설정
if getattr(sys, 'frozen', False):
    # PyInstaller로 생성된 실행 파일의 경우
    base_dir = sys._MEIPASS
else:
    # 일반 Python 스크립트로 실행하는 경우
    base_dir = os.path.dirname(os.path.abspath(__file__))

# sys.path에 필요한 디렉토리 추가
sys.path.insert(0, base_dir)


def main():
    """
    애플리케이션의 메인 진입점
    """
    try:
        app_logger.info("애플리케이션 초기화 중...")
        
        app = QApplication(sys.argv)
        app.setApplicationName("마우스 키보드 매크로")
        app.setWindowIcon(QIcon("resources/icon.png"))
        
        app_logger.info("메인 윈도우 생성 중...")
        # 메인 윈도우 생성
        window = MainWindow()
        window.show()
        
        app_logger.info("애플리케이션 실행 중...")
        # 애플리케이션 실행
        return_code = app.exec_()
        
        app_logger.info(f"애플리케이션 종료 (코드: {return_code})")
        return return_code
    
    except Exception as e:
        app_logger.critical("애플리케이션 실행 중 심각한 오류 발생", exc_info=True)
        raise

if __name__ == "__main__":
    sys.exit(main())