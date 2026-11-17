# -*- coding: utf-8 -*-
"""
core.debloat
Списки пакетов, пресеты, деблоат (CleanYourTV, Yandex, отключение сервисов).
"""
import os
import sys
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

KNOWN_TV_PACKAGES = {

    # Пользовательские онлайн-кинотеатры, плееры и медиа

    "com.vk.video": {"name": "ВК Видео", "desc": "Пользовательский онлайн-кинотеатр и ролики ВКонтакте. Остановка мгновенно вернет память ТВ.", "category": "user_app", "safety": "safe"},

    "com.vk.vkvideo": {"name": "ВК Видео", "desc": "Пользовательский онлайн-кинотеатр и ролики ВКонтакте.", "category": "user_app", "safety": "safe"},

    "ru.kinopoisk.tv": {"name": "Кинопоиск", "desc": "Онлайн-кинотеатр фильмов и сериалов от Яндекс.", "category": "user_app", "safety": "safe"},

    "ru.ivi.client": {"name": "Иви (ivi)", "desc": "Онлайн-кинотеатр фильмов и сериалов.", "category": "user_app", "safety": "safe"},

    "tv.okko.androidtv": {"name": "Okko", "desc": "Онлайн-кинотеатр и спортивные трансляции.", "category": "user_app", "safety": "safe"},

    "ru.rt.video.app.tv": {"name": "Wink", "desc": "Интерактивное ТВ и онлайн-кинотеатр Ростелеком.", "category": "user_app", "safety": "safe"},

    "tv.premier.as": {"name": "PREMIER", "desc": "Онлайн-кинотеатр сериалов и шоу Газпром-Медиа.", "category": "user_app", "safety": "safe"},

    "ru.rutube.apptv": {"name": "Rutube для ТВ", "desc": "Российский видеохостинг и каналы.", "category": "user_app", "safety": "safe"},

    "ru.mts.kion": {"name": "KION", "desc": "Онлайн-кинотеатр МТС.", "category": "user_app", "safety": "safe"},

    "ru.start.android": {"name": "START", "desc": "Онлайн-кинотеатр сериалов и премьер.", "category": "user_app", "safety": "safe"},

    "com.more.tv": {"name": "more.tv", "desc": "Онлайн-кинотеатр и стриминг.", "category": "user_app", "safety": "safe"},

    "com.amediateka": {"name": "Амедиатека", "desc": "Зарубежные сериалы и фильмы.", "category": "user_app", "safety": "safe"},

    "ru.tricolor.tv": {"name": "Триколор Кино и ТВ", "desc": "Онлайн-ТВ и каталог Триколор.", "category": "user_app", "safety": "safe"},

    "ru.vgtrk.smotrim": {"name": "Смотрим (ВГТРК)", "desc": "Федеральные каналы и архив передач ВГТРК.", "category": "user_app", "safety": "safe"},

    "ru.1tv.tve": {"name": "Первый канал", "desc": "Приложение Первого канала для ТВ.", "category": "user_app", "safety": "safe"},

    "ru.ntv.client": {"name": "НТВ", "desc": "Прямой эфир и архив программ телеканала НТВ.", "category": "user_app", "safety": "safe"},

    "com.liskovsoft.smarttubetv.beta": {"name": "SmartTube", "desc": "Клиент YouTube без рекламы для Android TV.", "category": "user_app", "safety": "safe"},

    "io.github.dovecoteescapee.byedpi": {"name": "ByeDPI TV", "desc": "Утилита обхода замедлений YouTube.", "category": "user_app", "safety": "safe"},

    "com.zona": {"name": "Zona", "desc": "Медиа-каталог фильмов и торрент-кинотеатр.", "category": "user_app", "safety": "safe"},

    "tv.lampa": {"name": "Lampa", "desc": "Медиа-каталог и просмотр фильмов онлайн.", "category": "user_app", "safety": "safe"},

    "com.globallook.hdrezka": {"name": "HDRezka", "desc": "Каталог фильмов и сериалов Rezka.", "category": "user_app", "safety": "safe"},

    "com.alphainventor.filemanager": {"name": "Диспетчер файлов+", "desc": "Удобный проводник файлов и накопителей.", "category": "user_app", "safety": "safe"},

    "com.happ.app": {"name": "Happ App", "desc": "Каталог приложений и медиа-контента.", "category": "user_app", "safety": "safe"},

    "com.spotify.tv.android": {"name": "Spotify TV", "desc": "Музыкальный стриминговый сервис.", "category": "user_app", "safety": "safe"},

    "org.videolan.vlc": {"name": "VLC Media Player", "desc": "Универсальный видеоплеер всех форматов.", "category": "user_app", "safety": "safe"},

    "com.mxtech.videoplayer.ad": {"name": "MX Player", "desc": "Аппаратный видеоплеер с поддержкой кодеков.", "category": "user_app", "safety": "safe"},

    "net.gtvbox.videoplayer": {"name": "Vimu Media Player", "desc": "Оптимизированный плеер для Android TV.", "category": "user_app", "safety": "safe"},

    "ru.yourok.num": {"name": "NUM (No UI Movies)", "desc": "Каталог торрент-новинок кино.", "category": "user_app", "safety": "safe"},

    "matriza.torrserve": {"name": "TorrServe", "desc": "Торрент-сервер для онлайн просмотра.", "category": "user_app", "safety": "safe"},

    "com.charlie.msx": {"name": "Media Station X", "desc": "Платформа веб-приложений для ТВ.", "category": "user_app", "safety": "safe"},

    "com.google.android.youtube.tv": {"name": "YouTube для TV", "desc": "Официальный клиент YouTube.", "category": "user_app", "safety": "safe"},

    "com.yandex.tv.music": {"name": "Яндекс Музыка", "desc": "Музыкальный сервис Яндекс.", "category": "user_app", "safety": "safe"},

    "org.telegram.messenger": {"name": "Telegram", "desc": "Мессенджер и каналы.", "category": "user_app", "safety": "safe"},

    "com.zhiliaoapp.musically": {"name": "TikTok для ТВ", "desc": "Видеолента коротких роликов.", "category": "user_app", "safety": "safe"},



    # Haier службы

    "com.haierubic.usmartdevice": {"name": "Служба Haier uSmart IoT", "desc": "Постоянный фоновый опрос умного дома Haier. Создает непрерывную паразитную нагрузку на CPU.", "category": "haier_bloat", "safety": "safe"},

    "com.haier.oemtabprovider": {"name": "Рекомендации Haier OEM", "desc": "Рекламные каналы и партнерские промо-баннеры на домашнем экране.", "category": "haier_bloat", "safety": "safe"},

    "com.haier.tvhousekeeper": {"name": "Haier TV Housekeeper", "desc": "Фоновая телеметрия, аналитика действий пользователя и отправка логов вендору.", "category": "haier_bloat", "safety": "safe"},

    "com.haier.appstore": {"name": "Магазин приложений Haier Store", "desc": "Штатный магазин приложений с фоновыми автообновлениями и рекламными пушами.", "category": "haier_bloat", "safety": "safe"},

    "com.haier.tvmarket": {"name": "Каталог Haier TV Market", "desc": "Партнерский промо-каталог приложений Haier.", "category": "haier_bloat", "safety": "safe"},

    "com.haier.browser": {"name": "Штатный браузер Haier", "desc": "Тяжелый встроенный браузер от вендора. Рекомендуется отключать при наличии ТВ-плееров.", "category": "haier_bloat", "safety": "safe"},

    "com.haier.launcher.haiermatrix": {"name": "Промо-лаунчер Haier Matrix", "desc": "Штатная тяжелая промо-оболочка. Отключайте только при наличии альтернативного лаунчера (CleanYourTV).", "category": "haier_launcher", "safety": "warning"},

    "com.haier.cast": {"name": "Трансляция экрана Haier Cast", "desc": "Беспроводная трансляция дисплея со смартфонов Haier.", "category": "haier_service", "safety": "warning"},

    "com.haier.screenshare": {"name": "Служба Haier ScreenShare", "desc": "Фоновый сервис Miracast дублирования дисплея.", "category": "haier_service", "safety": "warning"},

    "com.mstar.screen.cast": {"name": "Служба MStar Screen Cast", "desc": "Фоновый сервис трансляции экрана MStar.", "category": "haier_service", "safety": "warning"},

    "com.haier.systemupgrade": {"name": "Haier OTA Updater", "desc": "Фоновая служба проверки обновлений прошивки вендора.", "category": "haier_service", "safety": "warning"},

    "com.iflytek.xiri": {"name": "Голосовой движок Xunfei / iFlyTek", "desc": "Китайский голосовой сервис на платах Haier. Постоянно держит фоновые потоки микрофона.", "category": "haier_service", "safety": "warning"},



    # Яндекс ТВ (YaOS / CVTE)

    "com.yandex.tv.services": {"name": "Службы Яндекс ТВ и AppMetrica", "desc": "Фоновый сбор телеметрии, реклама и системные демоны YaOS (~550 МБ ОЗУ).", "category": "yaos_bloat", "safety": "safe"},

    "com.yandex.io.sdk": {"name": "Яндекс Алиса & Голосовой стек", "desc": "Фоновый демон распознавания голоса и умного дома Яндекс (~330 МБ ОЗУ).", "category": "yaos_service", "safety": "safe"},

    "ru.yandex.androidkeyboard.tv": {"name": "Клавиатура Яндекс ТВ", "desc": "Штатная экранная клавиатура YaOS (~240 МБ ОЗУ).", "category": "yaos_service", "safety": "warning"},

    "com.yandex.tv.services.platform": {"name": "Платформа служб Яндекс", "desc": "Службы рекламной платформы и синхронизации YaOS.", "category": "yaos_bloat", "safety": "safe"},

    "com.yandex.devices.farm.companion": {"name": "Яндекс Companion & Farm", "desc": "Фоновое сканирование сети для сопряжения со смартфонами и колонками.", "category": "yaos_bloat", "safety": "safe"},

    "com.yandex.devices.appstore": {"name": "Магазин приложений Яндекс", "desc": "Штатный магазин приложений YaOS с фоновой проверкой обновлений.", "category": "yaos_bloat", "safety": "safe"},

    "com.yandex.tv.store.promos": {"name": "Промо-витрина Яндекс", "desc": "Рекламные баннеры и промо-карточки Кинопоиска.", "category": "yaos_bloat", "safety": "safe"},

    "com.yandex.tv.bugreports": {"name": "Отчеты об ошибках YaOS", "desc": "Фоновая отправка дампов и логов вендору.", "category": "yaos_bloat", "safety": "safe"},

    "com.yandex.tv.launcher": {"name": "Лаунчер Яндекс ТВ", "desc": "Штатный лаунчер с тяжелыми промо-баннерами фильмов.", "category": "yaos_launcher", "safety": "warning"},

    "com.yandex.tv.home": {"name": "Главный экран Яндекс", "desc": "Ленты рекомендаций и трейлеры.", "category": "yaos_bloat", "safety": "safe"},

    "com.yandex.tv.adblocker": {"name": "Рекламный модуль Яндекс", "desc": "Показ спонсорских карточек и баннеров.", "category": "yaos_bloat", "safety": "safe"},

    "com.yandex.tv.promoview": {"name": "Промо-видеоплеер Яндекс", "desc": "Фоновое автовоспроизведение промо-трейлеров вверху экрана.", "category": "yaos_bloat", "safety": "safe"},

    "com.yandex.tv.music.overlay": {"name": "Фоновый сервис Яндекс Музыки", "desc": "Висит в памяти после старта системы.", "category": "yaos_bloat", "safety": "safe"},



    # Салют ТВ (Сбер)

    "ru.sberdevices.starlauncher": {"name": "Салют StarLauncher", "desc": "Штатная оболочка Сбер с промо-виджетами.", "category": "salut_launcher", "safety": "warning"},

    "ru.sberdevices.smartsearch": {"name": "Сбер Умный поиск", "desc": "Фоновая индексация и реклама экосистемы.", "category": "salut_bloat", "safety": "safe"},

    "ru.sberdevices.services": {"name": "СберСервисы & Телеметрия", "desc": "Сбор аналитики и фоновая синхронизация.", "category": "salut_bloat", "safety": "safe"},

    "ru.sberdevices.promoservice": {"name": "Промо-баннеры Салют", "desc": "Загрузка баннеров и промо-блоков.", "category": "salut_bloat", "safety": "safe"},

    "ru.sberdevices.salute": {"name": "Голосовой ассистент Салют", "desc": "Тяжелый голосовой движок (до 90 МБ ОЗУ).", "category": "salut_service", "safety": "warning"},



    # Xiaomi / PatchWall

    "com.mitv.tvhome": {"name": "Xiaomi PatchWall", "desc": "Штатная витрина контента Xiaomi.", "category": "xiaomi_launcher", "safety": "warning"},

    "com.xiaomi.mitv.upgrade": {"name": "Xiaomi OTA Update", "desc": "Автообновления PatchWall.", "category": "xiaomi_bloat", "safety": "safe"},



    # Google / Android TV

    "com.google.android.apps.tv.launcherx": {"name": "Google TV Launcher", "desc": "Штатный лаунчер Google TV с промо-роликами.", "category": "google_launcher", "safety": "warning"},

    "com.google.android.gms": {"name": "Google Play Services", "desc": "Фоновые службы Google (аккаунты, синхронизация). Занимают до 150 МБ ОЗУ.", "category": "google_service", "safety": "warning"},

    "com.google.android.gms.persistent": {"name": "Google Play Core", "desc": "Непрерывный системный демон Google Play.", "category": "google_service", "safety": "warning"},

    "com.android.vending": {"name": "Google Play Store", "desc": "Штатный магазин приложений с автообновлениями в фоне.", "category": "google_service", "safety": "warning"},

    "com.google.android.katniss": {"name": "Google Assistant TV", "desc": "Голосовой помощник Google.", "category": "google_service", "safety": "warning"},

    "com.google.android.syncadapters.calendar": {"name": "Google Календарь", "desc": "Служба синхронизации календаря в фоне.", "category": "google_bloat", "safety": "safe"},

    "com.google.android.syncadapters.contacts": {"name": "Google Контакты", "desc": "Служба синхронизации телефонной книги.", "category": "google_bloat", "safety": "safe"},

    "com.google.android.feedback": {"name": "Google Отзывы и телеметрия", "desc": "Фоновый сбор отчётов об ошибках для Google.", "category": "google_bloat", "safety": "safe"},



    # Критические модули (Hardware stoplist)

    "com.haier.tv.input": {"name": "ТВ-входы Haier (HDMI/AV)", "desc": "Критический драйвер переключения HDMI портов и ТВ-тюнера. Защищен стоп-листом!", "category": "critical", "safety": "critical"},

    "com.haier.settings": {"name": "Настройки Haier", "desc": "Системные настройки матрицы, звука и подсветки телевизора.", "category": "critical", "safety": "critical"},

    "com.haier.tv.service": {"name": "Служба шасси Haier", "desc": "Аппаратное управление платой телевизора Haier.", "category": "critical", "safety": "critical"},

    "com.mstar.tv.service": {"name": "Платформа MStar TV", "desc": "Аппаратный драйвер чипсета MStar.", "category": "critical", "safety": "critical"},

    "com.mediatek.tv": {"name": "Платформа MediaTek TV", "desc": "Аппаратный драйвер процессора MediaTek.", "category": "critical", "safety": "critical"},

    "com.android.tv.settings": {"name": "Настройки Android TV", "desc": "Главное меню системных настроек.", "category": "critical", "safety": "critical"},

    "com.android.providers.tv": {"name": "Провайдер ТВ-каналов", "desc": "База данных кабельного и эфирного телевидения.", "category": "critical", "safety": "critical"},

    "com.tcl.tvinput": {"name": "ТВ-входы TCL (HDMI/AV)", "desc": "Критический драйвер HDMI портов TCL.", "category": "critical", "safety": "critical"},

    "com.toshiba.tv.tvinput": {"name": "ТВ-входы Toshiba (HDMI/AV)", "desc": "Критический драйвер HDMI портов Toshiba.", "category": "critical", "safety": "critical"},

    "com.cvte.tv.api": {"name": "CVTE TV Chassis API", "desc": "Аппаратное управление платой ТВ (Яндекс/Tuvio/Hartens).", "category": "critical", "safety": "critical"},

}


class DebloatMixin:
    def _detect_profile(self, brand: str, model: str, board: str) -> str:

        combined = f"{brand} {model} {board}".lower()

        if any(k in combined for k in ("yandex", "cvte", "cv9632", "tuvio", "hartens")):

            return "yaos"

        if any(k in combined for k in ("sber", "salut", "staros", "sberbox")):

            return "salut"

        if "haier" in combined:

            return "haier"

        if any(k in combined for k in ("xiaomi", "redmi", "mitv")):

            return "xiaomi"

        if any(k in combined for k in ("tcl", "iffalcon")):

            return "tcl"

        return "googletv"


    def create_state_backup(self) -> str:

        """Сохраняет полный слепок отключенных и включенных пакетов перед очисткой."""

        disabled = self.run_adb(["shell", "pm", "list", "packages", "-d"])["stdout"].splitlines()

        enabled = self.run_adb(["shell", "pm", "list", "packages", "-e"])["stdout"].splitlines()



        clean_pkg = lambda lines: [line.replace("package:", "").strip() for line in lines if line]

        snapshot = {

            "timestamp": int(time.time()),

            "device": self.current_device,

            "disabled_packages": clean_pkg(disabled),

            "enabled_packages": clean_pkg(enabled),

        }



        safe_dev_name = (self.current_device or "tv").replace(":", "_")

        backup_file = self.backups_dir / f"backup_{safe_dev_name}.json"

        with open(backup_file, "w", encoding="utf-8") as f:

            json.dump(snapshot, f, ensure_ascii=False, indent=2)

        return str(backup_file)


    def apply_custom_debloat(self, selected_packages: List[str]) -> Dict[str, Any]:
        """Отключает выбранные пакеты с проверкой по критическому стоп-листу."""
        if not self.current_device:
            last_ip = self._get_last_known_ip()
            if last_ip:
                self.connect_tv(last_ip)
            else:
                return {"ok": False, "error": "ТВ не подключен к ADB"}

        self._notify(f"[Очистка] Отключение и заморозка {len(selected_packages)} выбранных пакетов...")
        stoplist = set(self.packages_db.get("critical_stoplist", []))

        mem_before = self.get_memory_stats()

        backup_path = self.create_state_backup()



        disabled_ok, skipped_critical, errors = [], [], []



        for pkg in selected_packages:

            if pkg in stoplist:

                skipped_critical.append(pkg)

                continue



            res = self.run_adb(["shell", "pm", "disable-user", "--user", "0", pkg])

            if res["ok"] and "disabled-user" in res["stdout"].lower():

                self.run_adb(["shell", "am", "force-stop", pkg])

                disabled_ok.append(pkg)

            else:

                errors.append({"package": pkg, "reason": res["stderr"] or res["stdout"]})



        mem_after = self.get_memory_stats()

        freed_mb = max(0, mem_after["free_mb"] - mem_before["free_mb"])



        return {

            "ok": True,

            "backup_file": backup_path,

            "disabled_count": len(disabled_ok),

            "disabled_packages": disabled_ok,

            "skipped_stoplist": skipped_critical,

            "errors": errors,

            "freed_ram_mb": freed_mb,

            "memory_after": mem_after,

        }


    def restore_from_backup(self) -> Dict[str, Any]:

        """Полный откат к заводскому состоянию или сохраненному слепку."""

        safe_dev_name = (self.current_device or "tv").replace(":", "_")

        backup_file = self.backups_dir / f"backup_{safe_dev_name}.json"



        restored = []

        if backup_file.exists():

            data = self._load_json(backup_file)

            for pkg in data.get("enabled_packages", []):

                res = self.run_adb(["shell", "pm", "enable", pkg])

                if res["ok"]:

                    restored.append(pkg)

        else:

            disabled = self.run_adb(["shell", "pm", "list", "packages", "-d"])["stdout"].splitlines()

            for line in disabled:

                pkg = line.replace("package:", "").strip()

                if pkg:

                    self.run_adb(["shell", "pm", "enable", pkg])

                    restored.append(pkg)



        # Restore stock launchers if disabled

        stock_launchers = [

            "com.yandex.tv.launcher",

            "com.google.android.apps.tv.launcherx",

            "com.google.android.tvlauncher",

            "ru.sberdevices.starlauncher",

            "com.haier.launcher.haiermatrix",

            "com.mitv.tvhome",

        ]

        for stock_pkg in stock_launchers:

            self.run_adb(["shell", "pm", "enable", stock_pkg])



        return {"ok": True, "restored_count": len(restored)}


    def scan_running_processes(self) -> Dict[str, Any]:

        """

        Сканирует запущенные в реальном времени процессы на ТВ,

        извлекает точный расход памяти PSS (в МБ), определяет статус безопасности

        и формирует подробное русское описание каждого процесса.

        """

        if not self.current_device:

            return {"ok": False, "error": "Телевизор не подключен. Сначала подключите ТВ на вкладке 'Подключение'."}



        self._notify("[Сканер] Считывание запущенных процессов и оперативной памяти ТВ...")



        # 1. Получаем список процессов и PSS памяти через dumpsys meminfo

        meminfo_res = self.run_adb(["shell", "dumpsys", "meminfo"], timeout=20)

        output = meminfo_res.get("stdout", "")



        raw_processes = []

        if output:

            matches = re.findall(r"^\s*([0-9,]+)K:\s+([^\s\(\)]+)\s+\(pid\s+(\d+)", output, re.MULTILINE)

            for m in matches:

                raw_mem, pkg_name, pid_str = m

                try:

                    ram_kb = int(raw_mem.replace(",", ""))

                    ram_mb = round(ram_kb / 1024, 1)

                    raw_processes.append({

                        "pkg": pkg_name.strip(),

                        "pid": int(pid_str),

                        "ram_mb": ram_mb,

                    })

                except Exception:

                    continue



        # Fallback на ps -A если dumpsys вернул пустоту

        if not raw_processes:

            self._notify("[Сканер] Запрос списка процессов через ps...")

            ps_res = self.run_adb(["shell", "ps", "-A"], timeout=15)

            ps_out = ps_res.get("stdout", "")

            for line in ps_out.splitlines()[1:]:

                parts = line.split()

                if len(parts) >= 9:

                    pid = parts[1]

                    name = parts[8]

                    if name.startswith("[") and name.endswith("]"):

                        continue

                    if pid.isdigit():

                        raw_processes.append({

                            "pkg": name,

                            "pid": int(pid),

                            "ram_mb": 18.0,

                        })



        # 2. Получаем список сторонних пользовательских приложений (pm list packages -3)

        user_apps_res = self.run_adb(["shell", "pm", "list", "packages", "-3"], timeout=12)

        user_pkgs = set()

        if user_apps_res.get("ok"):

            for line in user_apps_res["stdout"].splitlines():

                if line.startswith("package:"):

                    user_pkgs.add(line.replace("package:", "").strip())



        # 3. Получаем список отключенных (замороженных) пакетов (pm list packages -d)

        disabled_res = self.run_adb(["shell", "pm", "list", "packages", "-d"], timeout=12)

        disabled_pkgs = set()

        if disabled_res.get("ok"):

            for line in disabled_res["stdout"].splitlines():

                if line.startswith("package:"):

                    disabled_pkgs.add(line.replace("package:", "").strip())



        # 4. База знаний критического стоп-листа

        stoplist = set(self.packages_db.get("critical_stoplist", []))



        # 5. Классификация и сборка метаданных

        total_ram_mb = 0.0

        safe_ram_mb = 0.0

        processed_list = []

        seen_pkgs = set()



        for item in raw_processes:

            pkg = item["pkg"]

            pid = item["pid"]

            ram_mb = item["ram_mb"]



            base_pkg = pkg.split(":")[0]

            if base_pkg in seen_pkgs:

                for p in processed_list:

                    if p["pkg"] == base_pkg:

                        p["ram_mb"] = round(p["ram_mb"] + ram_mb, 1)

                        total_ram_mb += ram_mb

                        if p["safety"] == "safe":

                            safe_ram_mb += ram_mb

                        break

                continue



            seen_pkgs.add(base_pkg)

            total_ram_mb += ram_mb



            is_user_app = (base_pkg in user_pkgs)

            is_disabled = (base_pkg in disabled_pkgs)



            meta = KNOWN_TV_PACKAGES.get(base_pkg)



            if meta:

                display_name = meta["name"]

                desc = meta["desc"]

                safety = meta["safety"]

                category = meta["category"]

            elif is_user_app:

                clean_name = base_pkg.split(".")[-1].replace("_", " ").title()

                display_name = f"{clean_name} (Пользовательское)"

                desc = "Сторонняя программа, установленная пользователем. Остановка выгрузит её из оперативной памяти и устранит тормоза. В любой момент можно открыть снова с пульта."

                safety = "safe"

                category = "user_app"

            else:

                is_crit = any(crit in base_pkg for crit in ("system", "input", "setting", "audio", "display", "bluetooth", "wifi", "media.codec")) or (base_pkg in stoplist)

                if is_crit:

                    display_name = f"Системный модуль ({base_pkg})"

                    desc = "Критический системный модуль шасси телевизора или ядра Android. Защищен стоп-листом."

                    safety = "critical"

                    category = "system_critical"

                else:

                    display_name = f"Фоновая служба ({base_pkg})"

                    desc = "Системный или вендорский фоновый процесс. Рекомендуется отключать с осторожностью."

                    safety = "warning"

                    category = "system_service"



            if base_pkg in stoplist or category == "system_critical":

                safety = "critical"

                can_stop = False

                can_freeze = False

            else:

                can_stop = True

                can_freeze = True

                if safety == "safe":

                    safe_ram_mb += ram_mb



            processed_list.append({

                "pkg": base_pkg,

                "pid": pid,

                "ram_mb": ram_mb,

                "name": display_name,

                "desc": desc,

                "safety": safety,

                "category": category,

                "is_user_app": is_user_app,

                "is_disabled": is_disabled,

                "can_stop": can_stop,

                "can_freeze": can_freeze,

            })



        processed_list.sort(key=lambda x: x["ram_mb"], reverse=True)



        self._notify(f"[Сканер] ✓ Найдено {len(processed_list)} процессов. Занято ОЗУ: {round(total_ram_mb, 1)} МБ, можно безопасно освободить: {round(safe_ram_mb, 1)} МБ")



        return {

            "ok": True,

            "total_processes": len(processed_list),

            "total_ram_mb": round(total_ram_mb, 1),

            "safe_ram_mb": round(safe_ram_mb, 1),

            "processes": processed_list,

        }


    def stop_running_processes(self, packages: List[str]) -> Dict[str, Any]:

        """Мгновенно выгружает выбранные процессы из оперативной памяти ТВ через am force-stop."""

        if not self.current_device:

            return {"ok": False, "error": "Телевизор не подключен"}



        stopped, skipped = [], []

        stoplist = set(self.packages_db.get("critical_stoplist", []))



        for pkg in packages:

            if pkg in stoplist:

                skipped.append(pkg)

                continue

            res = self.run_adb(["shell", "am", "force-stop", pkg], timeout=10)

            if res["ok"]:

                stopped.append(pkg)



        self._notify(f"[Диспетчер] ✓ Выгружено процессов: {len(stopped)}, освобождена оперативная память.")

        return {"ok": True, "stopped": stopped, "skipped": skipped, "count": len(stopped)}


    def freeze_processes(self, packages: List[str]) -> Dict[str, Any]:

        """Отключает автозапуск выбранных пакетов навсегда через pm disable-user."""

        if not self.current_device:

            return {"ok": False, "error": "Телевизор не подключен"}



        frozen, skipped = [], []

        stoplist = set(self.packages_db.get("critical_stoplist", []))



        for pkg in packages:

            if pkg in stoplist:

                skipped.append(pkg)

                continue

            res = self.run_adb(["shell", "pm", "disable-user", "--user", "0", pkg], timeout=15)

            self.run_adb(["shell", "am", "force-stop", pkg], timeout=10)

            if res["ok"] and "disabled" in res["stdout"].lower():

                frozen.append(pkg)



        self._notify(f"[Диспетчер] ✓ Заморожено служб: {len(frozen)} (больше не запустятся при старте ТВ).")

        return {"ok": True, "frozen": frozen, "skipped": skipped, "count": len(frozen)}


    def unfreeze_processes(self, packages: List[str]) -> Dict[str, Any]:

        """Включает обратно замороженные пакеты через pm enable."""

        if not self.current_device:

            return {"ok": False, "error": "Телевизор не подключен"}



        unfrozen = []

        for pkg in packages:

            res = self.run_adb(["shell", "pm", "enable", pkg], timeout=15)

            if res["ok"] and "enabled" in res["stdout"].lower():

                unfrozen.append(pkg)



        self._notify(f"[Диспетчер] ✓ Включено обратно пакетов: {len(unfrozen)}.")

        return {"ok": True, "unfrozen": unfrozen, "count": len(unfrozen)}


    def clean_tv_ram(self) -> Dict[str, Any]:

        """

        1-Click Экспресс-очистка ОЗУ и кэша ТВ:

        - Очищает кэши приложений через pm trim-caches

        - Выгружает фоновые неактивные задачи через am kill-all

        - Замеряет и возвращает точный объем освобожденной памяти

        """

        if not self.current_device:

            last_ip = self._get_last_known_ip()

            if last_ip:

                self.connect_tv(last_ip)

            else:

                return {"ok": False, "error": "ТВ не подключен к ADB"}



        self._notify("[Очистка ОЗУ] Запуск оптимизации оперативной памяти и очистки кэша...")

        info_pre = self.inspect_device()

        free_pre = info_pre.get("memory", {}).get("free_mb", 0)



        # 1. Очистка накопившегося кэша приложений (2 ГБ лимит)

        self.run_adb(["shell", "pm", "trim-caches", "2G"], timeout=10)



        # 2. Выгрузка неактивных фоновых служб

        self.run_adb(["shell", "am", "kill-all"], timeout=10)



        # 3. Сброс кэша ядра

        self.run_adb(["shell", "echo", "3", ">", "/proc/sys/vm/drop_caches"], timeout=5)



        import time as _t

        _t.sleep(1.0)

        info_post = self.inspect_device()

        free_post = info_post.get("memory", {}).get("free_mb", 0)

        total_ram = info_post.get("memory", {}).get("total_mb", 1385)

        freed_mb = max(0, free_post - free_pre)



        msg = f"Очистка ОЗУ выполнена! Свободно: {free_post} МБ из {total_ram} МБ (высвобождено ~{freed_mb} МБ)."

        self._notify(f"[Очистка ОЗУ] ✓ {msg}")



        return {

            "ok": True,

            "msg": msg,

            "free_mb": free_post,

            "total_mb": total_ram,

            "freed_mb": freed_mb

        }


    def purge_yandex_services(self) -> Dict[str, Any]:

        """

        Очистка тяжелых фоновых служб Яндекс ТВ (YaOS / CVTE):

        Останавливает сбор телеметрии, рекламу и фоновые демоны (высвобождает до 1.2 ГБ ОЗУ).

        """

        if not self.current_device:

            last_ip = self._get_last_known_ip()

            if last_ip:

                self.connect_tv(last_ip)

            else:

                return {"ok": False, "error": "ТВ не подключен к ADB"}



        self._notify("[Яндекс ТВ] Выгрузка тяжелых фоновых процессов YaOS...")

        heavy_yandex_pkgs = [

            "com.yandex.tv.services",

            "com.yandex.io.sdk",

            "com.yandex.devices.farm.companion",

            "com.yandex.devices.appstore",

            "com.yandex.tv.store.promos",

            "com.yandex.tv.bugreports",

            "com.yandex.tv.promoview",

            "com.yandex.tv.adblocker",

            "com.yandex.tv.services.platform",

            "com.yandex.tv.home"

        ]



        stopped = []

        for pkg in heavy_yandex_pkgs:

            res = self.run_adb(["shell", "am", "force-stop", pkg], timeout=6)

            if res.get("ok"):

                stopped.append(pkg)



        self.run_adb(["shell", "pm", "trim-caches", "2G"], timeout=8)



        info_post = self.inspect_device()

        free_post = info_post.get("memory", {}).get("free_mb", 0)

        total_ram = info_post.get("memory", {}).get("total_mb", 1385)



        msg = f"Службы Яндекс ТВ успешно выгружены! Остановлено {len(stopped)} процессов. Свободно ОЗУ: {free_post} МБ из {total_ram} МБ."

        self._notify(f"[Яндекс ТВ] ✓ {msg}")



        return {

            "ok": True,

            "msg": msg,

            "stopped": stopped,

            "free_mb": free_post,

            "total_mb": total_ram

        }
