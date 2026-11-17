@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Smart TV Control Launcher

:: 1. Проверяем скомпилированный EXE в папке dist (рекомендованное расположение)
if exist "%~dp0dist\SmartTV_Control.exe" (
    powershell -NoProfile -Command "Unblock-File -Path '%~dp0dist\SmartTV_Control.exe' -ErrorAction SilentlyContinue" >nul 2>nul
    start "" "%~dp0dist\SmartTV_Control.exe"
    exit /b 0
)

:: 2. Проверяем EXE в корне проекта (для обратной совместимости)
if exist "%~dp0SmartTV_Control.exe" (
    powershell -NoProfile -Command "Unblock-File -Path '%~dp0SmartTV_Control.exe' -ErrorAction SilentlyContinue" >nul 2>nul
    start "" "%~dp0SmartTV_Control.exe"
    exit /b 0
)

:: 3. Если EXE не скомпилирован, запускаем через Python
echo [ИНФО] Скомпилированный EXE не найден в dist/ или корне проекта.
echo [ИНФО] Запуск Smart TV Toolbox через Python...

:: Поиск Python: сначала системный (с поддержкой pywebview), затем embedded
set "PY_CMD="
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=python"
) else (
    if exist "%~dp0python-embed\python.exe" (
        set "PY_CMD=%~dp0python-embed\python.exe"
    )
)

if "%PY_CMD%"=="" (
    echo [ОШИБКА] Не удалось запустить SmartTV_Control!
    echo Не найден ни скомпилированный SmartTV_Control.exe, ни установленный Python.
    echo Установите Python или соберите EXE через PyInstaller.
    pause
    exit /b 1
)

:: Пробуем запустить нативное окно через main_webview.py
"%PY_CMD%" -c "import webview" >nul 2>nul
if %errorlevel% equ 0 (
    start "" "%PY_CMD%" main_webview.py
    exit /b 0
)

:: Если pywebview не установлен, запускаем локальный сервер и открываем браузер
echo [ИНФО] Модуль pywebview не найден, запуск веб-сервера через server.py...
start "" "%PY_CMD%" server.py
exit /b 0
