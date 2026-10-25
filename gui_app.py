# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import os
import sys
import socket
import time

# Directory resolution (support both script and PyInstaller exe mode)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADB = os.path.join(BASE_DIR, "platform-tools", "adb.exe")
APPS_DIR = os.path.join(BASE_DIR, "apps")

class SmartTVApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart TV Toolbox — Панель управления")
        self.geometry("860x720")
        self.minsize(780, 620)
        
        # Color theme: Modern Dark
        self.c_bg = "#0f172a"
        self.c_card = "#1e293b"
        self.c_border = "#334155"
        self.c_accent = "#38bdf8"
        self.c_text = "#f8fafc"
        self.c_muted = "#94a3b8"
        self.c_success = "#22c55e"
        self.c_danger = "#ef4444"
        
        self.configure(bg=self.c_bg)
        self.current_ip = None
        
        self.build_ui()

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=self.c_bg, padx=20, pady=15)
        header.pack(fill="x")
        
        lbl_badge = tk.Label(header, text="SMART TV CONTROL PANEL", font=("Segoe UI", 8, "bold"),
                             fg=self.c_accent, bg="#1e293b", padx=10, pady=3)
        lbl_badge.pack(anchor="w")
        
        lbl_title = tk.Label(header, text="Управление и Оптимизация Smart TV", font=("Segoe UI", 18, "bold"),
                             fg="#ffffff", bg=self.c_bg)
        lbl_title.pack(anchor="w", pady=(6, 2))
        
        lbl_desc = tk.Label(header, text="Быстрая проверка соединения, установка приложений и деблоат в 1 клик",
                            font=("Segoe UI", 10), fg=self.c_muted, bg=self.c_bg)
        lbl_desc.pack(anchor="w")

        # Main Scrollable / Frame Container
        content = tk.Frame(self, bg=self.c_bg, padx=20)
        content.pack(fill="both", expand=True)

        # Card 1: Connection & Status
        card_conn = tk.LabelFrame(content, text=" 📡 ШАГ 1: Статус и Проверка Связи с ТВ ",
                                  font=("Segoe UI", 11, "bold"), fg=self.c_accent, bg=self.c_card,
                                  padx=15, pady=12, relief="groove", bd=1)
        card_conn.pack(fill="x", pady=(0, 12))

        f_ip = tk.Frame(card_conn, bg=self.c_card)
        f_ip.pack(fill="x", pady=(0, 8))
        
        tk.Label(f_ip, text="IP телевизора:", font=("Segoe UI", 10), fg=self.c_text, bg=self.c_card).pack(side="left")
        self.ent_ip = tk.Entry(f_ip, font=("Segoe UI", 10), width=18, bg="#090d16", fg="#ffffff", insertbackground="#fff", bd=1)
        self.ent_ip.pack(side="left", padx=10)
        self.ent_ip.insert(0, "Автопоиск")

        self.btn_test = tk.Button(f_ip, text="🔍 Проверить соединение", font=("Segoe UI", 10, "bold"),
                                  bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
                                  bd=0, padx=15, pady=5, cursor="hand2", command=self.on_test_connection)
        self.btn_test.pack(side="left", padx=5)

        self.lbl_status = tk.Label(card_conn, text="Статус: нажмите «Проверить соединение» для автопоиска ТВ в сети",
                                   font=("Segoe UI", 9), fg=self.c_muted, bg=self.c_card, anchor="w", justify="left")
        self.lbl_status.pack(fill="x")

        # Card 2: Quick Actions
        card_act = tk.LabelFrame(content, text=" ⚡ ШАГ 2: Быстрые Действия ",
                                 font=("Segoe UI", 11, "bold"), fg=self.c_accent, bg=self.c_card,
                                 padx=15, pady=12, relief="groove", bd=1)
        card_act.pack(fill="x", pady=(0, 12))

        btn_grid = tk.Frame(card_act, bg=self.c_card)
        btn_grid.pack(fill="x")

        # 4 Action buttons
        self.btn_install = self.create_action_btn(
            btn_grid, "📦 1. Установить приложения",
            "Happ, HDrezka TV 1.4.0, Zona, File Manager+, SmartTube",
            "#1e3a5f", "#38bdf8", lambda: self.run_bg_action("install")
        )
        self.btn_install.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        self.btn_light = self.create_action_btn(
            btn_grid, "⚡ 2. Очистить рекламу",
            "Отключить рекламу и трекеры. ЯНДЕКС ЛАУНЧЕР ОСТАЕТСЯ",
            "#1e3a5f", "#38bdf8", lambda: self.run_bg_action("light_debloat")
        )
        self.btn_light.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")

        self.btn_full = self.create_action_btn(
            btn_grid, "🚀 3. Полный деблоат + FLauncher",
            "Ставит приложения + чистый быстрый плиточный FLauncher",
            "#14532d", "#4ade80", lambda: self.run_bg_action("full_debloat")
        )
        self.btn_full.grid(row=1, column=0, padx=6, pady=6, sticky="nsew")

        self.btn_restore = self.create_action_btn(
            btn_grid, "🔄 4. Вернуть как было (Откат)",
            "Мгновенное восстановление заводских служб Яндекса",
            "#7f1d1d", "#f87171", lambda: self.run_bg_action("restore")
        )
        self.btn_restore.grid(row=1, column=1, padx=6, pady=6, sticky="nsew")

        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        # Card 3: Live Log Output
        card_log = tk.LabelFrame(content, text=" 📝 Лог выполнения операций ",
                                 font=("Segoe UI", 10, "bold"), fg=self.c_muted, bg=self.c_card,
                                 padx=10, pady=8, relief="groove", bd=1)
        card_log.pack(fill="both", expand=True, pady=(0, 10))

        self.txt_log = scrolledtext.ScrolledText(card_log, bg="#090d16", fg="#e2e8f0", insertbackground="#fff",
                                                 font=("Consolas", 9), bd=0, padx=8, pady=8)
        self.txt_log.pack(fill="both", expand=True)
        self.log("Приложение готово. Нажмите «Проверить соединение» для начала.")

    def create_action_btn(self, parent, title, desc, bg_color, fg_color, cmd):
        btn = tk.Button(parent, text=f"{title}\n{desc}", font=("Segoe UI", 9, "bold"),
                        bg=bg_color, fg=fg_color, activebackground=self.c_border, activeforeground="#ffffff",
                        bd=1, relief="solid", padx=12, pady=10, cursor="hand2", justify="left",
                        wraplength=340, command=cmd)
        return btn

    def log(self, text):
        self.txt_log.insert(tk.END, f"{text}\n")
        self.txt_log.see(tk.END)

    def set_busy(self, is_busy, msg=""):
        state = tk.DISABLED if is_busy else tk.NORMAL
        self.btn_test.config(state=state)
        self.btn_install.config(state=state)
        self.btn_light.config(state=state)
        self.btn_full.config(state=state)
        self.btn_restore.config(state=state)
        if msg:
            self.lbl_status.config(text=msg)

    def on_test_connection(self):
        def worker():
            self.set_busy(True, "⏳ Поиск телевизора в сети и проверка ADB...")
            self.log("\n[>] Запуск проверки соединения...")
            
            ip = self.ent_ip.get().strip()
            if ip.lower() in ["автопоиск", "auto", ""]:
                ip = None
            
            # Find TV
            found_ip = self.connect_tv(ip)
            if not found_ip:
                self.log("❌ Не удалось найти телевизор или порт 5555 закрыт.")
                self.lbl_status.config(text="❌ Ошибка: нет связи с ТВ. Убедитесь, что в Factory Menu включен ADB -> ON.", fg=self.c_danger)
                self.set_busy(False)
                return

            self.current_ip = found_ip
            self.ent_ip.delete(0, tk.END)
            self.ent_ip.insert(0, found_ip)

            # Query props
            model = self.adb_shell("getprop ro.product.model")
            brand = self.adb_shell("getprop ro.product.brand")
            android_v = self.adb_shell("getprop ro.build.version.release")
            launcher = self.adb_shell("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME")
            cur_launcher = launcher.splitlines()[-1] if launcher else "Стандартный"

            self.log(f"✅ УСПЕХ! Подключено к {found_ip}:5555")
            self.log(f"   Модель: {brand} {model} | Android: {android_v} | Лаунчер: {cur_launcher}")
            
            status_text = f"✅ Телевизор на связи! ({brand} {model}, Android {android_v}) — Готов к операциям"
            self.lbl_status.config(text=status_text, fg=self.c_success)
            self.set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def run_bg_action(self, action_name):
        def worker():
            self.set_busy(True, f"⏳ Выполняется операция '{action_name}'...")
            ip = self.ent_ip.get().strip()
            if ip.lower() in ["автопоиск", "auto", ""]:
                ip = self.current_ip
            
            connected_ip = self.connect_tv(ip)
            if not connected_ip:
                self.log("❌ Ошибка: нет связи с телевизором по ADB!")
                self.lbl_status.config(text="❌ Ошибка: телевизор не отвечает.", fg=self.c_danger)
                self.set_busy(False)
                return

            if action_name == "install":
                self.log("\n[>] Установка пакета приложений (Happ, HDrezka, Zona, File Manager+, SmartTube)...")
                apks = ["hdrezka.apk", "zona.apk", "filemanager_plus.apk", "smarttube.apk", "Happ.apk"]
                for apk in apks:
                    p = os.path.join(APPS_DIR, apk)
                    if os.path.exists(p):
                        self.log(f" • Установка {apk}...")
                        res = subprocess.run([ADB, "-s", f"{connected_ip}:5555", "install", "-r", p], capture_output=True, text=True)
                        if "Success" in res.stdout or "Success" in res.stderr:
                            self.log(f"   ✓ {apk} успешно установлено!")
                        else:
                            self.log(f"   ! {apk}: {res.stdout.strip()}")
                self.lbl_status.config(text="✅ Все приложения успешно установлены на ТВ!", fg=self.c_success)

            elif action_name == "light_debloat":
                self.log("\n[>] Легкая очистка рекламы (Яндекс лаунчер и Алиса сохраняются)...")
                pkgs = [
                    "com.yandex.android.advid",
                    "com.yandex.tv.bugreportsender",
                    "com.yandex.launcher.updaterapp",
                    "com.yandex.tv.daydream",
                    "com.yandex.browser.tv"
                ]
                for pkg in pkgs:
                    self.adb_shell(f"pm uninstall --user 0 {pkg}")
                    self.adb_shell(f"am force-stop {pkg}")
                    self.log(f" • Отключено: {pkg}")
                self.log("✅ Реклама и трекеры отключены!")
                self.lbl_status.config(text="✅ Легкая очистка выполнена! Реклама удалена.", fg=self.c_success)

            elif action_name == "full_debloat":
                self.log("\n[>] Полный деблоат и переключение на чистый FLauncher...")
                fl_apk = os.path.join(APPS_DIR, "flauncher.apk")
                if os.path.exists(fl_apk):
                    self.log(" • Проверка/установка FLauncher...")
                    subprocess.run([ADB, "-s", f"{connected_ip}:5555", "install", "-r", fl_apk], capture_output=True)
                
                self.log(" • Назначение FLauncher домашним экраном...")
                self.adb_shell("cmd package set-home-activity me.efesser.flauncher/.MainActivity")

                pkgs = [
                    "com.yandex.tv.alice", "com.yandex.tv.home", "com.yandex.tv.music",
                    "com.yandex.browser.tv", "com.yandex.tv.live", "com.yandex.tv.input.efir",
                    "com.yandex.tv.daydream", "com.yandex.tv.bugreportsender",
                    "com.yandex.android.advid", "com.yandex.tv.ytplayer",
                    "com.yandex.tv.webplayer", "com.yandex.tv.videoplayer",
                    "com.yandex.launcher.updaterapp"
                ]
                for pkg in pkgs:
                    self.adb_shell(f"pm uninstall --user 0 {pkg}")
                    self.adb_shell(f"am force-stop {pkg}")
                    self.log(f" • Отключено: {pkg}")

                self.adb_shell("am start -a android.intent.action.MAIN -c android.intent.category.HOME")
                self.log("✅ Полный деблоат завершен! Домашний экран теперь FLauncher.")
                self.lbl_status.config(text="✅ Полная оптимизация завершена! Экран: FLauncher", fg=self.c_success)

            elif action_name == "restore":
                self.log("\n[>] Восстановление заводских сервисов Яндекс ТВ...")
                pkgs = [
                    "com.yandex.tv.alice", "com.yandex.tv.home", "com.yandex.tv.music",
                    "com.yandex.browser.tv", "com.yandex.tv.live", "com.yandex.tv.input.efir",
                    "com.yandex.tv.daydream", "com.yandex.tv.bugreportsender",
                    "com.yandex.android.advid", "com.yandex.tv.ytplayer",
                    "com.yandex.tv.webplayer", "com.yandex.tv.videoplayer",
                    "com.yandex.launcher.updaterapp"
                ]
                for pkg in pkgs:
                    self.adb_shell(f"cmd package install-existing {pkg}")
                    self.log(f" • Восстановлено: {pkg}")
                
                self.adb_shell("cmd package set-home-activity com.yandex.tv.home/.HomeActivity")
                self.adb_shell("am start -a android.intent.action.MAIN -c android.intent.category.HOME")
                self.log("✅ Все сервисы восстановлены! Телевизор вернулся в исходное состояние.")
                self.lbl_status.config(text="✅ Заводское состояние Яндекса успешно восстановлено!", fg=self.c_success)

            self.set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def connect_tv(self, manual_ip=None):
        if not os.path.exists(ADB):
            self.log(f"❌ Файл adb.exe не найден по пути: {ADB}")
            return None

        ip = manual_ip
        if not ip:
            # 1. mDNS discovery
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
            # 2. ARP port scan
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
            return ip
        return None

    def adb_shell(self, cmd):
        ip = self.current_ip
        if not ip:
            return ""
        res = subprocess.run([ADB, "-s", f"{ip}:5555", "shell", cmd], capture_output=True, text=True)
        return res.stdout.strip()

if __name__ == "__main__":
    app = SmartTVApp()
    app.mainloop()
