# CLAUDE.md — SmartTV_Toolbox

Инструкции и правила поведения для Claude Code и других ИИ-агентов.
Смотри подробное руководство в [AGENTS.md](AGENTS.md).

## Краткие правила Karpathy Guidelines для проекта:
1. **Surgical Changes**: Не коммитить `*.exe`, `dist/`, `build/`, `*.spec`. Все временные скрипты и логи создавать только в `.scratch/`.
2. **Simplicity First**: Не дублировать APK и HTML (`app_ui.html` — единственный источник правды).
3. **Goal-Driven Execution**: Перед коммитом валидировать код: `python -m py_compile <измененные_файлы>`.
4. **Think Before Coding**: Согласовывать архитектурные изменения и удаление файлов.
