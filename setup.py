#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="macro-app",
    version="0.1.0",
    description="macro_proj",
    author="doyoung42",
    packages=find_packages(),
    install_requires=[
        "pyqt5==5.15.7",
        "pyautogui==0.9.53",
        "keyboard==0.13.5",
        "pynput==1.7.6",
        "pyperclip==1.8.2",
        "watchdog==2.2.1",
    ],
    python_requires=">=3.9,<3.11",
    entry_points={
        "console_scripts": [
            "macro-app=main:main",
        ],
    },
    options={
        'build_exe': {
            'excludes': ['__pycache__'],
        }
    }
)