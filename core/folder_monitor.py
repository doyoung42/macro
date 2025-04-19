#!/usr/bin/env python
# -*- coding: utf-8 -*-
# core/folder_monitor.py

import os
import time
import threading
import pyperclip
from PyQt5.QtCore import QObject, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.logger import app_logger

class FolderEventHandler(FileSystemEventHandler):
    """
    파일 시스템 이벤트 핸들러
    """
    def __init__(self, folder_monitor):
        self.folder_monitor = folder_monitor
    
    def on_created(self, event):
        """
        폴더 생성 이벤트 처리
        """
        if event.is_directory:
            app_logger.debug(f"새 폴더 생성 감지: {event.src_path}")
            self.folder_monitor.handle_new_folder(event.src_path)


class FolderMonitor(QObject):
    """
    폴더를 모니터링하고 새 폴더 생성시 클립보드 내용을 저장하는 클래스
    """
    # 상태 변화 시그널
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 폴더 모니터링 설정
        self.folder_path = ""
        self.monitoring = False
        self.observer = None
        
        app_logger.info("폴더 모니터 초기화 완료")
    
    def set_folder_path(self, folder_path):
        """
        모니터링할 폴더 경로 설정
        """
        app_logger.debug(f"모니터링 폴더 경로 설정: {folder_path}")
        self.folder_path = folder_path
    
    def is_monitoring(self):
        """
        폴더 모니터링 상태 확인
        """
        return self.monitoring
    
    def start_monitoring(self):
        """
        폴더 모니터링 시작
        """
        if self.monitoring or not self.folder_path or not os.path.exists(self.folder_path):
            app_logger.warning("폴더 모니터링을 시작할 수 없음: 이미 모니터링 중이거나 폴더 경로가 유효하지 않음")
            return
        
        # 클립보드 초기화
        pyperclip.copy('')
        app_logger.debug("클립보드 내용 초기화")
        
        self.monitoring = True
        
        # 이벤트 핸들러 생성
        event_handler = FolderEventHandler(self)
        
        # 관찰자 설정
        app_logger.info(f"폴더 모니터링 시작: {self.folder_path}")
        self.observer = Observer()
        self.observer.schedule(event_handler, self.folder_path, recursive=True)
        self.observer.start()
        
        self.status_changed.emit(f"폴더 모니터링 시작됨: {self.folder_path}")
    
    def stop_monitoring(self):
        """
        폴더 모니터링 중지
        """
        if not self.monitoring:
            app_logger.debug("폴더 모니터링이 활성화되어 있지 않음")
            return
        
        app_logger.info("폴더 모니터링 중지")
        self.monitoring = False
        
        # 관찰자 중지
        if self.observer:
            app_logger.debug("폴더 모니터링 관찰자 중지")
            self.observer.stop()
            self.observer.join(timeout=1.0)
            self.observer = None
        
        self.status_changed.emit("폴더 모니터링 중지됨")
    
    def handle_new_folder(self, folder_path):
        """
        새 폴더 생성 처리
        """
        # 모니터링 중이 아닌 경우 무시
        if not self.monitoring:
            app_logger.debug(f"새 폴더 무시 (모니터링 비활성): {folder_path}")
            return
        
        try:
            # 클립보드 내용 가져오기
            clipboard_content = pyperclip.paste()
            
            # 내용이 있는 경우 파일에 저장
            if clipboard_content:
                # 저장할 파일 경로 생성 (폴더명 + .txt)
                folder_name = os.path.basename(folder_path)
                file_path = os.path.join(folder_path, f"{folder_name}.txt")
                
                # 내용 길이 로깅 (전체 내용을 로깅하면 너무 길어질 수 있음)
                content_preview = clipboard_content[:50] + "..." if len(clipboard_content) > 50 else clipboard_content
                app_logger.info(f"클립보드 내용을 새 폴더에 저장 (길이: {len(clipboard_content)}): {folder_path}")
                app_logger.debug(f"클립보드 내용 미리보기: {content_preview}")
                
                # 파일에 내용 저장
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clipboard_content)
                
                app_logger.debug(f"저장된 파일 경로: {file_path}")
                
                # 클립보드 비우기
                pyperclip.copy('')
                app_logger.debug("클립보드 내용 비움")
                
                self.status_changed.emit(f"클립보드 내용이 새 폴더에 저장됨: {file_path}")
            else:
                app_logger.warning(f"새 폴더가 감지되었으나 클립보드가 비어 있음: {folder_path}")
        
        except Exception as e:
            error_msg = f"새 폴더 처리 중 오류 발생: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            self.status_changed.emit(error_msg)