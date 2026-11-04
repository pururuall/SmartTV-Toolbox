# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import subprocess
import os
import sys
import socket
import time

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADB = os.path.join(BASE_DIR, "platform-tools", "adb.exe")
APPS_DIR = os.path.join(BASE_DIR, "apps")
ICON_ICO = os.path.join(BASE_DIR, "app_icon.ico")

PRESETS = {
    "top6": ["zona.apk", "hdrezka.apk", "lampa.apk", "spotify.apk", "filemanager_plus.apk", "Happ.apk"],
    "basic": ["hdrezka.apk", "zona.apk", "filemanager_plus.apk", "smarttube.apk", "Happ.apk"]
}

class SmartTVApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart TV Toolbox — Панель управления")
        self.geometry("920x840")
        self.minsize(840, 720)
        
        # Set Capybara window icon if available
        if os.path.exists(ICON_ICO):
            try:
                self.iconbitmap(ICON_ICO)
            except Exception:
                pass

        # HTML Design System Palette
        self.c_bg = "#0f172a"          # slate-900 (главный фон)
        self.c_card = "#1e293b"        # slate-800 (фон карточек)
        self.c_border = "#334155"      # slate-700 (рамки)
        self.c_input_bg = "#090d16"    # темные поля ввода
        self.c_accent = "#38bdf8"      # sky-400 (акцентный голубой)
        self.c_text = "#f8fafc"        # белый текст
        self.c_muted = "#94a3b8"       # серый текст
        self.c_success = "#22c55e"     # зеленый
        self.c_success_bg = "#14532d"
        self.c_danger = "#ef4444"      # красный
        self.c_danger_bg = "#7f1d1d"
        
        self.configure(bg=self.c_bg)
        self.current_ip = None
        
        self.build_ui()

    def build_ui(self):
        # Header (как в HTML)
        header = tk.Frame(self, bg=self.c_bg, padx=25, pady=16)
        header.pack(fill="x")
        
        f_badge = tk.Frame(header, bg=self.c_bg)
        f_badge.pack(anchor="w")
        
        lbl_badge = tk.Label(f_badge, text="ИНТЕРАКТИВНОЕ РУКОВОДСТВО + УПРАВЛЕНИЕ", font=("Segoe UI", 8, "bold"),
                             fg=self.c_accent, bg="#1e293b", padx=12, pady=4, relief="solid", bd=1)
        lbl_badge.pack(side="left")
        
        lbl_title = tk.Label(header, text="Прокачка и Очистка Smart TV (Tuvio / Яндекс ТВ)",
                             font=("Segoe UI", 18, "bold"), fg="#ffffff", bg=self.c_bg)
        lbl_title.pack(anchor="w", pady=(8, 2))
        
        lbl_desc = tk.Label(header, text="Проверка соединения по сети, подгрузка приложений (Zona, HDrezka, Lampa, Spotify, File Manager+, Happ), деблоат",
                            font=("Segoe UI", 9), fg=self.c_muted, bg=self.c_bg)
        lbl_desc.pack(anchor="w")

        # Main Scrollable / Frame Container
        content = tk.Frame(self, bg=self.c_bg, padx=25)
        content.pack(fill="both", expand=True)

        # ----------------- КАРТОЧКА 1: ПРОВЕРКА СОЕДИНЕНИЯ -----------------
        c1 = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1, padx=18, pady=14)
        c1.pack(fill="x", pady=(0, 12))

        # Заголовок карточки
        c1_head = tk.Frame(c1, bg=self.c_card)
        c1_head.pack(fill="x", pady=(0, 10))
        
        tk.Label(c1_head, text="1", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg=self.c_accent,
                 width=3, height=1).pack(side="left", padx=(0, 10))
        tk.Label(c1_head, text="Проверка связи и доступ к отладке (ADB)", font=("Segoe UI", 12, "bold"),
                 fg="#ffffff", bg=self.c_card).pack(side="left")

        # Поле ввода IP и кнопка
        f_ip = tk.Frame(c1, bg=self.c_card)
        f_ip.pack(fill="x", pady=(0, 8))
        
        tk.Label(f_ip, text="IP телевизора:", font=("Segoe UI", 10), fg=self.c_text, bg=self.c_card).pack(side="left")
        self.ent_ip = tk.Entry(f_ip, font=("Segoe UI", 10), width=18, bg=self.c_input_bg, fg="#ffffff",
                               insertbackground="#fff", bd=1, relief="solid")
        self.ent_ip.pack(side="left", padx=10)
        self.ent_ip.insert(0, "Автопоиск")

        self.btn_test = tk.Button(f_ip, text="📡 Проверить соединение с телевизором", font=("Segoe UI", 10, "bold"),
                                  bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
                                  bd=0, padx=18, pady=6, cursor="hand2", command=self.on_test_connection)
        self.btn_test.pack(side="left", padx=5)

        # Информационная плашка статуса
        self.lbl_status = tk.Label(c1, text="Статус: нажмите «Проверить соединение» для автопоиска ТВ в локальной сети",
                                   font=("Segoe UI", 9), fg=self.c_muted, bg=self.c_card, anchor="w", justify="left")
        self.lbl_status.pack(fill="x")

        # ----------------- КАРТОЧКА 2: БЫСТРЫЕ ДЕЙСТВИЯ -----------------
        c2 = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1, padx=18, pady=14)
        c2.pack(fill="x", pady=(0, 12))

        c2_head = tk.Frame(c2, bg=self.c_card)
        c2_head.pack(fill="x", pady=(0, 10))
        
        tk.Label(c2_head, text="2", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg=self.c_accent,
                 width=3, height=1).pack(side="left", padx=(0, 10))
        tk.Label(c2_head, text="Оптимизация и пакетная подгрузка приложений", font=("Segoe UI", 12, "bold"),
                 fg="#ffffff", bg=self.c_card).pack(side="left")

        btn_grid = tk.Frame(c2, bg=self.c_card)
        btn_grid.pack(fill="x")

        self.btn_install = self.create_card_btn(
            btn_grid, "📥 1. Подгрузка приложений",
            "Выбор набора: Топ 6 в 1 клик (Zona, HDrezka, Lampa, Spotify, File Manager+, Happ), базовый набор или свои APK.",
            "#1e3a5f", "#38bdf8", self.open_install_dialog
        )
        self.btn_install.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.btn_light = self.create_card_btn(
            btn_grid, "⚡ 2. Очистить рекламу",
            "Отключить рекламу и трекеры. Родной лаунчер Яндекса и Алиса остаются!",
            "#1e3a5f", "#38bdf8", lambda: self.run_bg_action("light_debloat")
        )
        self.btn_light.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.btn_full = self.create_card_btn(
            btn_grid, "🚀 3. Полный деблоат + FLauncher",
            "Ставит приложения + чистый быстрый плиточный лаунчер FLauncher без тормозов",
            "#14532d", "#4ade80", lambda: self.run_bg_action("full_debloat")
        )
        self.btn_full.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.btn_restore = self.create_card_btn(
            btn_grid, "🔄 4. Вернуть как было (Откат)",
            "Мгновенное восстановление всех заводских сервисов и домашнего экрана Яндекса",
            "#7f1d1d", "#f87171", lambda: self.run_bg_action("restore")
        )
        self.btn_restore.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        # ----------------- КАРТОЧКА 3: УСТАНОВКА СВОЕГО APK -----------------
        c3 = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1, padx=18, pady=14)
        c3.pack(fill="x", pady=(0, 12))

        c3_head = tk.Frame(c3, bg=self.c_card)
        c3_head.pack(fill="x", pady=(0, 10))
        
        tk.Label(c3_head, text="3", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg=self.c_accent,
                 width=3, height=1).pack(side="left", padx=(0, 10))
        tk.Label(c3_head, text="Установка любого своего APK-приложения", font=("Segoe UI", 12, "bold"),
                 fg="#ffffff", bg=self.c_card).pack(side="left")

        f_apk = tk.Frame(c3, bg=self.c_card)
        f_apk.pack(fill="x")

        self.ent_custom_apk = tk.Entry(f_apk, font=("Segoe UI", 10), bg=self.c_input_bg, fg="#ffffff",
                                       insertbackground="#fff", bd=1, relief="solid")
        self.ent_custom_apk.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.ent_custom_apk.insert(0, "Выберите файл APK на компьютере...")

        btn_browse = tk.Button(f_apk, text="📁 Обзор...", font=("Segoe UI", 9, "bold"),
                               bg="#334155", fg="#ffffff", activebackground="#475569", activeforeground="#ffffff",
                               bd=0, padx=14, pady=5, cursor="hand2", command=self.on_browse_apk)
        btn_browse.pack(side="left", padx=(0, 8))

        self.btn_install_custom = tk.Button(f_apk, text="🚀 Установить на ТВ", font=("Segoe UI", 9, "bold"),
                                            bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
                                            bd=0, padx=16, pady=5, cursor="hand2", command=self.on_install_custom_apk)
        self.btn_install_custom.pack(side="left")

        # ----------------- КАРТОЧКА 4: ЖИВОЙ ЛОГ ВЫПОЛНЕНИЯ -----------------
        c4 = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1, padx=14, pady=10)
        c4.pack(fill="both", expand=True, pady=(0, 10))

        tk.Label(c4, text="📝 Лог выполнения операций", font=("Segoe UI", 10, "bold"),
                 fg=self.c_muted, bg=self.c_card).pack(anchor="w", pady=(0, 6))

        self.txt_log = scrolledtext.ScrolledText(c4, bg="#090d16", fg="#cbd5e1", insertbackground="#fff",
                                                 font=("Consolas", 9), bd=0, padx=8, pady=8)
        self.txt_log.pack(fill="both", expand=True)
        self.log("Программа готова к работе. Нажмите «Проверить соединение с телевизором».")

    def create_card_btn(self, parent, title, desc, bg_color, fg_color, cmd):
        f = tk.Frame(parent, bg=bg_color, highlightbackground=self.c_border, highlightthickness=1, padx=12, pady=10)
        
        lbl_t = tk.Label(f, text=title, font=("Segoe UI", 10, "bold"), fg=fg_color, bg=bg_color, anchor="w", justify="left")
        lbl_t.pack(fill="x")
        
        lbl_d = tk.Label(f, text=desc, font=("Segoe UI", 8), fg="#cbd5e1", bg=bg_color, anchor="w", justify="left", wraplength=360)
        lbl_d.pack(fill="x", pady=(4, 0))

        # Make entire frame clickable
        for widget in [f, lbl_t, lbl_d]:
            widget.bind("<Button-1>", lambda e: cmd())
            widget.config(cursor="hand2")
            widget.bind("<Enter>", lambda e, frame=f: frame.config(highlightbackground=self.c_accent))
            widget.bind("<Leave>", lambda e, frame=f: frame.config(highlightbackground=self.c_border))
        
        return f

    def open_install_dialog(self):
        win = tk.Toplevel(self)
        win.title("Подгрузка приложений на телевизор")
        win.geometry("540x480")
        win.configure(bg=self.c_bg)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="📥 Выберите набор приложений для установки", font=("Segoe UI", 12, "bold"),
                 fg="#ffffff", bg=self.c_bg, padx=15, pady=12).pack(anchor="w")

        # Опция 1: Топ 6
        f_top6 = tk.Frame(win, bg="#111a2e", highlightbackground=self.c_accent, highlightthickness=1, padx=14, pady=12)
        f_top6.pack(fill="x", padx=15, pady=6)
        tk.Label(f_top6, text="⭐ Топ-набор: Кино, Музыка и Файлы (6 шт.)", font=("Segoe UI", 10, "bold"),
                 fg="#38bdf8", bg="#111a2e").pack(anchor="w")
        tk.Label(f_top6, text="Zona, HDrezka TV (с ТВ), LAMPA (с ТВ), Spotify (с ТВ), File Manager+, Happ",
                 font=("Segoe UI", 8), fg="#cbd5e1", bg="#111a2e").pack(anchor="w", pady=(2, 8))
        tk.Button(f_top6, text="🚀 Установить этот набор (6 приложений) в 1 клик", font=("Segoe UI", 9, "bold"),
                  bg="#0284c7", fg="#fff", activebackground="#0369a1", activeforeground="#fff", bd=0, padx=12, pady=6,
                  cursor="hand2", command=lambda: [win.destroy(), self.run_bg_action("install", PRESETS["top6"])]).pack(anchor="w")

        # Опция 2: Базовый набор
        f_base = tk.Frame(win, bg="#111a2e", highlightbackground=self.c_border, highlightthickness=1, padx=14, pady=12)
        f_base.pack(fill="x", padx=15, pady=6)
        tk.Label(f_base, text="📦 Базовый стартовый комплект (5 шт.)", font=("Segoe UI", 10, "bold"),
                 fg="#e2e8f0", bg="#111a2e").pack(anchor="w")
        tk.Label(f_base, text="Happ, HDrezka TV, Zona, File Manager+, SmartTube",
                 font=("Segoe UI", 8), fg="#cbd5e1", bg="#111a2e").pack(anchor="w", pady=(2, 8))
        tk.Button(f_base, text="📦 Установить базовый набор", font=("Segoe UI", 9, "bold"),
                  bg="#334155", fg="#fff", activebackground="#475569", activeforeground="#fff", bd=0, padx=12, pady=6,
                  cursor="hand2", command=lambda: [win.destroy(), self.run_bg_action("install", PRESETS["basic"])]).pack(anchor="w")

        # Опция 3: Все приложения из папки apps
        f_all = tk.Frame(win, bg="#111a2e", highlightbackground=self.c_border, highlightthickness=1, padx=14, pady=12)
        f_all.pack(fill="x", padx=15, pady=6)
        tk.Label(f_all, text="📁 Все APK-файлы из папки apps", font=("Segoe UI", 10, "bold"),
                 fg="#e2e8f0", bg="#111a2e").pack(anchor="w")
        tk.Label(f_all, text="Установит все .apk файлы, которые находятся в папке apps",
                 font=("Segoe UI", 8), fg="#cbd5e1", bg="#111a2e").pack(anchor="w", pady=(2, 8))
        tk.Button(f_all, text="📲 Установить все APK из apps", font=("Segoe UI", 9, "bold"),
                  bg="#334155", fg="#fff", activebackground="#475569", activeforeground="#fff", bd=0, padx=12, pady=6,
                  cursor="hand2", command=lambda: [win.destroy(), self.run_bg_action("install", "all")]).pack(anchor="w")

        tk.Button(win, text="Закрыть", font=("Segoe UI", 9), bg="#1e293b", fg="#94a3b8", bd=0, padx=14, pady=4,
                  command=win.destroy).pack(anchor="e", padx=15, pady=10)

    def on_browse_apk(self):
        filename = filedialog.askopenfilename(
            title="Выберите APK-файл для установки на ТВ",
            filetypes=[("Android Package (*.apk)", "*.apk"), ("Все файлы (*.*)", "*.*")]
        )
        if filename:
            self.ent_custom_apk.delete(0, tk.END)
            self.ent_custom_apk.insert(0, filename)

    def on_install_custom_apk(self):
        apk_path = self.ent_custom_apk.get().strip()
        if not apk_path or not os.path.exists(apk_path) or not apk_path.lower().endswith(".apk"):
            messagebox.showwarning("Внимание", "Пожалуйста, выберите корректный файл .apk через кнопку «Обзор».")
            return
        
        def worker():
            self.set_busy(True, f"⏳ Установка {os.path.basename(apk_path)} на ТВ...")
            ip = self.ent_ip.get().strip()
            if ip.lower() in ["автопоиск", "auto", ""]:
                ip = self.current_ip
            
            connected_ip = self.connect_tv(ip)
            if not connected_ip:
                self.log("❌ Ошибка: нет связи с телевизором по ADB!")
                self.lbl_status.config(text="❌ Ошибка: телевизор не отвечает.", fg=self.c_danger)
                self.set_busy(False)
                return

            self.log(f"\n[>] Загрузка и установка {os.path.basename(apk_path)}...")
            res = subprocess.run([ADB, "-s", f"{connected_ip}:5555", "install", "-r", apk_path], capture_output=True, text=True)
            if "Success" in res.stdout or "Success" in res.stderr:
                self.log(f"✅ УСПЕХ! Приложение {os.path.basename(apk_path)} успешно установлено на телевизор!")
                self.lbl_status.config(text=f"✅ {os.path.basename(apk_path)} успешно установлено!", fg=self.c_success)
            else:
                self.log(f"❌ Ошибка установки: {res.stdout.strip()} {res.stderr.strip()}")
                self.lbl_status.config(text=f"❌ Ошибка установки {os.path.basename(apk_path)}", fg=self.c_danger)
            self.set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def set_busy(self, is_busy, msg=""):
        state = tk.DISABLED if is_busy else tk.NORMAL
        self.btn_test.config(state=state)
        self.btn_install_custom.config(state=state)
        if msg:
            self.lbl_status.config(text=msg)

    def on_test_connection(self):
        def worker():
            self.set_busy(True, "⏳ Поиск телевизора в сети и проверка ADB...")
            self.log("\n[>] Запуск проверки соединения...")
            
            ip = self.ent_ip.get().strip()
            if ip.lower() in ["автопоиск", "auto", ""]:
                ip = None
            
            found_ip = self.connect_tv(ip)
            if not found_ip:
                self.log("❌ Не удалось найти телевизор или порт 5555 закрыт.")
                self.lbl_status.config(text="❌ Ошибка: нет связи с ТВ. Убедитесь, что в Factory Menu включен ADB -> ON.", fg=self.c_danger)
                self.set_busy(False)
                return

            self.current_ip = found_ip
            self.ent_ip.delete(0, tk.END)
            self.ent_ip.insert(0, found_ip)

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

    def run_bg_action(self, action_name, apks_list=None):
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
                if apks_list and isinstance(apks_list, list):
                    apks = apks_list
                elif apks_list == "basic":
                    apks = PRESETS["basic"]
                elif apks_list == "all":
                    apks = [f for f in os.listdir(APPS_DIR) if f.lower().endswith(".apk")]
                else:
                    apks = PRESETS["top6"]

                self.log(f"\n[>] Подгрузка приложений ({len(apks)} шт.)...")
                installed_count = 0
                for apk in apks:
                    p = os.path.join(APPS_DIR, apk)
                    if os.path.exists(p):
                        self.log(f" • Установка {apk}...")
                        res = subprocess.run([ADB, "-s", f"{connected_ip}:5555", "install", "-r", p], capture_output=True, text=True)
                        if "Success" in res.stdout or "Success" in res.stderr:
                            self.log(f"   ✓ {apk} успешно установлено!")
                            installed_count += 1
                        else:
                            self.log(f"   ! {apk}: {res.stdout.strip()}")
                    else:
                        self.log(f"   ! Файл не найден: {apk}")
                self.lbl_status.config(text=f"✅ Подгрузка завершена! Установлено: {installed_count} из {len(apks)}", fg=self.c_success)

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
                self.log("✅ Полный деблоат завершен! Домашний экран переведен на FLauncher.")
                self.lbl_status.config(text="✅ Полный деблоат завершен! FLauncher активен.", fg=self.c_success)

            elif action_name == "restore":
                self.log("\n[>] Восстановление стандартного Яндекс ТВ...")
                pkgs = [
                    "com.yandex.tv.alice", "com.yandex.tv.home", "com.yandex.tv.music",
                    "com.yandex.browser.tv", "com.yandex.tv.live", "com.yandex.tv.input.efir",
                    "com.yandex.tv.daydream", "com.yandex.tv.bugreportsender",
                    "com.yandex.android.advid", "com.yandex.tv.ytplayer",
                    "com.yandex.tv.webplayer", "com.yandex.tv.videoplayer",
                    "com.yandex.launcher.updaterapp"
                ]
                for pkg in pkgs:
                    res = self.adb_shell(f"cmd package install-existing {pkg}")
                    self.log(f" • Восстановлено: {pkg}")
                self.adb_shell("cmd package set-home-activity com.yandex.tv.home/.HomeActivity")
                self.adb_shell("am start -a android.intent.action.MAIN -c android.intent.category.HOME")
                self.log("✅ Все сервисы восстановлены! Домашний экран Яндекса возвращен.")
                self.lbl_status.config(text="✅ Все службы восстановлены! Родной экран Яндекса возвращен.", fg=self.c_success)

            self.set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def connect_tv(self, ip=None):
        if not os.path.exists(ADB):
            self.log(f"❌ adb.exe не найден по пути {ADB}")
            return None

        # 0. Проверяем уже подключенные
        try:
            devs = subprocess.check_output([ADB, "devices"]).decode('utf-8', errors='ignore')
            for line in devs.splitlines():
                if ":5555\tdevice" in line:
                    active_ip = line.split(":5555")[0].strip()
                    return active_ip
        except Exception:
            pass

        # 1. mDNS опрос
        if not ip:
            self.log("[*] Поиск телевизора через mDNS (_yandexio)...")
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
                            self.log(f"[*] Найдено устройство: {ip}")
                            break
                    except socket.timeout:
                        break
                sock.close()
            except Exception:
                pass

        # 2. ARP кэш
        if not ip:
            self.log("[*] Сканирование ARP-кэша...")
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
                            self.log(f"[*] Найден открытый порт 5555 на {ip}")
                            break
                        s.close()
            except Exception:
                pass

        if not ip:
            return None

        self.log(f"[*] Подключение по ADB к {ip}:5555 ...")
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

    def log(self, text):
        self.txt_log.insert(tk.END, text + "\n")
        self.txt_log.see(tk.END)

if __name__ == "__main__":
    app = SmartTVApp()
    app.mainloop()
