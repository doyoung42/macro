#!/usr/bin/env python
# -*- coding: utf-8 -*-
# utils/config.py

import os
import json
from PyQt5.QtCore import QObject, QDir
from utils.logger import app_logger

class Config(QObject):
    """
    애플리케이션 설정을 관리하는 클래스
    """
    def __init__(self):
        super().__init__()
        
        # 설정 파일 경로
        self.config_dir = os.path.join(QDir.homePath(), ".macro_app")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        app_logger.debug(f"설정 디렉토리: {self.config_dir}")
        app_logger.debug(f"설정 파일: {self.config_file}")
        
        # 기본 설정값
        self.settings = {
            "window": {
                "width": 800,
                "height": 600,
                "x": 100,
                "y": 100
            },
            "macro": {
                "delay": 100,
                "loop_count": 1,
                "stop_key": "f12"
            },
            "clipboard": {
                "enabled": False,
                "output_file": ""
            },
            "folder_monitor": {
                "enabled": False,
                "folder_path": ""
            },
            "recent_files": []
        }
        
        # 설정 로드
        self._ensure_config_dir()
        self.load()
        
        app_logger.info("설정 매니저 초기화 완료")
    
    def _ensure_config_dir(self):
        """
        설정 디렉토리 확인 및 생성
        """
        if not os.path.exists(self.config_dir):
            app_logger.info(f"설정 디렉토리 생성: {self.config_dir}")
            os.makedirs(self.config_dir)
    
    def load(self):
        """
        설정 파일에서 설정 로드
        """
        try:
            if os.path.exists(self.config_file):
                app_logger.info(f"설정 파일 로드: {self.config_file}")
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # 기존 설정에 로드된 설정 병합
                    self._merge_settings(self.settings, loaded_settings)
                app_logger.debug("설정 로드 완료")
            else:
                app_logger.info("설정 파일이 존재하지 않음, 기본 설정 사용")
        except Exception as e:
            error_msg = f"설정 로드 중 오류 발생: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
            app_logger.warning("기본 설정 사용")
    
    def save(self):
        """
        설정을 파일에 저장
        """
        try:
            app_logger.info(f"설정 저장: {self.config_file}")
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            app_logger.debug("설정 저장 완료")
        except Exception as e:
            error_msg = f"설정 저장 중 오류 발생: {str(e)}"
            app_logger.error(error_msg, exc_info=True)
    
    def _merge_settings(self, target, source):
        """
        두 설정 사전을 병합
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_settings(target[key], value)
            else:
                target[key] = value
    
    def get(self, section, key, default=None):
        """
        설정값 조회
        """
        try:
            value = self.settings[section][key]
            app_logger.debug(f"설정 조회: {section}.{key} = {value}")
            return value
        except KeyError:
            app_logger.debug(f"설정 조회 실패 (기본값 사용): {section}.{key} = {default}")
            return default
    
    def set(self, section, key, value):
        """
        설정값 설정
        """
        app_logger.debug(f"설정 변경: {section}.{key} = {value}")
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section][key] = value
    
    def add_recent_file(self, file_path):
        """
        최근 파일 목록에 파일 추가
        """
        app_logger.debug(f"최근 파일 추가: {file_path}")
        recent_files = self.settings.get("recent_files", [])
        
        # 이미 있는 경우 제거 후 맨 앞에 추가
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # 맨 앞에 추가
        recent_files.insert(0, file_path)
        
        # 최대 10개만 유지
        self.settings["recent_files"] = recent_files[:10]
    
    def get_recent_files(self):
        """
        최근 파일 목록 조회
        """
        recent_files = self.settings.get("recent_files", [])
        app_logger.debug(f"최근 파일 목록 조회: {len(recent_files)}개")
        return recent_files