#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from datetime import datetime
import traceback
import sys

class Logger:
    """
    애플리케이션의 로깅을 관리하는 클래스
    """
    def __init__(self):
        self.logger = None
        self.log_file = None
        self.start_time = None
        self.setup_logger()
    
    def setup_logger(self):
        """
        로거 설정 초기화
        """
        # 현재 시간 기록
        self.start_time = datetime.now()
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # 로그 디렉토리 생성
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 로그 파일 경로 설정
        self.log_file = os.path.join(log_dir, f"logs_{timestamp}.txt")
        
        # 로거 설정
        self.logger = logging.getLogger("macro_app")
        self.logger.setLevel(logging.DEBUG)
        
        # 파일 핸들러 설정
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 포맷터 설정
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 핸들러 추가
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 시작 로그 메시지
        self.logger.info("=== 매크로 애플리케이션 시작 ===")
        self.logger.info(f"시작 시간: {self.start_time}")
        self.logger.info(f"로그 파일: {self.log_file}")
        
        # 시스템 정보 로깅
        self.log_system_info()
        
        # 예외 처리 핸들러 설정
        sys.excepthook = self.handle_exception
    
    def log_system_info(self):
        """
        시스템 정보 로깅
        """
        import platform
        
        self.logger.info("=== 시스템 정보 ===")
        self.logger.info(f"OS: {platform.system()} {platform.release()}")
        self.logger.info(f"Python 버전: {platform.python_version()}")
        
        try:
            import PyQt5
            self.logger.info(f"PyQt 버전: {PyQt5.QtCore.PYQT_VERSION_STR}")
        except:
            self.logger.info("PyQt 버전 확인 실패")
        
        self.logger.info("=== 시스템 정보 종료 ===")
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """
        처리되지 않은 예외 로깅
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # 키보드 인터럽트(Ctrl+C)는 기본 핸들러 사용
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # 예외 정보 로깅
        self.logger.error("처리되지 않은 예외 발생:", exc_info=(exc_type, exc_value, exc_traceback))
    
    def debug(self, message):
        """
        디버그 메시지 로깅
        """
        if self.logger:
            self.logger.debug(message)
    
    def info(self, message):
        """
        정보 메시지 로깅
        """
        if self.logger:
            self.logger.info(message)
    
    def warning(self, message):
        """
        경고 메시지 로깅
        """
        if self.logger:
            self.logger.warning(message)
    
    def error(self, message, exc_info=None):
        """
        오류 메시지 로깅
        """
        if self.logger:
            if exc_info:
                self.logger.error(message, exc_info=exc_info)
            else:
                self.logger.error(message)
    
    def critical(self, message, exc_info=None):
        """
        심각한 오류 메시지 로깅
        """
        if self.logger:
            if exc_info:
                self.logger.critical(message, exc_info=exc_info)
            else:
                self.logger.critical(message)
    
    def log_ui_action(self, action_name, details=None):
        """
        UI 액션 로깅
        """
        message = f"UI 액션: {action_name}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_macro_action(self, action_name, details=None):
        """
        매크로 동작 로깅
        """
        message = f"매크로 동작: {action_name}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_macro_start(self):
        """
        매크로 실행 시작 로깅
        """
        self.info("=== 매크로 실행 시작 ===")
    
    def log_macro_stop(self, reason=None):
        """
        매크로 실행 중지 로깅
        """
        message = "=== 매크로 실행 중지 ==="
        if reason:
            message += f" 이유: {reason}"
        self.info(message)
    
    def log_macro_pause(self):
        """
        매크로 일시 정지 로깅
        """
        self.info("매크로 실행 일시 정지")
    
    def log_macro_resume(self):
        """
        매크로 재개 로깅
        """
        self.info("매크로 실행 재개")
    
    def log_clipboard_action(self, action_type, details=None):
        """
        클립보드 관련 동작 로깅
        """
        message = f"클립보드 액션: {action_type}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_folder_action(self, action_type, details=None):
        """
        폴더 관련 동작 로깅
        """
        message = f"폴더 액션: {action_type}"
        if details:
            message += f" - {details}"
        self.info(message)

# 싱글톤 인스턴스 생성
app_logger = Logger()