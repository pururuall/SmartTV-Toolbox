# -*- coding: utf-8 -*-
import os
import sys
import shutil
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

def get_adb_path():
    candidates = []
    # 1. Bundled inside PyInstaller onefile
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        candidates.append(os.path.join(sys._MEIPASS, "platform-tools", "adb.exe"))
    # 2. In same folder as executable
    candidates.append(os.path.join(BASE_DIR, "platform-tools", "adb.exe"))
    # 3. In Desktop SmartTV_Toolbox
    candidates.append(os.path.join(os.path.expanduser('~/Desktop'), "SmartTV_Toolbox", "platform-tools", "adb.exe"))
    # 4. In current working directory
    candidates.append(os.path.join(os.getcwd(), "platform-tools", "adb.exe"))
    
    for c in candidates:
        if c and os.path.exists(c):
            return c
    
    sh = shutil.which("adb")
    if sh:
        return sh
    return None

def get_apps_dir():
    candidates = [
        os.path.join(BASE_DIR, "apps"),
        os.path.join(os.path.expanduser('~/Desktop'), "SmartTV_Toolbox", "apps"),
        os.path.join(os.getcwd(), "apps")
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return os.path.join(BASE_DIR, "apps")

class SmartTV_API:
    def __init__(self):
        self._window = None
        self.cached_ip = None

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
        adb = get_adb_path()
        if not adb:
            self._log_js("❌ Ошибка: adb.exe не найден!")
            return None, "Файл adb.exe не найден. Проверьте папку platform-tools."

        ip = manual_ip.strip() if manual_ip else self.cached_ip

        # 0. Проверяем, если устройство уже подключено в ADB
        try:
            devs = subprocess.check_output([adb, "devices"], timeout=3).decode('utf-8', errors='ignore')
            for line in devs.splitlines():
                if ":5555\tdevice" in line:
                    ip = line.split(":5555")[0].strip()
                    self._log_js(f"Устройство уже активно в ADB: {ip}")
                    self.cached_ip = ip
                    return ip, None
        except Exception:
            pass

        if not ip:
            # Быстрая проверка известных адресов в подсети
            for k_ip in ["192.168.3.54"]:
                try:
                    s = socket.socket()
                    s.settimeout(0.3)
                    if s.connect_ex((k_ip, 5555)) == 0:
                        ip = k_ip
                        s.close()
                        self._log_js(f"Телевизор обнаружен по адресу: {ip}")
                        break
                    s.close()
                except Exception:
                    pass

        if not ip:
            self._log_js("Поиск устройства в сети через mDNS...")
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
                            self._log_js(f"Найдено через mDNS: {ip}")
                            break
                    except socket.timeout:
                        break
                sock.close()
            except Exception as e:
                self._log_js(f"mDNS исключение: {e}")

        if not ip:
            self._log_js("Сканирование кэша ARP на порт 5555...")
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
                            self._log_js(f"Найден открытый порт 5555 на: {ip}")
                            break
                        s.close()
            except Exception as e:
                self._log_js(f"ARP исключение: {e}")

        if not ip:
            return None, "Телевизор не обнаружен автоматически. Введите его IP вручную."

        self._log_js(f"Подключение по ADB к {ip}:5555 ...")
        try:
            subprocess.run([adb, "connect", f"{ip}:5555"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            time.sleep(1)
            devs = subprocess.check_output([adb, "devices"], timeout=5).decode('utf-8', errors='ignore')
            if "device\n" in devs or "device\r" in devs or f"{ip}:5555\tdevice" in devs:
                self.cached_ip = ip
                return ip, None
            elif "unauthorized" in devs:
                return ip, "UNAUTHORIZED"
            else:
                return None, f"Порт 5555 закрыт или отклонил подключение (ADB devices: {devs.strip()})"
        except Exception as e:
            return None, f"Ошибка выполнения команды adb connect: {e}"

    def adb_shell(self, ip, cmd):
        adb = get_adb_path()
        if not adb:
            return ""
        try:
            res = subprocess.run([adb, "-s", f"{ip}:5555", "shell", cmd], capture_output=True, text=True, timeout=5)
            return res.stdout.strip()
        except Exception:
            return ""

    def test_connection(self, manual_ip=None):
        try:
            self._log_js("Запуск проверки соединения...")
            ip, err = self.connect_tv(manual_ip)
            
            if err == "UNAUTHORIZED":
                return {
                    "success": False,
                    "message": "Требуется подтверждение на экране ТВ!",
                    "details": "На экране телевизора появилось системное окно «Разрешить отладку». Поставьте галочку «Всегда разрешать с этого компьютера» и нажмите ОК пультом, затем нажмите кнопку проверки снова."
                }
            
            if not ip:
                return {
                    "success": False,
                    "message": "Не удалось подключиться к телевизору.",
                    "details": err or "Убедитесь, что ТВ включен, подключен к тому же Wi-Fi, и в Factory Menu включен пункт ADB -> ON."
                }

            model = self.adb_shell(ip, "getprop ro.product.model") or "Smart TV"
            brand = self.adb_shell(ip, "getprop ro.product.brand") or ""
            android_v = self.adb_shell(ip, "getprop ro.build.version.release") or "11"
            launcher = self.adb_shell(ip, "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME")
            cur_launcher = launcher.splitlines()[-1] if launcher else "Стандартный"
            
            self._log_js(f"Успех! Подключено: {brand} {model} (Android {android_v})")
            return {
                "success": True,
                "ip": ip,
                "brand": brand,
                "model": model,
                "android": android_v,
                "launcher": cur_launcher
            }
        except Exception as e:
            self._log_js(f"Критическая ошибка: {e}")
            return {
                "success": False,
                "message": "Произошла ошибка при тестировании соединения.",
                "details": str(e)
            }

    def run_action(self, action, manual_ip=None):
        adb = get_adb_path()
        apps_dir = get_apps_dir()
        
        ip, err = self.connect_tv(manual_ip)
        if not ip:
            return {"success": False, "message": f"Нет связи с телевизором по ADB ({err})"}

        try:
            if action == "install":
                self._log_js("Установка пакета приложений...")
                apks = ["hdrezka.apk", "zona.apk", "filemanager_plus.apk", "smarttube.apk", "Happ.apk"]
                installed_count = 0
                for apk in apks:
                    p = os.path.join(apps_dir, apk)
                    if os.path.exists(p):
                        self._log_js(f" • Установка {apk}...")
                        res = subprocess.run([adb, "-s", f"{ip}:5555", "install", "-r", p], capture_output=True, text=True, timeout=60)
                        if "Success" in res.stdout or "Success" in res.stderr:
                            self._log_js(f"   ✓ {apk} успешно установлено!")
                            installed_count += 1
                        else:
                            self._log_js(f"   ! {apk}: {res.stdout.strip()} {res.stderr.strip()}")
                    else:
                        self._log_js(f"   ! Файл не найден: {apk}")
                return {"success": True, "message": f"Установка завершена! Успешно обработано: {installed_count} приложений."}

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
                fl_apk = os.path.join(apps_dir, "flauncher.apk")
                if os.path.exists(fl_apk):
                    subprocess.run([adb, "-s", f"{ip}:5555", "install", "-r", fl_apk], capture_output=True, timeout=60)
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
        except Exception as e:
            return {"success": False, "message": f"Ошибка выполнения действия: {e}"}

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
        adb = get_adb_path()
        if not adb:
            return {"success": False, "message": "adb.exe не найден"}
            
        if not filepath or not os.path.exists(filepath):
            return {"success": False, "message": f"Файл не найден: {filepath}"}
        
        ip, err = self.connect_tv(manual_ip)
        if not ip:
            return {"success": False, "message": f"Нет связи с телевизором по ADB ({err})"}

        self._log_js(f"Загрузка и установка {os.path.basename(filepath)}...")
        try:
            res = subprocess.run([adb, "-s", f"{ip}:5555", "install", "-r", filepath], capture_output=True, text=True, timeout=120)
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
