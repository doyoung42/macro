#!/usr/bin/env python
# -*- coding: utf-8 -*-
# core/clipboard_manager.py

import os
import time
import threading
import pyperclip
from PyQt5.QtCore import QObject, pyqtSignal
from utils.logger import app_logger

class ClipboardManager(QObject):
    """
    클립보드 내용을 모니터링하고 파일에 저장하는 클래스
    """
    # 상태 변화 시그널
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 클립보드 모니터링 설정
        self.output_file = ""
        self.monitoring = False
        self.thread = None
        self.last_content = ""
        
        app_logger.info("클립보드 매니저 초기화 완료")
    
    def set_output_file(self, file_path):
        """
        클립보드 내용을 저장할 파일 경로 설정
        """
        app_logger.debug(f"클립보드 저장 파일 설정: {file_path}")
        self.output_file = file_path
    
    def is_monitoring(self):
        """
        클립보드 모니터링 상태 확인
        """
        return self.monitoring
    
    def start_monitoring(self):
        """
        클립보드 모니터링 시작
        """
        if self.monitoring or not self.output_file:
            app_logger.warning("클립보드 모니터링을 시작할 수 없음: 이미 모니터링 중이거나 출력 파일이 설정되지 않음")
            return
        
        # 클립보드 초기 상태 저장
        self.last_content = pyperclip.paste()
        app_logger.debug(f"클립보드 초기 상태 저장 (길이: {len(self.last_content)})")
        
        self.monitoring = True
        
        # 모니터링 스레드 시작
        app_logger.info(f"클립보드 모니터링 시작 (출력 파일: {self.output_file})")
        self.thread = threading.Thread(target=self._monitor_clipboard)
        self.thread.daemon = True
        self.thread.start()
        
        self.status_changed.emit("클립보드 모니터링 시작됨")
    
    def stop_monitoring(self):
        """
        클립보드 모니터링 중지
        """
        if not self.monitoring:
            app_logger.debug("클립보드 모니터링이 활성화되어 있지 않음")
            return
        
        app_logger.info("클립보드 모니터링 중지")
        self.monitoring = False
        
        # 스레드 종료 대기
        if self.thread and self.thread.is_alive():
            app_logger.debug("클립보드 모니터링 스레드 종료 대기")
            self.thread.join(1.0)  # 최대 1초간 대기
            self.thread = None
        
        self.status_changed.emit("클립보드 모니터링 중지됨")
    
    def _clear_clipboard(self):
        """
        클립보드 내용 초기화
        """
        app_logger.debug("클립보드 내용 초기화")
        pyperclip.copy('')
        self.last_content = ""
    
    def save_clipboard_content(self, content):
        """
        클립보드 내용을 파일에 저장
        """
        if not content or not self.output_file:
            return False
        
        try:
            # 내용 길이 로깅 (전체 내용을 로깅하면 너무 길어질 수 있음)
            content_preview = content[:50] + "..." if len(content) > 50 else content
            app_logger.info(f"클립보드 내용 저장 (길이: {len(content)}): {content_preview}")
            
            # 파일에 내용 추가
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(content + '\n')
            
            app_logger.debug(f"클립보드 내용을 파일에 저장: {self.output_file}")
            
            self.status_changed.emit(f"클립보드 내용이 파일에 저장됨")
            return True
        except Exception as e:
            error_msg = f"클립보드 내용 저장 중 오류: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            self.status_changed.emit(error_msg)
            return False
    
    def _monitor_clipboard(self):
        """
        클립보드 모니터링 스레드 함수
        """
        try:
            app_logger.debug("클립보드 모니터링 스레드 시작")
            
            while self.monitoring:
                # 현재 클립보드 내용 가져오기
                current_content = pyperclip.paste()
                
                # 새로운 내용이 있고 이전과 다른 경우에만 저장
                if current_content and current_content != self.last_content:
                    self.save_clipboard_content(current_content)
                    self.last_content = current_content
                
                # 잠시 대기
                time.sleep(0.5)
            
            app_logger.debug("클립보드 모니터링 스레드 종료")
        
        except Exception as e:
            error_msg = f"클립보드 모니터링 중 오류 발생: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            self.monitoring = False
            self.status_changed.emit(error_msg)