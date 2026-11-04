# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import subprocess
import os
import sys
import socket
import time

import tv_manager

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADB = tv_manager.ADB
APPS_DIR = tv_manager.APPS_DIR
ICON_ICO = os.path.join(BASE_DIR, "app_icon.ico")

PRESETS = tv_manager.PRESETS

class SmartTVApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart TV Toolbox v2.0 — Панель управления")
        self.geometry("960x860")
        self.minsize(860, 720)
        
        if os.path.exists(ICON_ICO):
            try:
                self.iconbitmap(ICON_ICO)
            except Exception:
                pass

        self.c_bg = "#0f172a"
        self.c_card = "#1e293b"
        self.c_border = "#334155"
        self.c_input_bg = "#090d16"
        self.c_accent = "#38bdf8"
        self.c_text = "#f8fafc"
        self.c_muted = "#94a3b8"
        self.c_success = "#22c55e"
        self.c_danger = "#ef4444"
        
        self.configure(bg=self.c_bg)
        self.current_ip = None
        self.current_platform = tk.StringVar(value="yaos")
        
        # Connect tv_manager logger to GUI
        tv_manager.set_logger(self.log)
        
        self.build_ui()

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=self.c_bg, padx=20, pady=12)
        header.pack(fill="x")
        
        f_badge = tk.Frame(header, bg=self.c_bg)
        f_badge.pack(anchor="w")
        
        lbl_badge = tk.Label(f_badge, text="SMART TV TOOLBOX v2.0 — MULTI-PLATFORM", font=("Segoe UI", 8, "bold"),
                             fg=self.c_accent, bg="#1e293b", padx=10, pady=3, relief="solid", bd=1)
        lbl_badge.pack(side="left")
        
        lbl_title = tk.Label(header, text="Универсальный центр оптимизации Smart TV",
                             font=("Segoe UI", 16, "bold"), fg="#ffffff", bg=self.c_bg)
        lbl_title.pack(anchor="w", pady=(6, 2))
        
        lbl_desc = tk.Label(header, text="Поддержка Яндекс ТВ (Tuvio), Android TV, Google TV (Xiaomi, TCL, Sony, Hisense). AdGuard DNS и CleanYourTV.",
                            font=("Segoe UI", 9), fg=self.c_muted, bg=self.c_bg)
        lbl_desc.pack(anchor="w")

        # Content
        content = tk.Frame(self, bg=self.c_bg, padx=20)
        content.pack(fill="both", expand=True)

        # ----------------- КАРТОЧКА 1: ВЫБОР ПЛАТФОРМЫ И СОЕДИНЕНИЕ -----------------
        c1 = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1, padx=16, pady=12)
        c1.pack(fill="x", pady=(0, 10))

        c1_head = tk.Frame(c1, bg=self.c_card)
        c1_head.pack(fill="x", pady=(0, 8))
        
        tk.Label(c1_head, text="1", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg=self.c_accent,
                 width=3, height=1).pack(side="left", padx=(0, 10))
        tk.Label(c1_head, text="Платформа и проверка соединения с ТВ", font=("Segoe UI", 11, "bold"),
                 fg="#ffffff", bg=self.c_card).pack(side="left")

        # Platform selector
        f_plat = tk.Frame(c1, bg=self.c_card)
        f_plat.pack(fill="x", pady=(0, 8))
        tk.Label(f_plat, text="Ваша система:", font=("Segoe UI", 9, "bold"), fg=self.c_text, bg=self.c_card).pack(side="left", padx=(0, 10))
        
        r1 = tk.Radiobutton(f_plat, text="Яндекс ТВ / YaOS (Tuvio, Hartens, DEXP)", variable=self.current_platform,
                            value="yaos", font=("Segoe UI", 9), bg=self.c_card, fg="#fff", selectcolor="#0f172a",
                            activebackground=self.c_card, activeforeground=self.c_accent)
        r1.pack(side="left", padx=(0, 15))
        
        r2 = tk.Radiobutton(f_plat, text="Android TV / Google TV (Xiaomi, TCL, Sony, Hisense)", variable=self.current_platform,
                            value="generic", font=("Segoe UI", 9), bg=self.c_card, fg="#fff", selectcolor="#0f172a",
                            activebackground=self.c_card, activeforeground=self.c_accent)
        r2.pack(side="left")

        # IP input and test button
        f_ip = tk.Frame(c1, bg=self.c_card)
        f_ip.pack(fill="x", pady=(0, 6))
        
        tk.Label(f_ip, text="IP телевизора:", font=("Segoe UI", 9), fg=self.c_text, bg=self.c_card).pack(side="left")
        self.ent_ip = tk.Entry(f_ip, font=("Segoe UI", 9), width=18, bg=self.c_input_bg, fg="#ffffff",
                               insertbackground="#fff", bd=1, relief="solid")
        self.ent_ip.pack(side="left", padx=8)
        self.ent_ip.insert(0, "Автопоиск")

        self.btn_test = tk.Button(f_ip, text="📡 Проверить соединение с ТВ", font=("Segoe UI", 9, "bold"),
                                  bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
                                  bd=0, padx=14, pady=5, cursor="hand2", command=self.on_test_connection)
        self.btn_test.pack(side="left", padx=4)

        self.lbl_status = tk.Label(c1, text="Статус: готов к подключению (Яндекс ТВ: Menu -> Влево -> Вверх -> Влево -> Вверх -> Назад | Android TV: Сборка 7 кликов -> Отладка)",
                                   font=("Segoe UI", 8), fg=self.c_muted, bg=self.c_card, anchor="w", justify="left")
        self.lbl_status.pack(fill="x")

        # ----------------- КАРТОЧКА 2: ДЕЙСТВИЯ ОПТИМИЗАЦИИ -----------------
        c2 = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1, padx=16, pady=12)
        c2.pack(fill="x", pady=(0, 10))

        c2_head = tk.Frame(c2, bg=self.c_card)
        c2_head.pack(fill="x", pady=(0, 8))
        
        tk.Label(c2_head, text="2", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg=self.c_accent,
                 width=3, height=1).pack(side="left", padx=(0, 10))
        tk.Label(c2_head, text="Оптимизация, деблоат и приложения", font=("Segoe UI", 11, "bold"),
                 fg="#ffffff", bg=self.c_card).pack(side="left")

        btn_grid = tk.Frame(c2, bg=self.c_card)
        btn_grid.pack(fill="x")

        self.btn_install = self.create_card_btn(
            btn_grid, "📥 1. Подгрузка приложений",
            "Установка Топ-6: Zona, HDrezka TV, Lampa, Spotify, Happ, File Manager+ в 1 клик",
            "#1e3a5f", "#38bdf8", self.open_install_dialog
        )
        self.btn_install.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")

        self.btn_light = self.create_card_btn(
            btn_grid, "⚡ 2. Очистить рекламу",
            "Заморозка рекламных служб и аналитики. Родной лаунчер сохранен!",
            "#1e3a5f", "#38bdf8", lambda: self.run_bg_action("light_debloat")
        )
        self.btn_light.grid(row=0, column=1, padx=4, pady=4, sticky="nsew")

        self.btn_full = self.create_card_btn(
            btn_grid, "🚀 3. Полный деблоат + CleanYourTV",
            "Ультралегкий лаунчер CleanYourTV (Apple TV Style) + заморозка тормозящей оболочки",
            "#14532d", "#4ade80", lambda: self.run_bg_action("full_debloat")
        )
        self.btn_full.grid(row=1, column=0, padx=4, pady=4, sticky="nsew")

        self.btn_restore = self.create_card_btn(
            btn_grid, "🔄 4. Заводской откат",
            "Разморозка всех служб и возврат стандартного лаунчера системы",
            "#7f1d1d", "#f87171", lambda: self.run_bg_action("restore")
        )
        self.btn_restore.grid(row=1, column=1, padx=4, pady=4, sticky="nsew")

        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        # ----------------- КАРТОЧКА 3: ИНСТРУМЕНТЫ 2.0 (DNS, ЛАУНЧЕР, APK) -----------------
        c3 = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1, padx=16, pady=10)
        c3.pack(fill="x", pady=(0, 10))

        c3_head = tk.Frame(c3, bg=self.c_card)
        c3_head.pack(fill="x", pady=(0, 6))
        
        tk.Label(c3_head, text="3", font=("Segoe UI", 10, "bold"), fg="#0f172a", bg=self.c_accent,
                 width=3, height=1).pack(side="left", padx=(0, 10))
        tk.Label(c3_head, text="Инструменты: AdGuard Private DNS, CleanYourTV и сторонний APK", font=("Segoe UI", 11, "bold"),
                 fg="#ffffff", bg=self.c_card).pack(side="left")

        # Row 1: DNS and Launcher tools
        f_tools = tk.Frame(c3, bg=self.c_card)
        f_tools.pack(fill="x", pady=(0, 6))

        tk.Button(f_tools, text="🛡️ Вкл AdGuard DNS", font=("Segoe UI", 8, "bold"), bg="#1e3a5f", fg="#38bdf8",
                  bd=0, padx=10, pady=4, cursor="hand2", command=lambda: self.run_bg_action("dns_on")).pack(side="left", padx=(0, 6))
        tk.Button(f_tools, text="⚪ Выкл DNS", font=("Segoe UI", 8), bg="#334155", fg="#cbd5e1",
                  bd=0, padx=10, pady=4, cursor="hand2", command=lambda: self.run_bg_action("dns_off")).pack(side="left", padx=(0, 12))
        tk.Button(f_tools, text="🍎 Активировать CleanYourTV", font=("Segoe UI", 8, "bold"), bg="#14532d", fg="#4ade80",
                  bd=0, padx=10, pady=4, cursor="hand2", command=lambda: self.run_bg_action("switch_cleanyourtv")).pack(side="left", padx=(0, 6))
        tk.Button(f_tools, text="💾 Обновить док (Топ-6)", font=("Segoe UI", 8), bg="#334155", fg="#cbd5e1",
                  bd=0, padx=10, pady=4, cursor="hand2", command=lambda: self.run_bg_action("set_dock")).pack(side="left")

        # Row 2: Custom APK
        f_apk = tk.Frame(c3, bg=self.c_card)
        f_apk.pack(fill="x")

        self.ent_custom_apk = tk.Entry(f_apk, font=("Segoe UI", 9), bg=self.c_input_bg, fg="#ffffff",
                                       insertbackground="#fff", bd=1, relief="solid")
        self.ent_custom_apk.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.ent_custom_apk.insert(0, "Выберите файл APK на компьютере...")

        btn_browse = tk.Button(f_apk, text="📁 Обзор...", font=("Segoe UI", 8, "bold"),
                               bg="#334155", fg="#ffffff", activebackground="#475569", activeforeground="#ffffff",
                               bd=0, padx=12, pady=4, cursor="hand2", command=self.on_browse_apk)
        btn_browse.pack(side="left", padx=(0, 6))

        self.btn_install_custom = tk.Button(f_apk, text="🚀 Установить APK", font=("Segoe UI", 8, "bold"),
                                            bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
                                            bd=0, padx=14, pady=4, cursor="hand2", command=self.on_install_custom_apk)
        self.btn_install_custom.pack(side="left")

        # ----------------- КАРТОЧКА 4: ЖИВОЙ ЛОГ ВЫПОЛНЕНИЯ -----------------
        c4 = tk.Frame(content, bg=self.c_card, highlightbackground=self.c_border, highlightthickness=1, padx=12, pady=8)
        c4.pack(fill="both", expand=True, pady=(0, 8))

        f_log_head = tk.Frame(c4, bg=self.c_card)
        f_log_head.pack(fill="x", pady=(0, 4))
        tk.Label(f_log_head, text="📝 Лог выполнения операций", font=("Segoe UI", 9, "bold"),
                 fg=self.c_muted, bg=self.c_card).pack(side="left")
        tk.Button(f_log_head, text="Очистить", font=("Segoe UI", 7), bg="#334155", fg="#cbd5e1",
                  bd=0, padx=8, pady=1, command=self.clear_log).pack(side="right")

        self.txt_log = scrolledtext.ScrolledText(c4, bg="#090d16", fg="#cbd5e1", insertbackground="#fff",
                                                 font=("Consolas", 8), bd=0, padx=6, pady=6)
        self.txt_log.pack(fill="both", expand=True)
        self.log("Smart TV Toolbox v2.0 готов к работе. Нажмите «Проверить соединение с ТВ».")

    def log(self, msg):
        try:
            self.txt_log.insert(tk.END, f"{msg}\n")
            self.txt_log.see(tk.END)
        except Exception:
            pass

    def clear_log(self):
        try:
            self.txt_log.delete('1.0', tk.END)
        except Exception:
            pass

    def create_card_btn(self, parent, title, desc, bg_color, fg_color, cmd):
        f = tk.Frame(parent, bg=bg_color, highlightbackground=self.c_border, highlightthickness=1, padx=10, pady=8)
        lbl_t = tk.Label(f, text=title, font=("Segoe UI", 9, "bold"), fg=fg_color, bg=bg_color, anchor="w", justify="left")
        lbl_t.pack(fill="x")
        lbl_d = tk.Label(f, text=desc, font=("Segoe UI", 8), fg="#cbd5e1", bg=bg_color, anchor="w", justify="left", wraplength=380)
        lbl_d.pack(fill="x", pady=(2, 0))

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

        f_top6 = tk.Frame(win, bg="#111a2e", highlightbackground=self.c_accent, highlightthickness=1, padx=14, pady=12)
        f_top6.pack(fill="x", padx=15, pady=6)
        tk.Label(f_top6, text="⭐ Топ-набор: Кино, Музыка и Файлы (6 шт.)", font=("Segoe UI", 10, "bold"),
                 fg="#38bdf8", bg="#111a2e").pack(anchor="w")
        tk.Label(f_top6, text="Zona, HDrezka TV, LAMPA, Spotify TV, Happ, File Manager+",
                 font=("Segoe UI", 8), fg="#cbd5e1", bg="#111a2e").pack(anchor="w", pady=(2, 8))
        tk.Button(f_top6, text="🚀 Установить Топ-6 в 1 клик", font=("Segoe UI", 9, "bold"),
                  bg="#0284c7", fg="#fff", activebackground="#0369a1", activeforeground="#fff", bd=0, padx=12, pady=6,
                  cursor="hand2", command=lambda: [win.destroy(), self.run_bg_action("install", PRESETS["top6"])]).pack(anchor="w")

        f_base = tk.Frame(win, bg="#111a2e", highlightbackground=self.c_border, highlightthickness=1, padx=14, pady=12)
        f_base.pack(fill="x", padx=15, pady=6)
        tk.Label(f_base, text="📦 Базовый комплект (5 шт.)", font=("Segoe UI", 10, "bold"),
                 fg="#e2e8f0", bg="#111a2e").pack(anchor="w")
        tk.Label(f_base, text="Happ, HDrezka TV, Zona, File Manager+, SmartTube",
                 font=("Segoe UI", 8), fg="#cbd5e1", bg="#111a2e").pack(anchor="w", pady=(2, 8))
        tk.Button(f_base, text="📦 Установить базовый набор", font=("Segoe UI", 9, "bold"),
                  bg="#334155", fg="#fff", activebackground="#475569", activeforeground="#fff", bd=0, padx=12, pady=6,
                  cursor="hand2", command=lambda: [win.destroy(), self.run_bg_action("install", PRESETS["basic"])]).pack(anchor="w")

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
            ip = self.get_target_ip()
            connected_ip = tv_manager.connect_adb(ip)
            if not connected_ip:
                self.log("❌ Ошибка: нет связи с телевизором по ADB!")
                self.lbl_status.config(text="❌ Ошибка: телевизор не отвечает.", fg=self.c_danger)
                self.set_busy(False)
                return

            self.log(f"\n[>] Загрузка и установка {os.path.basename(apk_path)}...")
            res = subprocess.run([ADB, "-s", f"{connected_ip}:5555", "install", "-r", apk_path], capture_output=True, text=True)
            if "Success" in res.stdout or "Success" in res.stderr:
                self.log(f"✅ УСПЕХ! Приложение {os.path.basename(apk_path)} установлено!")
                self.lbl_status.config(text=f"✅ {os.path.basename(apk_path)} установлено!", fg=self.c_success)
            else:
                self.log(f"❌ Ошибка установки: {res.stdout.strip()} {res.stderr.strip()}")
                self.lbl_status.config(text=f"❌ Ошибка установки {os.path.basename(apk_path)}", fg=self.c_danger)
            self.set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def get_target_ip(self):
        ip = self.ent_ip.get().strip()
        if ip.lower() in ["автопоиск", "auto", ""]:
            return self.current_ip
        return ip

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
            ip = self.get_target_ip()
            data = tv_manager.action_test_connection(ip)
            if not data:
                self.log("❌ Не удалось найти телевизор или порт 5555 закрыт.")
                self.lbl_status.config(text="❌ Ошибка: нет связи с ТВ. Включите отладку ADB.", fg=self.c_danger)
                self.set_busy(False)
                return

            self.current_ip = data.get("ip")
            self.ent_ip.delete(0, tk.END)
            self.ent_ip.insert(0, data.get("ip"))

            dns_msg = "AdGuard DNS: ВКЛ" if (data.get("dns_mode") == "hostname" and "adguard" in str(data.get("dns_specifier")).lower()) else "Стандартный DNS"
            self.log(f"✅ УСПЕХ! Подключено к {data.get('ip')}:5555 ({data.get('brand')} {data.get('model')}, Android {data.get('android')})")
            self.lbl_status.config(
                text=f"✅ НА СВЯЗИ: {data.get('brand')} {data.get('model')} (Android {data.get('android')}) | {dns_msg}",
                fg=self.c_success
            )
            self.set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def run_bg_action(self, action_name, param=None):
        def worker():
            self.set_busy(True, "⏳ Выполнение операции на телевизоре...")
            ip = self.get_target_ip()
            connected_ip = tv_manager.connect_adb(ip)
            if not connected_ip:
                self.log("❌ Ошибка: нет связи с телевизором по ADB!")
                self.lbl_status.config(text="❌ Ошибка: телевизор не отвечает.", fg=self.c_danger)
                self.set_busy(False)
                return

            self.current_ip = connected_ip
            tv_type = self.current_platform.get()

            if action_name == "install":
                tv_manager.action_install_apps(connected_ip, param or "top6")
                self.lbl_status.config(text="✅ Приложения успешно подгружены на ТВ!", fg=self.c_success)

            elif action_name == "light_debloat":
                tv_manager.action_light_debloat(connected_ip, tv_type)
                self.lbl_status.config(text="✅ Реклама и фоновая аналитика отключены!", fg=self.c_success)

            elif action_name == "full_debloat":
                tv_manager.action_full_debloat(connected_ip, tv_type, "cleanyourtv")
                self.lbl_status.config(text="✅ Полный деблоат завершен! CleanYourTV активен.", fg=self.c_success)

            elif action_name == "restore":
                tv_manager.action_restore(connected_ip, tv_type)
                self.lbl_status.config(text="✅ Все службы восстановлены в заводское состояние!", fg=self.c_success)

            elif action_name == "dns_on":
                tv_manager.action_set_dns(connected_ip, True)
                self.lbl_status.config(text="✅ AdGuard Private DNS включен!", fg=self.c_success)

            elif action_name == "dns_off":
                tv_manager.action_set_dns(connected_ip, False)
                self.lbl_status.config(text="⚪ Private DNS отключен.", fg=self.c_text)

            elif action_name == "switch_cleanyourtv":
                tv_manager.action_switch_launcher(connected_ip, "cleanyourtv")
                self.lbl_status.config(text="✅ CleanYourTV сделан основным лаунчером!", fg=self.c_success)

            elif action_name == "set_dock":
                tv_manager.action_set_dock(connected_ip)
                self.lbl_status.config(text="✅ Док CleanYourTV настроен!", fg=self.c_success)

            self.set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

def main():
    app = SmartTVApp()
    app.mainloop()

if __name__ == '__main__':
    main()
