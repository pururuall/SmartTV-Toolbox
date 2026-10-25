@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Поиск Python: сначала проверяем встроенный python-embed, затем системный
set "PY_CMD="
if exist "%~dp0python-embed\python.exe" (
    set "PY_CMD=%~dp0python-embed\python.exe"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "PY_CMD=python"
    )
)

if "%PY_CMD%"=="" (
    echo [ОШИБКА] Python не найден!
    echo Убедитесь, что папка python-embed находится рядом со скриптом.
    pause
    exit /b 1
)

"%PY_CMD%" tv_manager.py light_debloat
pause
