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
        elif action_type == "DelayAction":
            return DelayAction(
                name=data.get("name", "지연 시간"),
                delay=data.get("delay", 1000)
            )
        elif action_type == "ClipboardSaveAction":
            return ClipboardSaveAction(
                name=data.get("name", "클립보드 저장"),
                output_file=data.get("output_file", "")
            )
        elif action_type == "FolderMonitorAction":
            action = FolderMonitorAction(
                name=data.get("name", "폴더 모니터링"),
                folder_path=data.get("folder_path", "")
            )
            action.filename_template = data.get("filename_template", "clipboard.txt")
            return action
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
            keys = [key.strip().lower() for key in keys]  # 모든 키를 소문자로 변환
            
            app_logger.debug(f"키 조합 입력: {self.key_combination}")
            
            # Ctrl+C 처리 - 클립보드 클리어 필요
            if len(keys) == 2 and keys[0] in ['ctrl', 'control'] and keys[1] == 'c':
                app_logger.debug("복사(Ctrl+C) 동작 감지 - 클립보드 클리어 후 동작 실행")
                try:
                    import pyperclip
                    # 클립보드 비우기
                    pyperclip.copy('')
                    app_logger.debug("클립보드 내용 클리어 완료")
                except Exception as e:
                    app_logger.error(f"클립보드 클리어 실패: {str(e)}", exc_info=True)
                    
                # 키 조합 실행
                pyautogui.hotkey(*keys)
                
            # Ctrl+V 또는 기타 키 조합 처리 - 클립보드 유지
            else:
                # 키 조합 실행
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
        키 조합 입력 실행
        """
        try:
            import pyautogui
            keys = self.key_combination.split('+')
            keys = [key.strip().lower() for key in keys]  # 소문자로 변환하여 처리
            
            app_logger.debug(f"키 조합 입력: {self.key_combination}")
            
            # Ctrl+V 처리를 위한 특별 로직
            if len(keys) == 2 and keys[0] in ['ctrl', 'control'] and keys[1] == 'v':
                app_logger.debug("클립보드 붙여넣기 기능 사용")
                pyautogui.hotkey('ctrl', 'v')
            else:
                pyautogui.hotkey(*keys)
            
            return True
        except Exception as e:
            app_logger.error(f"키 조합 입력 실패: {str(e)}", exc_info=True)
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

class DelayAction(MacroAction):
    """
    지연 시간 동작
    """
    def __init__(self, delay=1000, name="지연"):
        super().__init__(name)
        self.delay = delay  # ms
    
    def execute(self):
        """
        지연 시간 실행
        """
        try:
            delay_sec = self.delay / 1000.0
            app_logger.debug(f"지연 시간 실행: {self.delay}ms ({delay_sec:.2f}초)")
            time.sleep(delay_sec)
            return True
        except Exception as e:
            app_logger.error(f"지연 시간 실행 실패: {str(e)}", exc_info=True)
            return False
    
    def get_description(self):
        """
        동작 설명 반환
        """
        return f"지연 시간: {self.delay}ms"
    
    def to_dict(self):
        """
        동작을 딕셔너리로 변환
        """
        data = super().to_dict()
        data.update({
            "delay": self.delay
        })
        return data
    
class ClipboardSaveAction(MacroAction):
    """
    클립보드 내용 저장 동작
    """
    def __init__(self, output_file="", name="클립보드 저장"):
        super().__init__(name)
        self.output_file = output_file
        self.clipboard_manager = None
    
    def execute(self):
        """
        클립보드 저장 시작
        """
        try:
            from core.clipboard_manager import ClipboardManager
            
            app_logger.debug(f"클립보드 저장 시작: {self.output_file}")
            
            # 클립보드 매니저 초기화 및 시작
            self.clipboard_manager = ClipboardManager()
            self.clipboard_manager.set_output_file(self.output_file)
            self.clipboard_manager.start_monitoring()
            
            return True
        except Exception as e:
            app_logger.error(f"클립보드 저장 실패: {str(e)}", exc_info=True)
            return False
    
    def get_description(self):
        """
        동작 설명 반환
        """
        return f"클립보드 저장: {self.output_file}"
    
    def to_dict(self):
        """
        동작을 딕셔너리로 변환
        """
        data = super().to_dict()
        data.update({
            "output_file": self.output_file
        })
        return data

class FolderMonitorAction(MacroAction):
    """
    폴더 모니터링 동작
    """
    def __init__(self, folder_path="", name="폴더 모니터링"):
        super().__init__(name)
        self.folder_path = folder_path
        self.folder_monitor = None
        self.filename_template = "clipboard.txt"  # 기본 파일명
    
    def execute(self):
        """
        폴더 모니터링 시작
        """
        try:
            from core.folder_monitor import FolderMonitor
            
            app_logger.debug(f"폴더 모니터링 시작: {self.folder_path}, 파일명: {self.filename_template}")
            
            # 폴더 모니터 초기화 및 시작
            self.folder_monitor = FolderMonitor()
            self.folder_monitor.set_folder_path(self.folder_path)
            self.folder_monitor.set_filename_template(self.filename_template)
            self.folder_monitor.start_monitoring()
            
            return True
        except Exception as e:
            app_logger.error(f"폴더 모니터링 실패: {str(e)}", exc_info=True)
            return False
    
    def get_description(self):
        """
        동작 설명 반환
        """
        return f"폴더 모니터링: {self.folder_path} (파일명: {self.filename_template})"
    
    def to_dict(self):
        """
        동작을 딕셔너리로 변환
        """
        data = super().to_dict()
        data.update({
            "folder_path": self.folder_path,
            "filename_template": self.filename_template
        })
        return data