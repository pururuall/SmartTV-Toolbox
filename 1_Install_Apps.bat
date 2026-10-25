@echo off
chcp 65001 >nul
cd /d "%~dp0"
python tv_manager.py install
pause
