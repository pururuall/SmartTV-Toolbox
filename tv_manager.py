# -*- coding: utf-8 -*-
"""
tv_manager.py — тонкий фасад (Bridge) для обратной совместимости.
Экспортирует класс SmartTVManager и вспомогательные структуры из пакета core.
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from core import (
    SmartTVManager,
    AdbClientMixin,
    DebloatMixin,
    AppsInstallerMixin,
    UIBridgeMixin,
    KNOWN_TV_PACKAGES,
    CLEANYOURTV_PRESETS,
    CLEANYOURTV_KEYS_SCHEMA,
)

# Обратная совместимость для скриптов CLI/Tkinter/сервера
_default_mgr = SmartTVManager()
ADB = _default_mgr.adb_bin
APPS_DIR = str(_default_mgr.base_dir / 'apps')
PRESETS = _default_mgr.packages_db.get('profiles', {})

__all__ = [
    'SmartTVManager',
    'AdbClientMixin',
    'DebloatMixin',
    'AppsInstallerMixin',
    'UIBridgeMixin',
    'KNOWN_TV_PACKAGES',
    'CLEANYOURTV_PRESETS',
    'CLEANYOURTV_KEYS_SCHEMA',
    'ADB',
    'APPS_DIR',
    'PRESETS',
]
