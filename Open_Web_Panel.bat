@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Запуск интерактивной панели Smart TV Toolbox...
python server.py
pause
