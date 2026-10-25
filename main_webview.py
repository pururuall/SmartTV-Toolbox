# -*- coding: utf-8 -*-
import os
import sys
import webview
import subprocess
import time
import socket

# Path resolution for PyInstaller
if getattr(sys, 'frozen', False):
    MEIPASS_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    BASE_DIR = os.path.dirname(sys.executable)
    HTML_FILE = os.path.join(MEIPASS_DIR, "app_ui.html")
    if not os.path.exists(HTML_FILE):
        HTML_FILE = os.path.join(BASE_DIR, "app_ui.html")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    HTML_FILE = os.path.join(BASE_DIR, "app_ui.html")

ADB = os.path.join(BASE_DIR, "platform-tools", "adb.exe")
APPS_DIR = os.path.join(BASE_DIR, "apps")

class SmartTV_API:
    def __init__(self):
        self._window = None
        self.cached_ip = None

    def set_window(self, window):
        self._window = window

    def _log_js(self, msg):
        if self._window:
            safe = msg.replace('"', '\\"').replace('\n', '<br>')
            try:
                self._window.evaluate_js(f'addLog("{safe}")')
            except Exception:
                pass

    def connect_tv(self, manual_ip=None):
        if manual_ip:
            ip = manual_ip.strip()
        else:
            ip = self.cached_ip

        if not ip:
            # mDNS discovery
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
                sock.settimeout(1.5)
                sock.bind(('', 0))
                header = b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                q = b'\x09_yandexio\x04_tcp\x05local\x00\x00\x0c\x00\x01'
                sock.sendto(header + q, ('224.0.0.251', 5353))
                start = time.time()
                while time.time() - start < 2.0:
                    try:
                        buf, addr = sock.recvfrom(2048)
                        if b'yandex' in buf.lower():
                            ip = addr[0]
                            break
                    except socket.timeout:
                        break
                sock.close()
            except Exception:
                pass

        if not ip:
            # ARP cache
            try:
                arp_out = subprocess.check_output("arp -a", shell=True).decode('cp866', errors='ignore')
                for line in arp_out.splitlines():
                    p = line.strip().split()
                    if len(p) >= 2 and p[0].count('.') == 3 and not p[0].startswith('224.') and not p[0].startswith('239.'):
                        s = socket.socket()
                        s.settimeout(0.2)
                        if s.connect_ex((p[0], 5555)) == 0:
                            ip = p[0]
                            s.close()
                            break
                        s.close()
            except Exception:
                pass

        if not ip:
            return None

        subprocess.run([ADB, "connect", f"{ip}:5555"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        devs = subprocess.check_output([ADB, "devices"]).decode('utf-8', errors='ignore')
        if "device\n" in devs or "device\r" in devs or f"{ip}:5555\tdevice" in devs:
            self.cached_ip = ip
            return ip
        return None

    def adb_shell(self, ip, cmd):
        res = subprocess.run([ADB, "-s", f"{ip}:5555", "shell", cmd], capture_output=True, text=True)
        return res.stdout.strip()

    def test_connection(self, manual_ip=None):
        self._log_js("Подключение к ADB...")
        ip = self.connect_tv(manual_ip)
        if not ip:
            return {
                "success": False,
                "message": "Не удалось обнаружить телевизор или порт 5555 закрыт.",
                "details": "Убедитесь, что телевизор включен, подключен к тому же Wi-Fi, и в Factory Menu включен пункт ADB -> ON."
            }

        try:
            model = self.adb_shell(ip, "getprop ro.product.model")
            brand = self.adb_shell(ip, "getprop ro.product.brand")
            android_v = self.adb_shell(ip, "getprop ro.build.version.release")
            launcher = self.adb_shell(ip, "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME")
            cur_launcher = launcher.splitlines()[-1] if launcher else "Стандартный"
            return {
                "success": True,
                "ip": ip,
                "brand": brand,
                "model": model,
                "android": android_v,
                "launcher": cur_launcher
            }
        except Exception as e:
            return {"success": False, "message": f"Ошибка запроса параметров: {e}"}

    def run_action(self, action, manual_ip=None):
        ip = self.connect_tv(manual_ip)
        if not ip:
            return {"success": False, "message": "Нет связи с телевизором по ADB!"}

        if action == "install":
            self._log_js("Установка пакета приложений...")
            apks = ["hdrezka.apk", "zona.apk", "filemanager_plus.apk", "smarttube.apk", "Happ.apk"]
            for apk in apks:
                p = os.path.join(APPS_DIR, apk)
                if os.path.exists(p):
                    self._log_js(f" • Установка {apk}...")
                    res = subprocess.run([ADB, "-s", f"{ip}:5555", "install", "-r", p], capture_output=True, text=True)
                    if "Success" in res.stdout or "Success" in res.stderr:
                        self._log_js(f"   ✓ {apk} успешно установлено!")
                    else:
                        self._log_js(f"   ! {apk}: {res.stdout.strip()}")
            return {"success": True, "message": "Все приложения (Happ, HDrezka, Zona, File Manager+, SmartTube) успешно установлены!"}

        elif action == "light_debloat":
            self._log_js("Очистка рекламы (Яндекс остается)...")
            pkgs = [
                "com.yandex.android.advid", "com.yandex.tv.bugreportsender",
                "com.yandex.launcher.updaterapp", "com.yandex.tv.daydream", "com.yandex.browser.tv"
            ]
            for pkg in pkgs:
                self.adb_shell(ip, f"pm uninstall --user 0 {pkg}")
                self.adb_shell(ip, f"am force-stop {pkg}")
                self._log_js(f" • Отключено: {pkg}")
            return {"success": True, "message": "Реклама и трекеры отключены! Родной лаунчер Яндекса сохранен."}

        elif action == "full_debloat":
            self._log_js("Полный деблоат и переключение на FLauncher...")
            fl_apk = os.path.join(APPS_DIR, "flauncher.apk")
            if os.path.exists(fl_apk):
                subprocess.run([ADB, "-s", f"{ip}:5555", "install", "-r", fl_apk], capture_output=True)
            self.adb_shell(ip, "cmd package set-home-activity me.efesser.flauncher/.MainActivity")

            pkgs = [
                "com.yandex.tv.alice", "com.yandex.tv.home", "com.yandex.tv.music",
                "com.yandex.browser.tv", "com.yandex.tv.live", "com.yandex.tv.input.efir",
                "com.yandex.tv.daydream", "com.yandex.tv.bugreportsender",
                "com.yandex.android.advid", "com.yandex.tv.ytplayer",
                "com.yandex.tv.webplayer", "com.yandex.tv.videoplayer",
                "com.yandex.launcher.updaterapp"
            ]
            for pkg in pkgs:
                self.adb_shell(ip, f"pm uninstall --user 0 {pkg}")
                self.adb_shell(ip, f"am force-stop {pkg}")
                self._log_js(f" • Отключено: {pkg}")
            self.adb_shell(ip, "am start -a android.intent.action.MAIN -c android.intent.category.HOME")
            return {"success": True, "message": "Полный деблоат завершен! Домашний экран теперь FLauncher."}

        elif action == "restore":
            self._log_js("Восстановление всех заводских служб...")
            pkgs = [
                "com.yandex.tv.alice", "com.yandex.tv.home", "com.yandex.tv.music",
                "com.yandex.browser.tv", "com.yandex.tv.live", "com.yandex.tv.input.efir",
                "com.yandex.tv.daydream", "com.yandex.tv.bugreportsender",
                "com.yandex.android.advid", "com.yandex.tv.ytplayer",
                "com.yandex.tv.webplayer", "com.yandex.tv.videoplayer",
                "com.yandex.launcher.updaterapp"
            ]
            for pkg in pkgs:
                self.adb_shell(ip, f"cmd package install-existing {pkg}")
                self._log_js(f" • Восстановлено: {pkg}")
            self.adb_shell(ip, "cmd package set-home-activity com.yandex.tv.home/.HomeActivity")
            self.adb_shell(ip, "am start -a android.intent.action.MAIN -c android.intent.category.HOME")
            return {"success": True, "message": "Все заводские службы восстановлены!"}

        return {"success": False, "message": "Неизвестное действие"}

    def browse_file(self):
        if not self._window:
            return ""
        result = self._window.create_file_dialog(webview.OPEN_DIALOG, file_types=('Android Package (*.apk)', 'All Files (*.*)'))
        if result and len(result) > 0:
            return result[0]
        return ""

    def install_custom_apk(self, filepath, manual_ip=None):
        if not filepath or not os.path.exists(filepath):
            return {"success": False, "message": f"Файл не найден: {filepath}"}
        
        ip = self.connect_tv(manual_ip)
        if not ip:
            return {"success": False, "message": "Нет связи с телевизором по ADB!"}

        self._log_js(f"Загрузка и установка {os.path.basename(filepath)}...")
        res = subprocess.run([ADB, "-s", f"{ip}:5555", "install", "-r", filepath], capture_output=True, text=True)
        if "Success" in res.stdout or "Success" in res.stderr:
            return {"success": True, "message": f"Приложение {os.path.basename(filepath)} успешно установлено на телевизор!"}
        else:
            return {"success": False, "message": f"Ошибка установки: {res.stdout.strip()} {res.stderr.strip()}"}

def main():
    api = SmartTV_API()
    
    url = HTML_FILE if os.path.exists(HTML_FILE) else os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_ui.html")
    
    window = webview.create_window(
        title="Smart TV Toolbox — Панель управления",
        url=url,
        js_api=api,
        width=1020,
        height=860,
        min_size=(840, 680),
        background_color="#0f172a"
    )
    api.set_window(window)
    webview.start(gui="edgechromium")

if __name__ == '__main__':
    main()
