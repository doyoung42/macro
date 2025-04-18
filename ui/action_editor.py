#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QLineEdit, QPushButton, QSpinBox,
                            QDialogButtonBox, QTabWidget, QWidget, QFileDialog,
                            QListWidget, QListWidgetItem, QGridLayout, QTextEdit,
                            QCheckBox, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QPoint
from PyQt5.QtGui import QCursor

from core.actions import (MacroAction, MouseClickAction, MouseMoveAction, 
                        KeyboardInputAction, KeyCombinationAction, 
                        MouseDragDropAction, TextListInputAction)
from utils.logger import app_logger

class ActionEditorDialog(QDialog):
    def __init__(self, parent=None, action=None):
        super().__init__(parent)
        
        self.setWindowTitle("매크로 동작 편집")
        self.setMinimumSize(500, 400)
        
        self.current_action = action
        self.capture_mode = False
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.update_cursor_position)
        
        app_logger.info(f"동작 편집 다이얼로그 초기화: {action.name if action else '새 동작'}")
        
        self._init_ui()
        
        # 편집 모드인 경우 값 설정
        if action:
            app_logger.info(f"기존 동작 로드: {action.name}")
            self._load_action_data(action)
    
    def _init_ui(self):
        """
        UI 초기화
        """
        main_layout = QVBoxLayout(self)
        
        # 동작 유형 선택
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("동작 유형:"))
        
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems([
            "마우스 이동",
            "마우스 클릭",
            "마우스 드래그 & 드롭",
            "키보드 입력",
            "키 조합 입력",
            "텍스트 리스트 입력"
        ])
        
        type_layout.addWidget(self.action_type_combo)
        main_layout.addLayout(type_layout)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        
        # 1. 마우스 이동 탭
        self.mouse_move_tab = QWidget()
        mouse_move_layout = QVBoxLayout(self.mouse_move_tab)
        
        mouse_pos_layout = QGridLayout()
        mouse_pos_layout.addWidget(QLabel("X 좌표:"), 0, 0)
        self.mouse_x_spin = QSpinBox()
        self.mouse_x_spin.setRange(0, 9999)
        mouse_pos_layout.addWidget(self.mouse_x_spin, 0, 1)
        
        mouse_pos_layout.addWidget(QLabel("Y 좌표:"), 1, 0)
        self.mouse_y_spin = QSpinBox()
        self.mouse_y_spin.setRange(0, 9999)
        mouse_pos_layout.addWidget(self.mouse_y_spin, 1, 1)
        
        self.capture_pos_btn = QPushButton("마우스 위치 캡처")
        mouse_pos_layout.addWidget(self.capture_pos_btn, 2, 0, 1, 2)
        
        mouse_move_layout.addLayout(mouse_pos_layout)
        mouse_move_layout.addStretch()
        
        # 2. 마우스 클릭 탭
        self.mouse_click_tab = QWidget()
        mouse_click_layout = QVBoxLayout(self.mouse_click_tab)
        
        click_pos_layout = QGridLayout()
        click_pos_layout.addWidget(QLabel("X 좌표:"), 0, 0)
        self.click_x_spin = QSpinBox()
        self.click_x_spin.setRange(0, 9999)
        click_pos_layout.addWidget(self.click_x_spin, 0, 1)
        
        click_pos_layout.addWidget(QLabel("Y 좌표:"), 1, 0)
        self.click_y_spin = QSpinBox()
        self.click_y_spin.setRange(0, 9999)
        click_pos_layout.addWidget(self.click_y_spin, 1, 1)
        
        click_pos_layout.addWidget(QLabel("클릭 유형:"), 2, 0)
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["좌클릭", "우클릭", "더블클릭"])
        click_pos_layout.addWidget(self.click_type_combo, 2, 1)
        
        self.capture_click_pos_btn = QPushButton("마우스 위치 캡처")
        click_pos_layout.addWidget(self.capture_click_pos_btn, 3, 0, 1, 2)
        
        mouse_click_layout.addLayout(click_pos_layout)
        mouse_click_layout.addStretch()
        
        # 3. 마우스 드래그 & 드롭 탭
        self.drag_drop_tab = QWidget()
        drag_drop_layout = QVBoxLayout(self.drag_drop_tab)
        
        drag_pos_layout = QGridLayout()
        drag_pos_layout.addWidget(QLabel("시작 X:"), 0, 0)
        self.drag_start_x_spin = QSpinBox()
        self.drag_start_x_spin.setRange(0, 9999)
        drag_pos_layout.addWidget(self.drag_start_x_spin, 0, 1)
        
        drag_pos_layout.addWidget(QLabel("시작 Y:"), 1, 0)
        self.drag_start_y_spin = QSpinBox()
        self.drag_start_y_spin.setRange(0, 9999)
        drag_pos_layout.addWidget(self.drag_start_y_spin, 1, 1)
        
        drag_pos_layout.addWidget(QLabel("끝 X:"), 2, 0)
        self.drag_end_x_spin = QSpinBox()
        self.drag_end_x_spin.setRange(0, 9999)
        drag_pos_layout.addWidget(self.drag_end_x_spin, 2, 1)
        
        drag_pos_layout.addWidget(QLabel("끝 Y:"), 3, 0)
        self.drag_end_y_spin = QSpinBox()
        self.drag_end_y_spin.setRange(0, 9999)
        drag_pos_layout.addWidget(self.drag_end_y_spin, 3, 1)
        
        self.capture_drag_start_btn = QPushButton("드래그 시작 위치 캡처")
        drag_pos_layout.addWidget(self.capture_drag_start_btn, 4, 0, 1, 2)
        
        self.capture_drag_end_btn = QPushButton("드래그 끝 위치 캡처")
        drag_pos_layout.addWidget(self.capture_drag_end_btn, 5, 0, 1, 2)
        
        drag_drop_layout.addLayout(drag_pos_layout)
        drag_drop_layout.addStretch()
        
        # 4. 키보드 입력 탭
        self.keyboard_tab = QWidget()
        keyboard_layout = QVBoxLayout(self.keyboard_tab)
        
        keyboard_layout.addWidget(QLabel("입력할 텍스트:"))
        self.keyboard_text = QTextEdit()
        keyboard_layout.addWidget(self.keyboard_text)
        
        # 5. 키 조합 입력 탭
        self.key_combo_tab = QWidget()
        key_combo_layout = QVBoxLayout(self.key_combo_tab)
        
        key_combo_layout.addWidget(QLabel("키 조합 (예: ctrl+c, alt+tab):"))
        self.key_combo_text = QLineEdit()
        key_combo_layout.addWidget(self.key_combo_text)
        key_combo_layout.addWidget(QLabel("여러 키를 동시에 입력하려면 '+' 기호로 구분하세요."))
        key_combo_layout.addStretch()
        
        # 6. 텍스트 리스트 입력 탭
        self.text_list_tab = QWidget()
        text_list_layout = QVBoxLayout(self.text_list_tab)
        
        text_list_layout.addWidget(QLabel("텍스트 리스트:"))
        self.text_list_widget = QListWidget()
        text_list_layout.addWidget(self.text_list_widget)
        
        text_list_buttons = QHBoxLayout()
        self.add_text_btn = QPushButton("추가")
        self.remove_text_btn = QPushButton("삭제")
        self.load_from_file_btn = QPushButton("파일에서 불러오기")
        
        text_list_buttons.addWidget(self.add_text_btn)
        text_list_buttons.addWidget(self.remove_text_btn)
        text_list_buttons.addWidget(self.load_from_file_btn)
        
        text_list_layout.addLayout(text_list_buttons)
        
        # 탭 위젯에 탭 추가
        self.tab_widget.addTab(self.mouse_move_tab, "마우스 이동")
        self.tab_widget.addTab(self.mouse_click_tab, "마우스 클릭")
        self.tab_widget.addTab(self.drag_drop_tab, "드래그 & 드롭")
        self.tab_widget.addTab(self.keyboard_tab, "키보드 입력")
        self.tab_widget.addTab(self.key_combo_tab, "키 조합")
        self.tab_widget.addTab(self.text_list_tab, "텍스트 리스트")
        
        main_layout.addWidget(self.tab_widget)
        
        # 동작 이름
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("동작 이름:"))
        self.action_name_edit = QLineEdit()
        name_layout.addWidget(self.action_name_edit)
        
        main_layout.addLayout(name_layout)
        
        # 확인/취소 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # 이벤트 연결
        self.action_type_combo.currentIndexChanged.connect(self.on_action_type_changed)
        self.capture_pos_btn.clicked.connect(lambda: self.start_capture_mode("move"))
        self.capture_click_pos_btn.clicked.connect(lambda: self.start_capture_mode("click"))
        self.capture_drag_start_btn.clicked.connect(lambda: self.start_capture_mode("drag_start"))
        self.capture_drag_end_btn.clicked.connect(lambda: self.start_capture_mode("drag_end"))
        
        # 텍스트 리스트 관련 이벤트
        self.add_text_btn.clicked.connect(self.add_text_to_list)
        self.remove_text_btn.clicked.connect(self.remove_text_from_list)
        self.load_from_file_btn.clicked.connect(self.load_text_from_file)
        
        # 초기 탭 설정
        self.on_action_type_changed(0)
        
        app_logger.debug("동작 편집 다이얼로그 UI 초기화 완료")
    
    def on_action_type_changed(self, index):
        """
        동작 유형 변경 시 해당 탭으로 전환
        """
        app_logger.log_ui_action("동작 유형 변경", f"새 유형: {self.action_type_combo.currentText()}")
        self.tab_widget.setCurrentIndex(index)
    
    def start_capture_mode(self, mode):
        """
        마우스 위치 캡처 모드 시작
        """
        app_logger.log_ui_action("마우스 위치 캡처 시작", f"모드: {mode}")
        self.capture_mode = mode
        self.setWindowOpacity(0.3)
        self.capture_timer.start(100)  # 100ms마다 위치 업데이트
        
        # 3초 후 자동으로 캡처 모드 종료
        QTimer.singleShot(3000, self.stop_capture_mode)
    
    def stop_capture_mode(self):
        """
        마우스 위치 캡처 모드 종료
        """
        if self.capture_mode:
            app_logger.log_ui_action("마우스 위치 캡처 종료", f"모드: {self.capture_mode}")
            self.capture_timer.stop()
            self.setWindowOpacity(1.0)
            self.capture_mode = False
    
    def update_cursor_position(self):
        """
        현재 커서 위치 업데이트
        """
        pos = QCursor.pos()
        
        if self.capture_mode == "move":
            app_logger.debug(f"마우스 이동 위치 캡처: ({pos.x()}, {pos.y()})")
            self.mouse_x_spin.setValue(pos.x())
            self.mouse_y_spin.setValue(pos.y())
        elif self.capture_mode == "click":
            app_logger.debug(f"마우스 클릭 위치 캡처: ({pos.x()}, {pos.y()})")
            self.click_x_spin.setValue(pos.x())
            self.click_y_spin.setValue(pos.y())
        elif self.capture_mode == "drag_start":
            app_logger.debug(f"드래그 시작 위치 캡처: ({pos.x()}, {pos.y()})")
            self.drag_start_x_spin.setValue(pos.x())
            self.drag_start_y_spin.setValue(pos.y())
        elif self.capture_mode == "drag_end":
            app_logger.debug(f"드래그 끝 위치 캡처: ({pos.x()}, {pos.y()})")
            self.drag_end_x_spin.setValue(pos.x())
            self.drag_end_y_spin.setValue(pos.y())
    
    def add_text_to_list(self):
        """
        텍스트 리스트에 항목 추가
        """
        app_logger.log_ui_action("텍스트 항목 추가 버튼 클릭")
        text, ok = QInputDialog.getText(self, "텍스트 추가", "입력할 텍스트:")
        if ok and text:
            app_logger.debug(f"텍스트 항목 추가: {text}")
            self.text_list_widget.addItem(text)
    
    def remove_text_from_list(self):
        """
        텍스트 리스트에서 선택된 항목 제거
        """
        current_item = self.text_list_widget.currentItem()
        if current_item:
            text = current_item.text()
            row = self.text_list_widget.row(current_item)
            app_logger.log_ui_action("텍스트 항목 삭제", f"항목: {text}, 위치: {row}")
            self.text_list_widget.takeItem(row)
    
    def load_text_from_file(self):
        """
        파일에서 텍스트 리스트 불러오기
        """
        app_logger.log_ui_action("파일에서 텍스트 불러오기 버튼 클릭")
        file_path, _ = QFileDialog.getOpenFileName(self, "텍스트 파일 선택", "", "텍스트 파일 (*.txt);;모든 파일 (*.*)")
        if file_path:
            app_logger.info(f"텍스트 파일 선택: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    count = 0
                    for line in lines:
                        line = line.strip()
                        if line:
                            self.text_list_widget.addItem(line)
                            count += 1
                app_logger.info(f"텍스트 파일에서 {count}개 항목 로드 완료")
            except Exception as e:
                error_msg = f"파일을 불러오는 중 오류가 발생했습니다: {str(e)}"
                app_logger.error(error_msg)
                QMessageBox.warning(self, "오류", error_msg)
    
    def _load_action_data(self, action):
        """
        기존 동작 데이터 로드
        """
        app_logger.debug(f"기존 동작 데이터 로드: {action.name}")
        self.action_name_edit.setText(action.name)
        
        if isinstance(action, MouseMoveAction):
            app_logger.debug(f"마우스 이동 동작 로드: ({action.x}, {action.y})")
            self.action_type_combo.setCurrentIndex(0)
            self.mouse_x_spin.setValue(action.x)
            self.mouse_y_spin.setValue(action.y)
        
        elif isinstance(action, MouseClickAction):
            app_logger.debug(f"마우스 클릭 동작 로드: ({action.x}, {action.y}), 버튼: {action.button}")
            self.action_type_combo.setCurrentIndex(1)
            self.click_x_spin.setValue(action.x)
            self.click_y_spin.setValue(action.y)
            self.click_type_combo.setCurrentIndex(action.button)
        
        elif isinstance(action, MouseDragDropAction):
            app_logger.debug(f"마우스 드래그&드롭 동작 로드: ({action.start_x}, {action.start_y}) -> ({action.end_x}, {action.end_y})")
            self.action_type_combo.setCurrentIndex(2)
            self.drag_start_x_spin.setValue(action.start_x)
            self.drag_start_y_spin.setValue(action.start_y)
            self.drag_end_x_spin.setValue(action.end_x)
            self.drag_end_y_spin.setValue(action.end_y)
        
        elif isinstance(action, KeyboardInputAction):
            app_logger.debug(f"키보드 입력 동작 로드: 텍스트 길이: {len(action.text)}")
            self.action_type_combo.setCurrentIndex(3)
            self.keyboard_text.setText(action.text)
        
        elif isinstance(action, KeyCombinationAction):
            app_logger.debug(f"키 조합 동작 로드: {action.key_combination}")
            self.action_type_combo.setCurrentIndex(4)
            self.key_combo_text.setText(action.key_combination)
        
        elif isinstance(action, TextListInputAction):
            app_logger.debug(f"텍스트 리스트 동작 로드: {len(action.text_list)}개 항목")
            self.action_type_combo.setCurrentIndex(5)
            for text in action.text_list:
                self.text_list_widget.addItem(text)
    
    def get_action(self):
        """
        현재 설정된 동작 객체 반환
        """
        action_type = self.action_type_combo.currentIndex()
        name = self.action_name_edit.text()
        
        if not name:
            name = self.action_type_combo.currentText()
        
        app_logger.info(f"동작 생성 중: {name}, 유형: {self.action_type_combo.currentText()}")
        
        try:
            if action_type == 0:  # 마우스 이동
                x = self.mouse_x_spin.value()
                y = self.mouse_y_spin.value()
                app_logger.debug(f"마우스 이동 동작 생성: ({x}, {y})")
                return MouseMoveAction(
                    name=name,
                    x=x,
                    y=y
                )
            
            elif action_type == 1:  # 마우스 클릭
                x = self.click_x_spin.value()
                y = self.click_y_spin.value()
                button = self.click_type_combo.currentIndex()
                app_logger.debug(f"마우스 클릭 동작 생성: ({x}, {y}), 버튼: {button}")
                return MouseClickAction(
                    name=name,
                    x=x,
                    y=y,
                    button=button
                )
            
            elif action_type == 2:  # 마우스 드래그 & 드롭
                start_x = self.drag_start_x_spin.value()
                start_y = self.drag_start_y_spin.value()
                end_x = self.drag_end_x_spin.value()
                end_y = self.drag_end_y_spin.value()
                app_logger.debug(f"마우스 드래그&드롭 동작 생성: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
                return MouseDragDropAction(
                    name=name,
                    start_x=start_x,
                    start_y=start_y,
                    end_x=end_x,
                    end_y=end_y
                )
            
            elif action_type == 3:  # 키보드 입력
                text = self.keyboard_text.toPlainText()
                app_logger.debug(f"키보드 입력 동작 생성: 텍스트 길이: {len(text)}")
                return KeyboardInputAction(
                    name=name,
                    text=text
                )
            
            elif action_type == 4:  # 키 조합 입력
                key_combination = self.key_combo_text.text()
                app_logger.debug(f"키 조합 동작 생성: {key_combination}")
                return KeyCombinationAction(
                    name=name,
                    key_combination=key_combination
                )
            
            elif action_type == 5:  # 텍스트 리스트 입력
                text_list = []
                for i in range(self.text_list_widget.count()):
                    text_list.append(self.text_list_widget.item(i).text())
                
                app_logger.debug(f"텍스트 리스트 동작 생성: {len(text_list)}개 항목")
                return TextListInputAction(
                    name=name,
                    text_list=text_list
                )
        
        except Exception as e:
            app_logger.error(f"동작 생성 중 오류 발생: {str(e)}", exc_info=True)
            return None
        
        return None
    
    def accept(self):
        """
        다이얼로그 확인 버튼 클릭 시 처리
        """
        app_logger.log_ui_action("동작 편집 확인 버튼 클릭")
        
        # 유효성 검사
        action_type = self.action_type_combo.currentIndex()
        
        if action_type == 5 and self.text_list_widget.count() == 0:
            app_logger.warning("텍스트 리스트가 비어 있음")
            QMessageBox.warning(self, "경고", "텍스트 리스트에 항목을 추가해주세요.")
            return
        
        super().accept()
    
    def reject(self):
        """
        다이얼로그 취소 버튼 클릭 시 처리
        """
        app_logger.log_ui_action("동작 편집 취소 버튼 클릭")
        super().reject()