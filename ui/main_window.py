#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ui/main_window.py


import os
import json
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QListWidget, QLabel, QMessageBox,
                            QGroupBox, QCheckBox, QSpinBox, QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot

from ui.action_editor import ActionEditorDialog
from core.macro_engine import MacroEngine
from core.actions import (MacroAction, MouseClickAction, MouseMoveAction, 
                         KeyboardInputAction, KeyCombinationAction, 
                         MouseDragDropAction, TextListInputAction)  # TextListInputAction 추가
from core.clipboard_manager import ClipboardManager
from core.folder_monitor import FolderMonitor
from utils.config import Config
from utils.logger import app_logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        app_logger.info("메인 윈도우 초기화 중...")
        
        # 앱 설정 로드
        self.config = Config()
        app_logger.info("설정 로드 완료")
        
        # 매크로 엔진 초기화
        self.macro_engine = MacroEngine()
        app_logger.info("매크로 엔진 초기화 완료")
        
        # 클립보드 매니저 초기화
        self.clipboard_manager = ClipboardManager()
        app_logger.info("클립보드 매니저 초기화 완료")
        
        # 폴더 모니터 초기화
        self.folder_monitor = FolderMonitor()
        app_logger.info("폴더 모니터 초기화 완료")
        
        # UI 설정
        self.setWindowTitle("마우스 키보드 매크로")
        self.setMinimumSize(800, 600)
        
        # 중앙 위젯 설정
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 레이아웃 설정
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # UI 요소 초기화
        app_logger.info("UI 요소 초기화 시작")
        self._init_ui()
        app_logger.info("UI 요소 초기화 완료")
        
        # 이벤트 연결
        app_logger.info("이벤트 연결 시작")
        self._connect_events()
        app_logger.info("이벤트 연결 완료")
        
        # 로깅 상태 메시지
        app_logger.info("메인 윈도우 초기화 완료")
    
    def _init_ui(self):
        """
        UI 요소 초기화
        """
        # 매크로 동작 리스트 섹션
        self.actions_group = QGroupBox("매크로 동작 리스트")
        actions_layout = QVBoxLayout()
        
        # 동작 리스트 위젯
        self.actions_list = QListWidget()
        self.actions_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        actions_layout.addWidget(self.actions_list)
        
        # 동작 관리 버튼 레이아웃
        action_buttons_layout = QHBoxLayout()
        self.add_action_btn = QPushButton("동작 추가")
        self.edit_action_btn = QPushButton("동작 편집")
        self.remove_action_btn = QPushButton("동작 삭제")
        self.move_up_btn = QPushButton("위로")
        self.move_down_btn = QPushButton("아래로")
        
        action_buttons_layout.addWidget(self.add_action_btn)
        action_buttons_layout.addWidget(self.edit_action_btn)
        action_buttons_layout.addWidget(self.remove_action_btn)
        action_buttons_layout.addWidget(self.move_up_btn)
        action_buttons_layout.addWidget(self.move_down_btn)
        
        actions_layout.addLayout(action_buttons_layout)

        # 저장 및 불러오기 버튼 추가
        save_load_layout = QHBoxLayout()
        self.save_macro_btn = QPushButton("매크로 저장")
        self.load_macro_btn = QPushButton("매크로 불러오기")
        
        save_load_layout.addWidget(self.save_macro_btn)
        save_load_layout.addWidget(self.load_macro_btn)
        
        actions_layout.addLayout(save_load_layout)

        self.actions_group.setLayout(actions_layout)
        self.main_layout.addWidget(self.actions_group)
        
        # 매크로 실행 설정 섹션
        self.execution_group = QGroupBox("매크로 실행 설정")
        execution_layout = QVBoxLayout()
        
        # 반복 설정
        loop_layout = QHBoxLayout()
        loop_layout.addWidget(QLabel("반복 횟수:"))
        self.loop_count_spin = QSpinBox()
        self.loop_count_spin.setMinimum(1)
        self.loop_count_spin.setMaximum(9999)
        self.loop_count_spin.setValue(1)
        loop_layout.addWidget(self.loop_count_spin)
        
        self.infinite_loop_check = QCheckBox("무한 반복")
        loop_layout.addWidget(self.infinite_loop_check)
        
        # 지연 설정
        loop_layout.addWidget(QLabel("동작 간 지연(ms):"))
        self.delay_spin = QSpinBox()
        self.delay_spin.setMinimum(0)
        self.delay_spin.setMaximum(10000)
        self.delay_spin.setValue(100)
        loop_layout.addWidget(self.delay_spin)
        
        execution_layout.addLayout(loop_layout)
        
        # 실행 중지 키 설정
        stop_key_layout = QHBoxLayout()
        stop_key_layout.addWidget(QLabel("중지 키:"))
        self.stop_key_label = QLabel("F12")
        stop_key_layout.addWidget(self.stop_key_label)
        self.set_stop_key_btn = QPushButton("중지 키 설정")
        stop_key_layout.addWidget(self.set_stop_key_btn)
        stop_key_layout.addStretch()
        
        execution_layout.addLayout(stop_key_layout)
        
        # 클립보드 관리 설정
        clipboard_layout = QHBoxLayout()
        self.save_clipboard_check = QCheckBox("클립보드 내용 저장")
        clipboard_layout.addWidget(self.save_clipboard_check)
        
        self.clipboard_file_path = QLabel("파일 미선택")
        clipboard_layout.addWidget(self.clipboard_file_path)
        
        self.select_clipboard_file_btn = QPushButton("파일 선택")
        clipboard_layout.addWidget(self.select_clipboard_file_btn)
        
        execution_layout.addLayout(clipboard_layout)
        
        # 폴더 모니터링 설정
        folder_layout = QHBoxLayout()
        self.monitor_folder_check = QCheckBox("폴더 모니터링")
        folder_layout.addWidget(self.monitor_folder_check)
        
        self.monitored_folder_path = QLabel("폴더 미선택")
        folder_layout.addWidget(self.monitored_folder_path)
        
        self.select_folder_btn = QPushButton("폴더 선택")
        folder_layout.addWidget(self.select_folder_btn)
        
        execution_layout.addLayout(folder_layout)
        
        self.execution_group.setLayout(execution_layout)
        self.main_layout.addWidget(self.execution_group)
        
        # 실행 제어 버튼
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("매크로 시작")
        self.start_btn.setMinimumHeight(50)
        self.pause_btn = QPushButton("일시 정지")
        self.pause_btn.setMinimumHeight(50)
        self.stop_btn = QPushButton("중지")
        self.stop_btn.setMinimumHeight(50)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        
        self.main_layout.addLayout(control_layout)
        
        # 상태 표시줄
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("준비")
        
        # 초기 버튼 상태 설정
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.edit_action_btn.setEnabled(False)
        self.remove_action_btn.setEnabled(False)
        self.move_up_btn.setEnabled(False)
        self.move_down_btn.setEnabled(False)
    
    def _connect_events(self):
        """
        이벤트 연결
        """
        # 동작 관리 버튼
        self.add_action_btn.clicked.connect(self.add_action)
        self.edit_action_btn.clicked.connect(self.edit_action)
        self.remove_action_btn.clicked.connect(self.remove_action)
        self.move_up_btn.clicked.connect(self.move_action_up)
        self.move_down_btn.clicked.connect(self.move_action_down)
        
        # 리스트 아이템 선택 변경
        self.actions_list.itemSelectionChanged.connect(self.on_action_selection_changed)
        
        # 실행 제어 버튼
        self.start_btn.clicked.connect(self.start_macro)
        self.pause_btn.clicked.connect(self.pause_macro)
        self.stop_btn.clicked.connect(self.stop_macro)
        
        # 저장 및 불러오기 버튼 연결
        self.save_macro_btn.clicked.connect(self.save_macro)
        self.load_macro_btn.clicked.connect(self.load_macro)

        # 설정 버튼
        self.set_stop_key_btn.clicked.connect(self.set_stop_key)
        self.select_clipboard_file_btn.clicked.connect(self.select_clipboard_file)
        self.select_folder_btn.clicked.connect(self.select_monitored_folder)
        
        # 체크박스
        self.infinite_loop_check.stateChanged.connect(self.on_infinite_loop_changed)
        self.save_clipboard_check.stateChanged.connect(self.on_save_clipboard_changed)
        self.monitor_folder_check.stateChanged.connect(self.on_monitor_folder_changed)
        
        # 매크로 엔진 시그널
        self.macro_engine.status_changed.connect(self.on_macro_status_changed)
        self.macro_engine.macro_finished.connect(self.on_macro_finished)
    
    @pyqtSlot(str)
    def on_macro_status_changed(self, status):
        """
        매크로 상태 변경 시 처리
        """
        app_logger.info(f"매크로 상태 변경: {status}")
        self.statusbar.showMessage(status)
    
    @pyqtSlot()
    def on_macro_finished(self):
        """
        매크로 실행 완료 시 처리
        """
        app_logger.info("매크로 실행 완료")
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.actions_group.setEnabled(True)
        self.execution_group.setEnabled(True)
    
    @pyqtSlot()
    def add_action(self):
        """
        새 매크로 동작 추가
        """
        app_logger.log_ui_action("동작 추가 버튼 클릭")
        dialog = ActionEditorDialog(self)
        if dialog.exec():
            action = dialog.get_action()
            if action:
                app_logger.log_ui_action("새 동작 추가", f"유형: {action.name}")
                self.actions_list.addItem(action.to_list_item())
                self.macro_engine.add_action(action)
                
                # 텍스트 리스트 입력인 경우 자동으로 반복 횟수 설정
                if isinstance(action, TextListInputAction) and not self.infinite_loop_check.isChecked():
                    items_count = action.get_items_count()
                    if items_count > 0:
                        app_logger.info(f"텍스트 리스트 입력 동작 추가: 반복 횟수를 {items_count}로 자동 설정")
                        self.loop_count_spin.setValue(items_count)
    
    @pyqtSlot()
    def edit_action(self):
        """
        선택된 매크로 동작 편집
        """
        current_row = self.actions_list.currentRow()
        app_logger.log_ui_action("동작 편집 버튼 클릭", f"선택된 항목: {current_row}")
        
        if current_row >= 0:
            current_action = self.macro_engine.get_action(current_row)
            dialog = ActionEditorDialog(self, current_action)
            
            if dialog.exec():
                edited_action = dialog.get_action()
                if edited_action:
                    app_logger.log_ui_action("동작 편집 완료", f"유형: {edited_action.name}")
                    self.actions_list.takeItem(current_row)
                    self.actions_list.insertItem(current_row, edited_action.to_list_item())
                    self.actions_list.setCurrentRow(current_row)
                    self.macro_engine.replace_action(current_row, edited_action)
                    
                    # 텍스트 리스트 입력인 경우 자동으로 반복 횟수 설정 (무한 반복이 설정되지 않은 경우에만)
                    if isinstance(edited_action, TextListInputAction) and not self.infinite_loop_check.isChecked():
                        items_count = edited_action.get_items_count()
                        if items_count > 0:
                            app_logger.info(f"텍스트 리스트 입력 동작 편집: 반복 횟수를 {items_count}로 자동 설정")
                            self.loop_count_spin.setValue(items_count)
    
    @pyqtSlot()
    def remove_action(self):
        """
        선택된 매크로 동작 제거
        """
        current_row = self.actions_list.currentRow()
        app_logger.log_ui_action("동작 삭제 버튼 클릭", f"선택된 항목: {current_row}")
        
        if current_row >= 0:
            action = self.macro_engine.get_action(current_row)
            app_logger.log_ui_action("동작 삭제", f"유형: {action.name}")
            
            self.actions_list.takeItem(current_row)
            self.macro_engine.remove_action(current_row)
            
            # 선택 항목이 없을 경우 버튼 비활성화
            if self.actions_list.count() == 0:
                self.edit_action_btn.setEnabled(False)
                self.remove_action_btn.setEnabled(False)
                self.move_up_btn.setEnabled(False)
                self.move_down_btn.setEnabled(False)
    
    @pyqtSlot()
    def move_action_up(self):
        """
        선택된 매크로 동작을 위로 이동
        """
        current_row = self.actions_list.currentRow()
        app_logger.log_ui_action("동작 위로 이동 버튼 클릭", f"선택된 항목: {current_row}")
        
        if current_row > 0:
            action = self.macro_engine.get_action(current_row)
            app_logger.log_ui_action("동작 위로 이동", f"유형: {action.name}, 위치: {current_row} -> {current_row-1}")
            
            item = self.actions_list.takeItem(current_row)
            self.actions_list.insertItem(current_row - 1, item)
            self.actions_list.setCurrentRow(current_row - 1)
            self.macro_engine.move_action_up(current_row)
    
    @pyqtSlot()
    def move_action_down(self):
        """
        선택된 매크로 동작을 아래로 이동
        """
        current_row = self.actions_list.currentRow()
        app_logger.log_ui_action("동작 아래로 이동 버튼 클릭", f"선택된 항목: {current_row}")
        
        if current_row < self.actions_list.count() - 1:
            action = self.macro_engine.get_action(current_row)
            app_logger.log_ui_action("동작 아래로 이동", f"유형: {action.name}, 위치: {current_row} -> {current_row+1}")
            
            item = self.actions_list.takeItem(current_row)
            self.actions_list.insertItem(current_row + 1, item)
            self.actions_list.setCurrentRow(current_row + 1)
            self.macro_engine.move_action_down(current_row)
    
    @pyqtSlot()
    def save_macro(self):
        """
        매크로 동작 리스트 저장
        """
        app_logger.log_ui_action("매크로 저장 버튼 클릭")
        
        if self.actions_list.count() == 0:
            app_logger.warning("저장할 매크로 동작이 없음")
            QMessageBox.warning(self, "경고", "저장할 매크로 동작이 없습니다.")
            return
        
        # 파일 저장 대화상자 표시
        file_path, _ = QFileDialog.getSaveFileName(
            self, "매크로 저장", "", "매크로 파일 (*.json);;모든 파일 (*.*)"
        )
        
        if not file_path:
            app_logger.debug("매크로 저장 취소됨")
            return
        
        # 확장자 확인 및 추가
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
        
        # 매크로 저장
        if self.macro_engine.save_to_file(file_path):
            self.config.add_recent_file(file_path)  # 최근 파일 목록에 추가
            QMessageBox.information(self, "저장 완료", f"매크로가 저장되었습니다.\n{file_path}")
        else:
            QMessageBox.critical(self, "저장 실패", "매크로 저장 중 오류가 발생했습니다.")

    @pyqtSlot()
    def load_macro(self):
        """
        매크로 동작 리스트 불러오기
        """
        app_logger.log_ui_action("매크로 불러오기 버튼 클릭")
        
        # 현재 실행 중인 경우 경고
        if self.macro_engine.is_running():
            app_logger.warning("매크로 실행 중에는 불러올 수 없음")
            QMessageBox.warning(self, "경고", "매크로가 실행 중입니다. 먼저 중지해주세요.")
            return
        
        # 확인 메시지 표시
        if self.actions_list.count() > 0:
            reply = QMessageBox.question(
                self, "매크로 불러오기", 
                "현재 매크로 동작 목록을 지우고 새로 불러오시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                app_logger.debug("매크로 불러오기 취소됨")
                return
        
        # 파일 선택 대화상자 표시
        file_path, _ = QFileDialog.getOpenFileName(
            self, "매크로 불러오기", "", "매크로 파일 (*.json);;모든 파일 (*.*)"
        )
        
        if not file_path:
            app_logger.debug("매크로 불러오기 취소됨")
            return
        
        # 매크로 불러오기
        if self.macro_engine.load_from_file(file_path):
            # UI 업데이트
            self.actions_list.clear()
            for action in self.macro_engine.actions:
                self.actions_list.addItem(action.to_list_item())
            
            # 설정 업데이트
            self.delay_spin.setValue(self.macro_engine.delay)
            
            loop_count = self.macro_engine.loop_count
            if loop_count <= 0:
                self.infinite_loop_check.setChecked(True)
                self.loop_count_spin.setEnabled(False)
            else:
                self.infinite_loop_check.setChecked(False)
                self.loop_count_spin.setEnabled(True)
                self.loop_count_spin.setValue(loop_count)
            
            self.stop_key_label.setText(self.macro_engine.stop_key)
            
            # 최근 파일 목록에 추가
            self.config.add_recent_file(file_path)
            
            QMessageBox.information(self, "불러오기 완료", f"매크로를 불러왔습니다.\n{file_path}")
        else:
            QMessageBox.critical(self, "불러오기 실패", "매크로 불러오기 중 오류가 발생했습니다.")

    @pyqtSlot()
    def on_action_selection_changed(self):
        """
        동작 선택 변경 시 핸들러
        """
        has_selection = len(self.actions_list.selectedItems()) > 0
        current_row = self.actions_list.currentRow()
        
        if has_selection:
            action = self.macro_engine.get_action(current_row)
            app_logger.log_ui_action("동작 선택 변경", f"유형: {action.name if action else 'None'}, 위치: {current_row}")
        
        self.edit_action_btn.setEnabled(has_selection)
        self.remove_action_btn.setEnabled(has_selection)
        self.move_up_btn.setEnabled(has_selection and current_row > 0)
        self.move_down_btn.setEnabled(has_selection and current_row < self.actions_list.count() - 1)
    
    @pyqtSlot()
    def start_macro(self):
        """
        매크로 실행 시작
        """
        app_logger.log_ui_action("매크로 시작 버튼 클릭")
        
        if self.actions_list.count() == 0:
            app_logger.warning("실행할 매크로 동작이 없음")
            QMessageBox.warning(self, "경고", "실행할 매크로 동작이 없습니다.")
            return
        
        # 매크로 설정
        self.macro_engine.set_delay(self.delay_spin.value())
        app_logger.info(f"매크로 지연 시간 설정: {self.delay_spin.value()}ms")
        
        if self.infinite_loop_check.isChecked():
            app_logger.info("매크로 무한 반복 설정")
            self.macro_engine.set_loop_count(-1)  # 무한 반복
        else:
            loop_count = self.loop_count_spin.value()
            app_logger.info(f"매크로 반복 횟수 설정: {loop_count}")
            self.macro_engine.set_loop_count(loop_count)
        
        # 클립보드 관리 설정
        if self.save_clipboard_check.isChecked():
            clipboard_file = self.clipboard_file_path.text()
            app_logger.info(f"클립보드 저장 활성화: {clipboard_file}")
            
            if os.path.exists(os.path.dirname(clipboard_file)) and clipboard_file != "파일 미선택":
                self.clipboard_manager.set_output_file(clipboard_file)
                self.clipboard_manager.start_monitoring()
            else:
                app_logger.warning("클립보드 저장 파일 경로 유효하지 않음")
                QMessageBox.warning(self, "경고", "클립보드 저장 파일을 선택해주세요.")
                return
        
        # 폴더 모니터링 설정
        if self.monitor_folder_check.isChecked():
            folder_path = self.monitored_folder_path.text()
            app_logger.info(f"폴더 모니터링 활성화: {folder_path}")
            
            if os.path.exists(folder_path) and folder_path != "폴더 미선택":
                self.folder_monitor.set_folder_path(folder_path)
                self.folder_monitor.start_monitoring()
            else:
                app_logger.warning("모니터링할 폴더 경로 유효하지 않음")
                QMessageBox.warning(self, "경고", "모니터링할 폴더를 선택해주세요.")
                return
        
        # UI 상태 변경
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.actions_group.setEnabled(False)
        self.execution_group.setEnabled(False)
        
        # 매크로 시작
        app_logger.log_macro_start()
        self.macro_engine.start()
        self.statusbar.showMessage("매크로 실행 중...")
    
    @pyqtSlot()
    def pause_macro(self):
        """
        매크로 일시 정지
        """
        app_logger.log_ui_action("일시 정지/재개 버튼 클릭")
        
        if self.macro_engine.is_paused():
            app_logger.log_macro_resume()
            self.macro_engine.resume()
            self.pause_btn.setText("일시 정지")
            self.statusbar.showMessage("매크로 실행 중...")
        else:
            app_logger.log_macro_pause()
            self.macro_engine.pause()
            self.pause_btn.setText("계속 실행")
            self.statusbar.showMessage("매크로 일시 정지됨")
    
    @pyqtSlot()
    def stop_macro(self):
        """
        매크로 중지
        """
        app_logger.log_ui_action("중지 버튼 클릭")
        app_logger.log_macro_stop("사용자에 의한 중지")
        
        self.macro_engine.stop()
        
        # 클립보드/폴더 모니터링 중지
        if self.clipboard_manager.is_monitoring():
            app_logger.log_clipboard_action("모니터링 중지", "매크로 중지로 인한 종료")
            self.clipboard_manager.stop_monitoring()
        
        if self.folder_monitor.is_monitoring():
            app_logger.log_folder_action("모니터링 중지", "매크로 중지로 인한 종료")
            self.folder_monitor.stop_monitoring()
        
        # UI 상태 복원
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("일시 정지")
        self.stop_btn.setEnabled(False)
        self.actions_group.setEnabled(True)
        self.execution_group.setEnabled(True)
        
        self.statusbar.showMessage("매크로 중지됨")
    
    @pyqtSlot()
    def set_stop_key(self):
        """
        중지 키 설정
        """
        app_logger.log_ui_action("중지 키 설정 버튼 클릭")
        
        key, ok = QInputDialog.getText(self, "중지 키 설정", "중지할 키를 입력하세요:")
        if ok and key:
            app_logger.info(f"중지 키 변경: {self.stop_key_label.text()} -> {key}")
            self.stop_key_label.setText(key)
            self.macro_engine.set_stop_key(key)
    
    @pyqtSlot()
    def select_clipboard_file(self):
        """
        클립보드 내용을 저장할 파일 선택
        """
        app_logger.log_ui_action("클립보드 저장 파일 선택 버튼 클릭")
        
        file_path, _ = QFileDialog.getSaveFileName(self, "클립보드 저장 파일 선택", "", "텍스트 파일 (*.txt);;모든 파일 (*.*)")
        if file_path:
            app_logger.log_clipboard_action("파일 선택", f"경로: {file_path}")
            self.clipboard_file_path.setText(file_path)
    
    @pyqtSlot()
    def select_monitored_folder(self):
        """
        모니터링할 폴더 선택
        """
        app_logger.log_ui_action("모니터링 폴더 선택 버튼 클릭")
        
        folder_path = QFileDialog.getExistingDirectory(self, "모니터링할 폴더 선택")
        if folder_path:
            app_logger.log_folder_action("폴더 선택", f"경로: {folder_path}")
            self.monitored_folder_path.setText(folder_path)
    
    @pyqtSlot(int)
    def on_infinite_loop_changed(self, state):
        """
        무한 반복 체크박스 변경 시 핸들러
        """
        is_checked = bool(state)
        app_logger.log_ui_action("무한 반복 설정 변경", f"상태: {is_checked}")
        self.loop_count_spin.setEnabled(not is_checked)
    
    @pyqtSlot(int)
    def on_save_clipboard_changed(self, state):
        """
        클립보드 저장 체크박스 변경 시 핸들러
        """
        is_enabled = bool(state)
        app_logger.log_ui_action("클립보드 저장 설정 변경", f"상태: {is_enabled}")
        self.clipboard_file_path.setEnabled(is_enabled)
        self.select_clipboard_file_btn.setEnabled(is_enabled)
    
    @pyqtSlot(int)
    def on_monitor_folder_changed(self, state):
        """
        폴더 모니터링 체크박스 변경 시 핸들러
        """
        is_enabled = bool(state)
        app_logger.log_ui_action("폴더 모니터링 설정 변경", f"상태: {is_enabled}")
        self.monitored_folder_path.setEnabled(is_enabled)
        self.select_folder_btn.setEnabled(is_enabled)
    
    def closeEvent(self, event):
        """
        애플리케이션 종료 시 핸들러
        """
        app_logger.info("애플리케이션 종료 요청")
        
        # 실행 중인 매크로 중지
        if self.macro_engine.is_running():
            app_logger.log_macro_stop("애플리케이션 종료로 인한 중지")
            self.macro_engine.stop()
        
        # 클립보드 모니터링 중지
        if self.clipboard_manager.is_monitoring():
            app_logger.log_clipboard_action("모니터링 중지", "애플리케이션 종료로 인한 종료")
            self.clipboard_manager.stop_monitoring()
            
        # 폴더 모니터링 중지
        if self.folder_monitor.is_monitoring():
            app_logger.log_folder_action("모니터링 중지", "애플리케이션 종료로 인한 종료")
            self.folder_monitor.stop_monitoring()
        
        # 설정 저장
        self.config.save()
        app_logger.info("설정 저장 완료")
        
        app_logger.info("=== 애플리케이션 종료 ===")
        event.accept()