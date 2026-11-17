# -*- coding: utf-8 -*-
"""
Smoke Tests for Smart TV Toolbox
Проверка успешного импорта всех модулей, валидности структуры классов,
наличия обязательных методов и обратной совместимости.
"""
import os
import sys
import unittest
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestSmokeModules(unittest.TestCase):
    """Тестирование импорта модулей пакета core и фасада tv_manager."""

    def test_01_import_core_submodules(self):
        """Проверка импорта подмодулей core/."""
        from core.adb_client import AdbClientMixin
        from core.debloat import DebloatMixin, KNOWN_TV_PACKAGES
        from core.apps_installer import AppsInstallerMixin
        from core.ui_bridge import UIBridgeMixin, CLEANYOURTV_PRESETS, CLEANYOURTV_KEYS_SCHEMA

        self.assertTrue(isinstance(KNOWN_TV_PACKAGES, dict))
        self.assertGreater(len(KNOWN_TV_PACKAGES), 30)
        self.assertTrue(isinstance(CLEANYOURTV_PRESETS, dict))
        self.assertTrue(isinstance(CLEANYOURTV_KEYS_SCHEMA, list))

    def test_02_import_core_manager(self):
        """Проверка импорта SmartTVManager из пакета core."""
        from core import SmartTVManager
        from core.adb_client import AdbClientMixin
        from core.debloat import DebloatMixin
        from core.apps_installer import AppsInstallerMixin
        from core.ui_bridge import UIBridgeMixin

        # Проверка наследования всех миксинов
        self.assertTrue(issubclass(SmartTVManager, AdbClientMixin))
        self.assertTrue(issubclass(SmartTVManager, DebloatMixin))
        self.assertTrue(issubclass(SmartTVManager, AppsInstallerMixin))
        self.assertTrue(issubclass(SmartTVManager, UIBridgeMixin))

    def test_03_facade_backward_compatibility(self):
        """Проверка фасада tv_manager.py на полную обратную совместимость."""
        import tv_manager
        from tv_manager import (
            SmartTVManager as FacadeManager,
            KNOWN_TV_PACKAGES,
            CLEANYOURTV_PRESETS,
            CLEANYOURTV_KEYS_SCHEMA,
            ADB,
            APPS_DIR,
            PRESETS,
        )
        from core import SmartTVManager as CoreManager

        self.assertIs(FacadeManager, CoreManager)
        self.assertIsNotNone(ADB)
        self.assertIsNotNone(APPS_DIR)
        self.assertTrue(isinstance(PRESETS, dict))
        self.assertTrue(hasattr(tv_manager, 'SmartTVManager'))

    def test_04_manager_instance_initialization(self):
        """Проверка инициализации экземпляра SmartTVManager и его атрибутов."""
        from tv_manager import SmartTVManager

        mgr = SmartTVManager(base_dir=str(PROJECT_ROOT))
        self.assertIsNotNone(mgr.base_dir)
        self.assertIsNotNone(mgr.exe_dir)
        self.assertIsNotNone(mgr.adb_bin)
        self.assertIsNone(mgr.current_device)
        self.assertTrue(isinstance(mgr.packages_db, dict))
        self.assertTrue(isinstance(mgr.launchers_db, dict))
        self.assertTrue(mgr.backups_dir.exists())

    def test_05_public_methods_presence(self):
        """Проверка наличия всех 47 публичных и ключевых методов на экземпляре."""
        from tv_manager import SmartTVManager

        mgr = SmartTVManager(base_dir=str(PROJECT_ROOT))
        expected_methods = [
            # ADB Client
            '_resolve_adb_binary',
            'run_adb',
            'run_raw_adb',
            'connect_tv',
            'wireless_pair',
            '_get_known_devices_file',
            'get_known_devices',
            'save_known_device',
            'set_device_nickname',
            'scan_network',
            '_get_last_known_ip',
            'capture_tv_screenshot',
            # Debloat
            '_detect_profile',
            'create_state_backup',
            'apply_custom_debloat',
            'restore_from_backup',
            'scan_running_processes',
            'stop_running_processes',
            'freeze_processes',
            'unfreeze_processes',
            'clean_tv_ram',
            'purge_yandex_services',
            # Apps Installer
            'is_valid_apk',
            'resolve_apk',
            'install_and_activate_launcher',
            'push_launcher_wallpaper',
            'setup_tv_web_remote',
            'setup_smarttube_and_bypass',
            'install_batch_apps',
            'install_apk_file',
            'list_installed_third_party',
            'get_vpn_status',
            'install_vpn_client',
            'push_wireguard_conf',
            'import_happ_subscription',
            'get_installed_tv_apps',
            # UI Bridge
            '_resolve_file',
            '_load_json',
            '_notify',
            'inspect_device',
            'get_memory_stats',
            'save_launcher_config',
            'get_cleanyourtv_config',
            'save_cleanyourtv_config',
            'reset_cleanyourtv_to_factory',
            'reset_cleanyourtv_config',
        ]

        for method_name in expected_methods:
            self.assertTrue(
                hasattr(mgr, method_name),
                f"Метод {method_name} отсутствует в SmartTVManager!"
            )
            self.assertTrue(
                callable(getattr(mgr, method_name)),
                f"Атрибут {method_name} не является вызываемым методом!"
            )

    def test_06_webview_and_server_bridge_compatibility(self):
        """Проверка совместимости с server.py и main_webview.py."""
        import server
        self.assertTrue(hasattr(server, 'SmartTVManager'))

        try:
            import webview
            from main_webview import WebViewBridge
            bridge = WebViewBridge()
            self.assertIsNotNone(bridge.manager)
            self.assertTrue(hasattr(bridge, 'connect'))
            self.assertTrue(hasattr(bridge, 'clean_tv_ram'))
            self.assertTrue(hasattr(bridge, 'get_cleanyourtv_config'))
        except ModuleNotFoundError:
            # webview опционален в минимальном автономном окружении
            pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
