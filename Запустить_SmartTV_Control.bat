@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Smart TV Control Launcher

:: Снимаем метку блокировки Windows SmartScreen с exe, если есть
powershell -NoProfile -Command "Unblock-File -Path '%~dp0SmartTV_Control.exe' -ErrorAction SilentlyContinue" >nul 2>nul

if exist "%~dp0SmartTV_Control.exe" (
    start "" "%~dp0SmartTV_Control.exe"
    exit
) else (
    echo [ОШИБКА] Файл SmartTV_Control.exe не найден в папке!
    pause
)
