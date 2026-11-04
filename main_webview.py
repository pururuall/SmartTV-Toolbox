# -*- coding: utf-8 -*-
import os
import sys
import shutil
import webview
import subprocess
import time
import socket
import json

import tv_manager

# Path resolution for PyInstaller
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    MEIPASS_DIR = getattr(sys, '_MEIPASS', BASE_DIR)
    if os.path.exists(os.path.join(BASE_DIR, "app_ui.html")):
        HTML_FILE = os.path.join(BASE_DIR, "app_ui.html")
    else:
        HTML_FILE = os.path.join(MEIPASS_DIR, "app_ui.html")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    HTML_FILE = os.path.join(BASE_DIR, "app_ui.html")

class SmartTV_API:
    def __init__(self):
        self._window = None
        self.cached_ip = None
        tv_manager.set_logger(self._log_js)

    def set_window(self, window):
        self._window = window

    def _log_js(self, msg):
        if self._window:
            safe = str(msg).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '<br>')
            try:
                self._window.evaluate_js(f'addLog("{safe}")')
            except Exception:
                pass

    def connect_tv(self, manual_ip=None):
        clean_ip = manual_ip.strip() if (manual_ip and manual_ip.strip() and manual_ip.strip().lower() != 'автопоиск') else None
        ip = tv_manager.connect_adb(clean_ip)
        if ip:
            self.cached_ip = ip
            return ip, None
        return None, "Не удалось подключиться к телевизору. Проверьте сеть и включение отладки на ТВ."

    def test_connection(self, manual_ip=None):
        try:
            self._log_js("Запуск проверки соединения...")
            clean_ip = manual_ip.strip() if (manual_ip and manual_ip.strip() and manual_ip.strip().lower() != 'автопоиск') else None
            data = tv_manager.action_test_connection(clean_ip)
            if not data:
                return {
                    "success": False,
                    "message": "Не удалось подключиться к телевизору.",
                    "details": "Убедитесь, что телевизор включен, подключен к тому же Wi-Fi и на нем разрешена сетевая отладка (ADB)."
                }
            self.cached_ip = data.get("ip")
            return {
                "success": True,
                "ip": data.get("ip"),
                "brand": data.get("brand"),
                "model": data.get("model"),
                "android": data.get("android"),
                "launcher": data.get("launcher"),
                "dns_mode": data.get("dns_mode"),
                "dns_specifier": data.get("dns_specifier")
            }
        except Exception as e:
            self._log_js(f"Критическая ошибка: {e}")
            return {
                "success": False,
                "message": "Произошла ошибка при тестировании соединения.",
                "details": str(e)
            }

    def get_dns_status(self, manual_ip=None):
        ip, err = self.connect_tv(manual_ip)
        if not ip:
            return {"success": False, "message": err}
        dns = tv_manager.action_get_dns(ip)
        return {"success": True, "ip": ip, **dns}

    def set_dns(self, enable=True, manual_ip=None):
        ip, err = self.connect_tv(manual_ip)
        if not ip:
            return {"success": False, "message": err}
        res = tv_manager.action_set_dns(ip, enable)
        dns = tv_manager.action_get_dns(ip)
        return {
            "success": True,
            "enabled": dns["enabled"],
            "message": "AdGuard Private DNS активирован! Реклама блокируется системно." if dns["enabled"] else "Private DNS отключен. Восстановлен стандартный DNS."
        }

    def set_dock_config(self, dock_apps=None, columns=6, manual_ip=None):
        ip, err = self.connect_tv(manual_ip)
        if not ip:
            return {"success": False, "message": err}
        tv_manager.action_set_dock(ip, dock_apps, int(columns))
        return {"success": True, "message": "Конфигурация дока успешно обновлена на телевизоре!"}

    def switch_launcher(self, launcher_name="cleanyourtv", manual_ip=None):
        ip, err = self.connect_tv(manual_ip)
        if not ip:
            return {"success": False, "message": err}
        tv_manager.action_switch_launcher(ip, launcher_name)
        return {"success": True, "message": f"Домашний экран переключен на {launcher_name.upper()}!"}

    def get_available_apps(self):
        apps_dir = tv_manager.APPS_DIR
        apps_list = []
        if os.path.exists(apps_dir):
            for f in sorted(os.listdir(apps_dir)):
                if f.lower().endswith(".apk"):
                    fp = os.path.join(apps_dir, f)
                    size_mb = round(os.path.getsize(fp) / (1024 * 1024), 1)
                    apps_list.append({"filename": f, "size_mb": size_mb})
        return apps_list

    def run_action(self, action, manual_ip=None, apps_list=None, tv_type="yaos", launcher_choice="cleanyourtv", *args, **kwargs):
        ip, err = self.connect_tv(manual_ip)
        if not ip:
            return {"success": False, "message": f"Нет связи с телевизором по ADB ({err})"}

        try:
            if action == "install":
                installed = tv_manager.action_install_apps(ip, apps_list or "top6")
                return {"success": True, "message": f"Подгрузка приложений завершена! Успешно: {installed} шт."}

            elif action == "light_debloat":
                tv_manager.action_light_debloat(ip, tv_type)
                desc = "Яндекс ТВ" if tv_type == "yaos" else "Android TV / Google TV"
                return {"success": True, "message": f"Легкая очистка рекламы и фоновых служб ({desc}) выполнена успешно!"}

            elif action == "full_debloat":
                tv_manager.action_full_debloat(ip, tv_type, launcher_choice)
                desc = "Яндекс ТВ" if tv_type == "yaos" else "Android TV / Google TV"
                return {"success": True, "message": f"Полный деблоат ({desc}) выполнен! Домашний экран переведен на {launcher_choice.upper()}."}

            elif action == "restore":
                tv_manager.action_restore(ip, tv_type)
                desc = "Яндекс ТВ" if tv_type == "yaos" else "Google TV / Android TV"
                return {"success": True, "message": f"Все заводские службы ({desc}) успешно восстановлены!"}

            elif action == "set_dns":
                enable = kwargs.get("enable", True)
                tv_manager.action_set_dns(ip, enable)
                return {"success": True, "message": "Настройки DNS успешно обновлены!"}

            elif action == "switch_launcher":
                tv_manager.action_switch_launcher(ip, launcher_choice)
                return {"success": True, "message": f"Лаунчер успешно переключен на {launcher_choice}!"}

            return {"success": False, "message": f"Неизвестное действие: {action}"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка выполнения действия: {e}"}

    def install_selected_apps(self, apps_list, manual_ip=None):
        return self.run_action("install", manual_ip=manual_ip, apps_list=apps_list)

    def browse_file(self):
        if not self._window:
            return ""
        try:
            result = self._window.create_file_dialog(webview.OPEN_DIALOG, file_types=('Android Package (*.apk)', 'All Files (*.*)'))
            if result and len(result) > 0:
                return result[0]
        except Exception as e:
            self._log_js(f"Диалог выбора файла: {e}")
        return ""

    def install_custom_apk(self, filepath, manual_ip=None):
        if not filepath or not os.path.exists(filepath):
            return {"success": False, "message": f"Файл не найден: {filepath}"}
        
        ip, err = self.connect_tv(manual_ip)
        if not ip:
            return {"success": False, "message": f"Нет связи с телевизором по ADB ({err})"}

        self._log_js(f"Загрузка и установка {os.path.basename(filepath)}...")
        try:
            res = subprocess.run([tv_manager.ADB, "-s", f"{ip}:5555", "install", "-r", filepath], capture_output=True, text=True, timeout=120)
            if "Success" in res.stdout or "Success" in res.stderr:
                return {"success": True, "message": f"Приложение {os.path.basename(filepath)} успешно установлено на телевизор!"}
            else:
                return {"success": False, "message": f"Ошибка установки: {res.stdout.strip()} {res.stderr.strip()}"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка при установке: {e}"}

def main():
    api = SmartTV_API()
    url = HTML_FILE if os.path.exists(HTML_FILE) else os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_ui.html")
    
    window = webview.create_window(
        title="Smart TV Toolbox v2.0 — Панель управления",
        url=url,
        js_api=api,
        width=1040,
        height=880,
        min_size=(860, 700),
        background_color="#0f172a"
    )
    api.set_window(window)
    webview.start(gui="edgechromium")

if __name__ == '__main__':
    main()
