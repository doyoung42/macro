#!/usr/bin/env python
# -*- coding: utf-8 -*-
# core/folder_monitor.py

import os
import time
import threading
import pyperclip
from datetime import datetime
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
        self.filename_template = "clipboard.txt"  # 기본 파일명
        self.monitoring = False
        self.observer = None
        self.initial_folders = []  # 시작 시 폴더 목록
        
        app_logger.info("폴더 모니터 초기화 완료")
    
    def set_folder_path(self, folder_path):
        """
        모니터링할 폴더 경로 설정
        """
        app_logger.debug(f"모니터링 폴더 경로 설정: {folder_path}")
        self.folder_path = folder_path
    
    def set_filename_template(self, filename):
        """
        저장할 파일명 템플릿 설정
        """
        app_logger.debug(f"저장 파일명 템플릿 설정: {filename}")
        self.filename_template = filename if filename else "clipboard.txt"
    
    def is_monitoring(self):
        """
        폴더 모니터링 상태 확인
        """
        return self.monitoring
    
    def start_monitoring(self):
        """
        폴더 모니터링 시작
        """
        if not self.folder_path or not os.path.exists(self.folder_path):
            app_logger.warning("폴더 모니터링을 시작할 수 없음: 폴더 경로가 유효하지 않음")
            return
        
        # 이미 실행 중인 경우 먼저 중지
        if self.monitoring:
            self.stop_monitoring()
        
        # 시작 시 폴더 목록 저장
        self.initial_folders = self._get_subfolders()
        app_logger.debug(f"시작 시 하위 폴더 개수: {len(self.initial_folders)}")
        
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
    
    def _get_subfolders(self):
        """
        현재 하위 폴더 목록 가져오기
        """
        subfolders = []
        for name in os.listdir(self.folder_path):
            full_path = os.path.join(self.folder_path, name)
            if os.path.isdir(full_path):
                subfolders.append(full_path)
        return subfolders
    
    def check_new_folders(self):
        """
        새로 생성된 폴더 확인
        """
        if not self.monitoring or not self.folder_path:
            return []
        
        current_folders = self._get_subfolders()
        new_folders = [f for f in current_folders if f not in self.initial_folders]
        
        if new_folders:
            app_logger.debug(f"새 폴더 감지: {len(new_folders)}개")
        
        return new_folders
    
    def handle_new_folder(self, folder_path):
        """
        새 폴더 생성 처리
        """
        # 모니터링 중이 아닌 경우 무시
        if not self.monitoring:
            app_logger.debug(f"새 폴더 무시 (모니터링 비활성): {folder_path}")
            return
        
        try:
            # 클립보드 내용 캡처하기 전 잠시 대기 (복사 작업이 완료될 시간)
            import time
            time.sleep(0.5)  # 500ms 대기
            
            # 클립보드 내용 가져오기
            clipboard_content = pyperclip.paste()
            
            # 내용이 있는 경우 파일에 저장
            if clipboard_content:
                # 저장할 파일 경로 생성 (사용자 지정 파일명 또는 기본값)
                file_path = os.path.join(folder_path, self.filename_template)
                
                # 내용 길이 로깅 (전체 내용을 로깅하면 너무 길어질 수 있음)
                content_preview = clipboard_content[:50] + "..." if len(clipboard_content) > 50 else clipboard_content
                app_logger.info(f"클립보드 내용을 새 폴더에 저장 (길이: {len(clipboard_content)}): {folder_path}")
                app_logger.debug(f"클립보드 내용 미리보기: {content_preview}")
                
                # 파일에 내용 저장
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clipboard_content)
                
                app_logger.debug(f"저장된 파일 경로: {file_path}")
                
                self.status_changed.emit(f"클립보드 내용이 새 폴더에 저장됨: {file_path}")
                return True
            else:
                app_logger.warning(f"새 폴더가 감지되었으나 클립보드가 비어 있음: {folder_path}")
                return False
        
        except Exception as e:
            error_msg = f"새 폴더 처리 중 오류 발생: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            self.status_changed.emit(error_msg)
            return False
    
    def save_to_parent_folder(self):
        """
        새 폴더가 없을 경우 부모 폴더에 타임스탬프 파일명으로 저장
        """
        if not self.monitoring or not self.folder_path:
            return False
        
        try:
            # 클립보드 내용 가져오기
            clipboard_content = pyperclip.paste()
            
            if clipboard_content:
                # 타임스탬프 파일명 생성
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"clipboard_{timestamp}.txt"
                file_path = os.path.join(self.folder_path, filename)
                
                # 파일에 내용 저장
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clipboard_content)
                
                app_logger.info(f"클립보드 내용을 타임스탬프 파일로 저장: {file_path}")
                
                self.status_changed.emit(f"클립보드 내용이 저장됨: {file_path}")
                return True
            else:
                app_logger.warning("클립보드가 비어 있어 저장하지 않음")
                return False
                
        except Exception as e:
            error_msg = f"부모 폴더 저장 중 오류 발생: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            self.status_changed.emit(error_msg)
            return False
        
    def check_and_process_folders(self):
        """
        새 폴더 확인 및 처리 - 매크로 실행 시 명시적으로 호출할 메서드
        """
        if not self.monitoring or not self.folder_path:
            app_logger.debug("폴더 모니터링이 활성화되어 있지 않음")
            return False
        
        try:
            # 현재 하위 폴더 목록 가져오기
            current_folders = self._get_subfolders()
            
            # 새로 추가된 폴더 확인
            new_folders = [f for f in current_folders if f not in self.initial_folders]
            
            if new_folders:
                app_logger.info(f"새 폴더 {len(new_folders)}개 감지: {new_folders}")
                
                # 클립보드 내용 가져오기
                clipboard_content = pyperclip.paste()
                
                if not clipboard_content:
                    app_logger.warning("클립보드가 비어 있어 저장할 내용이 없습니다.")
                    return False
                
                # 각 새 폴더에 클립보드 내용 저장
                for folder in new_folders:
                    folder_name = os.path.basename(folder)
                    file_path = os.path.join(folder, self.filename_template)
                    
                    app_logger.info(f"클립보드 내용을 새 폴더에 저장: {file_path}")
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(clipboard_content)
                    
                    # 처리된 폴더를 초기 목록에 추가
                    self.initial_folders.append(folder)
                
                self.status_changed.emit(f"클립보드 내용이 {len(new_folders)}개의 새 폴더에 저장됨")
                return True
            else:
                app_logger.debug("새 폴더가 감지되지 않음")
                
                # 새 폴더가 없을 경우 타임스탬프 파일로 저장
                if self.save_to_parent_folder():
                    return True
                
                return False
                
        except Exception as e:
            error_msg = f"폴더 확인 중 오류 발생: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            self.status_changed.emit(error_msg)
            return False