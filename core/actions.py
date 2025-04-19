#!/usr/bin/env python
# -*- coding: utf-8 -*-
# core/actions.py


from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import QObject
from utils.logger import app_logger

class MacroAction(QObject):
    """
    매크로 동작의 기본 추상 클래스
    """
    def __init__(self, name="동작"):
        super().__init__()
        self.name = name
        
        # PyAutoGUI FailSafe 비활성화
        try:
            import pyautogui
            pyautogui.FAILSAFE = False
        except:
            pass
    
    def execute(self):
        """
        동작 실행 메서드 (하위 클래스에서 구현)
        """
        raise NotImplementedError("서브클래스에서 구현해야 합니다.")
    
    def to_list_item(self):
        """
        리스트 위젯 아이템으로 변환
        """
        item = QListWidgetItem(self.name)
        item.setToolTip(self.get_description())
        return item
    
    def get_description(self):
        """
        동작 설명 반환 (하위 클래스에서 구현)
        """
        return self.name
    
    def to_dict(self):
        """
        동작을 딕셔너리로 변환 (JSON 저장용)
        """
        return {
            "type": self.__class__.__name__,
            "name": self.name
        }
    
    @staticmethod
    def from_dict(data):
        """
        딕셔너리에서 동작 객체 생성 (JSON 로드용)
        """
        action_type = data.get("type", "")
        
        if action_type == "MouseMoveAction":
            return MouseMoveAction(
                name=data.get("name", "마우스 이동"),
                x=data.get("x", 0),
                y=data.get("y", 0)
            )
        elif action_type == "MouseClickAction":
            return MouseClickAction(
                name=data.get("name", "마우스 클릭"),
                x=data.get("x", 0),
                y=data.get("y", 0),
                button=data.get("button", 0)
            )
        elif action_type == "MouseDragDropAction":
            return MouseDragDropAction(
                name=data.get("name", "드래그 & 드롭"),
                start_x=data.get("start_x", 0),
                start_y=data.get("start_y", 0),
                end_x=data.get("end_x", 0),
                end_y=data.get("end_y", 0)
            )
        elif action_type == "KeyboardInputAction":
            return KeyboardInputAction(
                name=data.get("name", "키보드 입력"),
                text=data.get("text", "")
            )
        elif action_type == "KeyCombinationAction":
            return KeyCombinationAction(
                name=data.get("name", "키 조합"),
                key_combination=data.get("key_combination", "")
            )
        elif action_type == "TextListInputAction":
            return TextListInputAction(
                name=data.get("name", "텍스트 리스트 입력"),
                text_list=data.get("text_list", [])
            )
        else:
            app_logger.warning(f"알 수 없는 동작 유형: {action_type}")
            return None

class MouseMoveAction(MacroAction):
    """
    마우스 이동 동작
    """
    def __init__(self, x=0, y=0, name="마우스 이동"):
        super().__init__(name)
        self.x = x
        self.y = y
    
    def execute(self):
        """
        마우스를 지정된 좌표로 이동
        """
        try:
            import pyautogui
            app_logger.debug(f"마우스 이동: ({self.x}, {self.y})")
            pyautogui.moveTo(self.x, self.y)
            return True
        except Exception as e:
            app_logger.error(f"마우스 이동 실패: {str(e)}", exc_info=True)
            return False
    
    def get_description(self):
        """
        동작 설명 반환
        """
        return f"마우스 좌표 ({self.x}, {self.y})로 이동"
    
    def to_dict(self):
        """
        동작을 딕셔너리로 변환
        """
        data = super().to_dict()
        data.update({
            "x": self.x,
            "y": self.y
        })
        return data



class MouseClickAction(MacroAction):
    """
    마우스 클릭 동작
    """
    def __init__(self, x=0, y=0, button=0, name="마우스 클릭"):
        """
        button: 0=좌클릭, 1=우클릭, 2=더블클릭
        """
        super().__init__(name)
        self.x = x
        self.y = y
        self.button = button
    
    def execute(self):
        """
        지정된 위치에서 마우스 클릭 실행
        """
        try:
            import pyautogui
            button_names = ["left", "right", "double"]
            button_type = button_names[self.button] if self.button < len(button_names) else "left"
            
            app_logger.debug(f"마우스 이동: ({self.x}, {self.y})")
            pyautogui.moveTo(self.x, self.y)
            
            if self.button == 0:  # 좌클릭
                app_logger.debug("좌클릭 실행")
                pyautogui.click(button='left')
            elif self.button == 1:  # 우클릭
                app_logger.debug("우클릭 실행")
                pyautogui.click(button='right')
            elif self.button == 2:  # 더블클릭
                app_logger.debug("더블클릭 실행")
                pyautogui.doubleClick()
            
            return True
        except Exception as e:
            app_logger.error(f"마우스 클릭 실패: {str(e)}", exc_info=True)
            return False
    
    def get_description(self):
        """
        동작 설명 반환
        """
        button_names = ["좌클릭", "우클릭", "더블클릭"]
        button_type = button_names[self.button] if self.button < len(button_names) else "좌클릭"
        return f"좌표 ({self.x}, {self.y})에서 {button_type}"
    
    def to_dict(self):
        """
        동작을 딕셔너리로 변환
        """
        data = super().to_dict()
        data.update({
            "x": self.x,
            "y": self.y,
            "button": self.button
        })
        return data



class MouseDragDropAction(MacroAction):
    """
    마우스 드래그 앤 드롭 동작
    """
    def __init__(self, start_x=0, start_y=0, end_x=0, end_y=0, name="드래그 & 드롭"):
        super().__init__(name)
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
    
    def execute(self):
        """
        드래그 앤 드롭 실행
        """
        try:
            import pyautogui
            app_logger.debug(f"드래그 시작: ({self.start_x}, {self.start_y})")
            pyautogui.moveTo(self.start_x, self.start_y)
            pyautogui.mouseDown(button='left')
            
            app_logger.debug(f"드래그 종료: ({self.end_x}, {self.end_y})")
            pyautogui.moveTo(self.end_x, self.end_y)
            pyautogui.mouseUp(button='left')
            
            return True
        except Exception as e:
            app_logger.error(f"드래그 앤 드롭 실패: {str(e)}", exc_info=True)
            return False
    
    def get_description(self):
        """
        동작 설명 반환
        """
        return f"좌표 ({self.start_x}, {self.start_y})에서 ({self.end_x}, {self.end_y})로 드래그"
    
    def to_dict(self):
        """
        동작을 딕셔너리로 변환
        """
        data = super().to_dict()
        data.update({
            "start_x": self.start_x,
            "start_y": self.start_y,
            "end_x": self.end_x,
            "end_y": self.end_y
        })
        return data


class KeyboardInputAction(MacroAction):
    """
    키보드 입력 동작
    """
    def __init__(self, text="", name="키보드 입력"):
        super().__init__(name)
        self.text = text
    
    def execute(self):
        """
        텍스트 입력 실행
        """
        try:
            import pyautogui
            preview = self.text[:20] + "..." if len(self.text) > 20 else self.text
            app_logger.debug(f"키보드 입력: {preview}")
            
            # issue 5
            # 입력 딜레이 설정 - 너무 빠른 입력으로 인한 중복 문제 해결
            pyautogui.PAUSE = 0.05
            pyautogui.write(self.text, interval=0.05)
            return True
        except Exception as e:
            app_logger.error(f"키보드 입력 실패: {str(e)}", exc_info=True)
            return False
        
    def to_dict(self):
        """
        동작을 딕셔너리로 변환
        """
        data = super().to_dict()
        data.update({
            "text": self.text
        })
        return data

class KeyCombinationAction(MacroAction):
    """
    키 조합 입력 동작
    """
    def __init__(self, key_combination="", name="키 조합"):
        super().__init__(name)
        self.key_combination = key_combination
    
    def execute(self):
        """
        키 조합 입력 실행
        """
        try:
            import pyautogui
            keys = self.key_combination.split('+')
            keys = [key.strip() for key in keys]
            
            app_logger.debug(f"키 조합 입력: {self.key_combination}")
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            app_logger.error(f"키 조합 입력 실패: {str(e)}", exc_info=True)
            return False
    
    def get_description(self):
        """
        동작 설명 반환
        """
        return f"키 조합: {self.key_combination}"

    def to_dict(self):
        """
        동작을 딕셔너리로 변환
        """
        data = super().to_dict()
        data.update({
            "key_combination": self.key_combination
        })
        return data


class TextListInputAction(MacroAction):
    """
    텍스트 리스트 입력 동작
    """
    def __init__(self, text_list=None, name="텍스트 리스트 입력"):
        super().__init__(name)
        self.text_list = text_list or []
        self.current_index = 0
    
    def execute(self):
        """
        현재 텍스트 리스트에서 다음 항목 입력
        """
        if not self.text_list:
            app_logger.warning("텍스트 리스트가 비어 있음")
            return False
        
        try:
            # 현재 인덱스에 해당하는 텍스트 입력
            import pyautogui
            text = self.text_list[self.current_index]
            preview = text[:20] + "..." if len(text) > 20 else text
            
            app_logger.debug(f"텍스트 리스트 입력: [{self.current_index+1}/{len(self.text_list)}] {preview}")
            
            # 한글/영어 입력 문제 해결
            # 클립보드를 활용한 입력 방식으로 변경
            import pyperclip
            
            # 원래 클립보드 내용 백업
            original_clipboard = pyperclip.paste()
            
            # 텍스트를 클립보드에 복사
            pyperclip.copy(text)
            
            # Ctrl+V로 붙여넣기 (키보드 입력 대신)
            pyautogui.hotkey('ctrl', 'v')
            
            # 원래 클립보드 내용 복원
            pyperclip.copy(original_clipboard)
            
            # 다음 텍스트 항목으로 인덱스 이동 (순환)
            self.current_index = (self.current_index + 1) % len(self.text_list)
            
            return True
        except Exception as e:
            app_logger.error(f"텍스트 리스트 입력 실패: {str(e)}", exc_info=True)
            return False
    
    def reset(self):
        """
        인덱스 초기화
        """
        app_logger.debug("텍스트 리스트 인덱스 초기화")
        self.current_index = 0
    
    def get_description(self):
        """
        동작 설명 반환
        """
        if not self.text_list:
            return "텍스트 리스트: (비어 있음)"
        
        count = len(self.text_list)
        preview = self.text_list[0]
        if len(preview) > 15:
            preview = preview[:15] + "..."
        
        if count > 1:
            return f"텍스트 리스트: '{preview}' 외 {count-1}개 항목"
        else:
            return f"텍스트 리스트: '{preview}'"
    
    def get_items_count(self):
        """
        텍스트 리스트 항목 개수 반환
        """
        return len(self.text_list)
    
    def to_dict(self):
        """
        동작을 딕셔너리로 변환
        """
        data = super().to_dict()
        data.update({
            "text_list": self.text_list
        })
        return data
