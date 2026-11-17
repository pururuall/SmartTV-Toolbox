# -*- coding: utf-8 -*-
"""
Smart TV Toolbox Core Package
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.adb_client import AdbClientMixin
from core.debloat import DebloatMixin, KNOWN_TV_PACKAGES
from core.apps_installer import AppsInstallerMixin
from core.ui_bridge import UIBridgeMixin, CLEANYOURTV_PRESETS, CLEANYOURTV_KEYS_SCHEMA


class SmartTVManager(AdbClientMixin, DebloatMixin, AppsInstallerMixin, UIBridgeMixin):
    """
    Единый менеджер управления Smart TV, объединяющий подсистемы ADB,
    деблоата, установки APK и интерфейсного моста.
    """
    def __init__(self, base_dir: Optional[str] = None):

        if base_dir:

            self.base_dir = Path(base_dir)

            self.exe_dir = self.base_dir

            self.meipass_dir = self.base_dir

        elif getattr(sys, 'frozen', False):

            self.exe_dir = Path(os.path.dirname(sys.executable))

            self.meipass_dir = Path(getattr(sys, '_MEIPASS', self.exe_dir))

            self.base_dir = self.exe_dir if (self.exe_dir / "data" / "packages.json").exists() else self.meipass_dir

        else:

            self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))

            self.exe_dir = self.base_dir

            self.meipass_dir = self.base_dir



        self.adb_bin = self._resolve_adb_binary()

        self.current_device: Optional[str] = None



        self.packages_db = self._load_json(self._resolve_file("data/packages.json"))

        self.launchers_db = self._load_json(self._resolve_file("data/launchers.json"))

        self.backups_dir = self.exe_dir / "backups"

        try:

            self.backups_dir.mkdir(exist_ok=True)

        except Exception:

            self.backups_dir = self.base_dir / "backups"

            self.backups_dir.mkdir(exist_ok=True)


__all__ = [
    'SmartTVManager',
    'AdbClientMixin',
    'DebloatMixin',
    'AppsInstallerMixin',
    'UIBridgeMixin',
    'KNOWN_TV_PACKAGES',
    'CLEANYOURTV_PRESETS',
    'CLEANYOURTV_KEYS_SCHEMA',
]
