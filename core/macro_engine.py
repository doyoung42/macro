#!/usr/bin/env python
# -*- coding: utf-8 -*-
# core/macro_engine.py

import time
import threading
import json
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from pynput import keyboard
from utils.logger import app_logger
from core.actions import MacroAction

class MacroEngine(QObject):
    """
    매크로 동작을 실행하고 관리하는 엔진 클래스
    """
    # 상태 변화 시그널
    status_changed = pyqtSignal(str)
    macro_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # 매크로 동작 목록
        self.actions = []
        
        # 실행 설정
        self.delay = 100  # ms
        self.loop_count = 1
        self.stop_key = "f12"
        
        # 실행 상태
        self.running = False
        self.paused = False
        self.thread = None
        self.keyboard_listener = None
        
        app_logger.info("매크로 엔진 초기화 완료")
    
    def add_action(self, action):
        """
        매크로 동작 추가
        """
        app_logger.debug(f"매크로 동작 추가: {action.name}")
        self.actions.append(action)
    
    def replace_action(self, index, action):
        """
        매크로 동작 교체
        """
        if 0 <= index < len(self.actions):
            old_action = self.actions[index]
            app_logger.debug(f"매크로 동작 교체: [{index}] {old_action.name} -> {action.name}")
            self.actions[index] = action
    
    def remove_action(self, index):
        """
        매크로 동작 제거
        """
        if 0 <= index < len(self.actions):
            action = self.actions[index]
            app_logger.debug(f"매크로 동작 제거: [{index}] {action.name}")
            del self.actions[index]
    
    def move_action_up(self, index):
        """
        매크로 동작을 위로 이동
        """
        if 0 < index < len(self.actions):
            app_logger.debug(f"매크로 동작 위로 이동: [{index}] {self.actions[index].name}")
            self.actions[index], self.actions[index-1] = self.actions[index-1], self.actions[index]
    
    def move_action_down(self, index):
        """
        매크로 동작을 아래로 이동
        """
        if 0 <= index < len(self.actions) - 1:
            app_logger.debug(f"매크로 동작 아래로 이동: [{index}] {self.actions[index].name}")
            self.actions[index], self.actions[index+1] = self.actions[index+1], self.actions[index]
    
    def get_action(self, index):
        """
        지정된 인덱스의 매크로 동작 반환
        """
        if 0 <= index < len(self.actions):
            return self.actions[index]
        return None
    
    def clear_actions(self):
        """
        모든 매크로 동작 제거
        """
        app_logger.debug("모든 매크로 동작 제거")
        self.actions.clear()
    
    def set_delay(self, delay):
        """
        동작 간 지연 시간 설정
        """
        app_logger.debug(f"매크로 지연 시간 설정: {delay}ms")
        self.delay = max(0, delay)
    
    def set_loop_count(self, count):
        """
        반복 횟수 설정
        """
        if count <= 0:
            app_logger.debug("매크로 무한 반복 설정")
        else:
            app_logger.debug(f"매크로 반복 횟수 설정: {count}회")
        self.loop_count = count
    
    def set_stop_key(self, key):
        """
        중지 키 설정
        """
        app_logger.debug(f"매크로 중지 키 설정: {key}")
        self.stop_key = key.lower()
    
    def is_running(self):
        """
        매크로가 실행 중인지 확인
        """
        return self.running
    
    def is_paused(self):
        """
        매크로가 일시정지 상태인지 확인
        """
        return self.paused
    
    def on_key_press(self, key):
        """
        키 입력 이벤트 핸들러
        """
        try:
            # 일반 키인 경우
            key_str = key.char.lower()
        except AttributeError:
            # 특수 키인 경우 (F1-F12, ESC 등)
            key_str = key.name.lower() if hasattr(key, 'name') else str(key).lower()
        
        # 중지 키가 눌렸는지 확인
        if key_str == self.stop_key.lower():
            app_logger.info(f"중지 키 감지: {key_str}")
            self.stop()
            return False  # 리스너 중지
        
        return True  # 다른 키는 무시
    
    def start(self):
        """
        매크로 실행 시작
        """
        if self.running:
            app_logger.warning("매크로가 이미 실행 중입니다")
            return
        
        if not self.actions:
            app_logger.warning("실행할 매크로 동작이 없습니다")
            self.status_changed.emit("실행할 매크로 동작이 없습니다.")
            return
        
        # 실행 상태 초기화
        self.running = True
        self.paused = False
        
        # 중지 키 리스너 시작
        app_logger.info(f"키보드 리스너 시작 (중지 키: {self.stop_key})")
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        
        # 텍스트 리스트 동작 인덱스 초기화
        for action in self.actions:
            if hasattr(action, 'reset'):
                action.reset()
        
        # 매크로 실행 스레드 시작
        app_logger.info("매크로 실행 스레드 시작")
        self.thread = threading.Thread(target=self._run_macro)
        self.thread.daemon = True
        self.thread.start()
        
        self.status_changed.emit("매크로 실행 시작")
    
    def pause(self):
        """
        매크로 일시 정지
        """
        if self.running and not self.paused:
            app_logger.info("매크로 일시 정지")
            self.paused = True
            self.status_changed.emit("매크로 일시 정지됨")
    
    def resume(self):
        """
        매크로 재개
        """
        if self.running and self.paused:
            app_logger.info("매크로 실행 재개")
            self.paused = False
            self.status_changed.emit("매크로 다시 실행 중")
    
    def stop(self):
        """
        매크로 실행 중지
        """
        if not self.running:
            app_logger.debug("매크로가 실행 중이 아닙니다")
            return
        
        app_logger.info("매크로 실행 중지")
        self.running = False
        self.paused = False
        
        # 키보드 리스너 중지
        if self.keyboard_listener and self.keyboard_listener.is_alive():
            app_logger.debug("키보드 리스너 중지")
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        # 스레드 종료 대기 - 현재 스레드가 아닌 경우에만 join 시도
        if self.thread and self.thread.is_alive() and self.thread != threading.current_thread():
            app_logger.debug("매크로 스레드 종료 대기")
            self.thread.join(1.0)  # 최대 1초간 대기
        self.thread = None
        
        self.status_changed.emit("매크로 중지됨")
        self.macro_finished.emit()

    def _run_macro(self):
        """
        매크로 실행 스레드 함수
        """
        try:
            # 무한 반복 또는 지정된 횟수만큼 반복
            loop_counter = 0
            infinite_loop = (self.loop_count <= 0)
            
            app_logger.info(f"매크로 실행 시작: {'무한 반복' if infinite_loop else f'{self.loop_count}회 반복'}")
            
            # 폴더 모니터링 객체 찾기
            folder_monitor_actions = [action for action in self.actions 
                                    if isinstance(action, FolderMonitorAction)]
            
            while self.running and (infinite_loop or loop_counter < self.loop_count):
                # 각 반복 시작 시 새 폴더 체크
                for action in folder_monitor_actions:
                    if hasattr(action, 'folder_monitor') and action.folder_monitor:
                        # 새 폴더 확인
                        new_folders = action.folder_monitor.check_new_folders()
                        
                        if new_folders:
                            # 새 폴더가 있으면 각각 처리
                            for folder in new_folders:
                                action.folder_monitor.handle_new_folder(folder)
                                # 처리된 폴더를 초기 목록에 추가하여 다시 처리하지 않게 함
                                action.folder_monitor.initial_folders.append(folder)
                        else:
                            # 새 폴더가 없으면 부모 폴더에 저장
                            action.folder_monitor.save_to_parent_folder()
                
                # 각 동작 실행
                action_index = 0
                for action in self.actions:
                    # 일시정지 상태면 대기
                    while self.paused and self.running:
                        time.sleep(0.1)
                    
                    # 중지되었으면 반복 종료
                    if not self.running:
                        app_logger.debug("매크로 중지 감지, 실행 종료")
                        break
                    
                    # 동작 실행
                    try:
                        app_logger.info(f"매크로 동작: [{action_index}] {action.name} - 반복: {loop_counter+1}")
                        success = action.execute()
                        if not success:
                            error_msg = f"동작 실패: {action.name}"
                            app_logger.warning(error_msg)
                            self.status_changed.emit(error_msg)
                    except Exception as e:
                        error_msg = f"오류 발생: {str(e)}"
                        app_logger.error(error_msg, exc_info=True)
                        self.status_changed.emit(error_msg)
                    
                    # 지연 시간 대기
                    time.sleep(self.delay / 1000.0)
                    action_index += 1
                
                # 반복 카운터 증가
                if not infinite_loop:
                    loop_counter += 1
                    app_logger.debug(f"매크로 반복 완료: {loop_counter}/{self.loop_count}")
            
            # 정상 종료 시
            if self.running:
                app_logger.info("매크로 모든 반복 실행 완료")
                self.status_changed.emit("매크로 실행 완료")
                
                # 스레드 내에서 stop 호출 시 current_thread 문제 방지
                self.running = False
                self.paused = False
                self.macro_finished.emit()
            
        except Exception as e:
            error_msg = f"매크로 실행 중 오류 발생: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            self.status_changed.emit(error_msg)
            self.running = False
            self.paused = False
            self.macro_finished.emit()

    def save_to_file(self, file_path):
        """
        매크로 동작 리스트를 파일로 저장
        """
        try:
            app_logger.info(f"매크로 동작 리스트 저장: {file_path}")
            
            # 모든 동작을 딕셔너리로 변환
            actions_data = []
            for action in self.actions:
                actions_data.append(action.to_dict())
            
            # 설정 데이터 준비
            data = {
                "version": "1.0",
                "delay": self.delay,
                "loop_count": self.loop_count,
                "stop_key": self.stop_key,
                "actions": actions_data
            }
            
            # JSON 파일로 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            app_logger.info(f"매크로 저장 완료: {len(actions_data)}개 동작")
            return True
        
        except Exception as e:
            error_msg = f"매크로 저장 중 오류 발생: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            return False
    
    def load_from_file(self, file_path):
        """
        파일에서 매크로 동작 리스트 불러오기
        """
        try:
            app_logger.info(f"매크로 동작 리스트 불러오기: {file_path}")
            
            # 파일에서 JSON 데이터 불러오기
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 버전 확인
            version = data.get("version", "1.0")
            app_logger.debug(f"매크로 파일 버전: {version}")
            
            # 설정 값 불러오기
            self.delay = data.get("delay", 100)
            self.loop_count = data.get("loop_count", 1)
            self.stop_key = data.get("stop_key", "f12")
            
            # 동작 목록 초기화
            self.clear_actions()
            
            # 동작 객체 생성 및 추가
            actions_data = data.get("actions", [])
            for action_data in actions_data:
                action = MacroAction.from_dict(action_data)
                if action:
                    self.add_action(action)
            
            app_logger.info(f"매크로 불러오기 완료: {len(self.actions)}개 동작")
            return True
        
        except Exception as e:
            error_msg = f"매크로 불러오기 중 오류 발생: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            return False
    