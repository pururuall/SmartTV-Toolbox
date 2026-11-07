import json
import os
import sys
import re
import socket
import subprocess
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

    # Яндекс ТВ (YaOS)
    "com.yandex.tv.launcher": {"name": "Лаунчер Яндекс ТВ", "desc": "Штатный лаунчер с тяжелыми промо-баннерами фильмов.", "category": "yaos_launcher", "safety": "warning"},
    "com.yandex.tv.home": {"name": "Главный экран Яндекс", "desc": "Ленты рекомендаций и трейлеры.", "category": "yaos_bloat", "safety": "safe"},
    "com.yandex.io.sdk": {"name": "Яндекс Алиса & Голосовой стек", "desc": "Фоновое распознавание и службы умного дома Яндекс.", "category": "yaos_service", "safety": "warning"},
    "com.yandex.tv.adblocker": {"name": "Рекламный модуль Яндекс", "desc": "Показ спонсорских карточек и баннеров.", "category": "yaos_bloat", "safety": "safe"},
    "com.yandex.tv.promoview": {"name": "Промо-видеоплеер Яндекс", "desc": "Фоновое автовоспроизведение промо-трейлеров вверху экрана.", "category": "yaos_bloat", "safety": "safe"},

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
    "com.google.android.gms": {"name": "Google Play Services", "desc": "Фоновые службы Google (синхронизация, аккаунты, реклама). Занимают до 150 МБ ОЗУ.", "category": "google_service", "safety": "warning"},
    "com.google.android.gms.persistent": {"name": "Google Play Core", "desc": "Непрерывный системный демон Google Play.", "category": "google_service", "safety": "warning"},
    "com.android.vending": {"name": "Google Play Маркет", "desc": "Магазин приложений и фоновая проверка обновлений.", "category": "google_service", "safety": "warning"},
    "com.google.android.katniss": {"name": "Google Assistant TV", "desc": "Голосовой помощник Google.", "category": "google_service", "safety": "warning"},
    "com.google.android.syncadapters.calendar": {"name": "Google Календарь (Синхронизация)", "desc": "Бесполезная на ТВ фоновая синхронизация календаря.", "category": "google_bloat", "safety": "safe"},
    "com.google.android.syncadapters.contacts": {"name": "Google Контакты (Синхронизация)", "desc": "Бесполезная на ТВ фоновая синхронизация адресной книги.", "category": "google_bloat", "safety": "safe"},
    "com.google.android.feedback": {"name": "Google Отчёты об ошибках", "desc": "Сбор и отправка отчётов о сбоях в Google.", "category": "google_bloat", "safety": "safe"},

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


class SmartTVManager:
    """
    Единый контроллер SmartTV-Toolbox v4.0.
    Объединяет наработки SmartTV-Toolbox, tv-cleaner, moy-tv и chistytv.
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

    def _resolve_file(self, rel_path: str) -> Path:
        for root in [self.exe_dir, self.meipass_dir, self.base_dir]:
            p = root / rel_path
            if p.exists():
                return p
        return self.base_dir / rel_path

    def _resolve_adb_binary(self) -> str:
        candidates = [
            self.exe_dir / "platform-tools" / "adb.exe",
            self.meipass_dir / "platform-tools" / "adb.exe",
            self.base_dir / "platform-tools" / "adb.exe",
        ]
        for c in candidates:
            if c.exists():
                return str(c)
        return "adb"

    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def is_valid_apk(self, path: Optional[Path]) -> bool:
        """Проверяет существование файла, минимальный размер (>1000 байт) и сигнатуру zip/apk."""
        try:
            if not path:
                return False
            p = Path(path)
            if not p.is_file():
                return False
            if p.stat().st_size < 1000:
                return False
            with open(p, "rb") as f:
                return f.read(4) == b"PK\x03\x04"
        except Exception:
            return False

    def _notify(self, msg: str, status_cb=None):
        if status_cb and callable(status_cb):
            try:
                status_cb(msg)
            except Exception:
                pass
        try:
            import webview
            if getattr(webview, "windows", None) and len(webview.windows) > 0:
                import json
                webview.windows[0].evaluate_js(f"log({json.dumps(msg)})")
        except Exception:
            pass

    def resolve_apk(self, rel_path: str, status_cb=None) -> Optional[Path]:
        """
        Ищет APK в exe_dir, _MEIPASS, base_dir, плоских папках apps,
        проверяет сигнатуру файла (отсекает 131-байтные Git LFS указатели)
        и при необходимости автоматически скачивает файл из GitHub-репозитория.
        """
        if not rel_path:
            return None

        clean_rel = rel_path.replace("\\", "/").strip("/")
        filename = Path(clean_rel).name

        candidates = [
            self.exe_dir / clean_rel,
            self.meipass_dir / clean_rel,
            self.base_dir / clean_rel,
            self.exe_dir / "apps" / filename,
            self.base_dir / "apps" / filename,
            self.meipass_dir / "apps" / filename,
            Path.cwd() / clean_rel,
            Path.cwd() / "apps" / filename,
            Path.cwd() / filename,
            self.exe_dir / "apps" / filename.lower(),
            self.base_dir / "apps" / filename.lower(),
        ]

        for cand in candidates:
            if self.is_valid_apk(cand):
                return cand

        # Дополнительный рекурсивный поиск в папках apps (на случай вложенности или регистра)
        for root in [self.exe_dir, self.meipass_dir, self.base_dir, Path.cwd()]:
            if not root or not root.exists():
                continue
            apps_dir = root / "apps"
            if apps_dir.exists():
                for found_file in apps_dir.rglob("*.apk"):
                    if found_file.name.lower() == filename.lower() and self.is_valid_apk(found_file):
                        return found_file

        # Если локально нет или файл поврежден (например LFS указатель ~131 байт) — скачиваем из GitHub
        self._notify(f"[Облако] Скачивание {filename} из репозитория...", status_cb)

        target_dir = self.exe_dir / Path(clean_rel).parent
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = self.exe_dir / clean_rel
        except Exception:
            appdata = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "SmartTV_Toolbox"
            target_dir = appdata / Path(clean_rel).parent
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = appdata / clean_rel

        urls = [
            f"https://media.githubusercontent.com/media/pururuall/SmartTV-Toolbox/main/{clean_rel}",
            f"https://raw.githubusercontent.com/pururuall/SmartTV-Toolbox/main/{clean_rel}",
            f"https://github.com/pururuall/SmartTV-Toolbox/raw/main/{clean_rel}",
        ]
        if not clean_rel.startswith("apps/"):
            urls.insert(0, f"https://media.githubusercontent.com/media/pururuall/SmartTV-Toolbox/main/apps/{clean_rel}")

        import urllib.request
        import shutil

        temp_target = target_path.with_suffix(target_path.suffix + ".downloading")
        for url in urls:
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SmartTV-Toolbox/3.0",
                        "Accept": "*/*",
                    },
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    if resp.status == 200:
                        with open(temp_target, "wb") as f_out:
                            shutil.copyfileobj(resp, f_out)

                        if self.is_valid_apk(temp_target):
                            if target_path.exists():
                                target_path.unlink()
                            temp_target.replace(target_path)
                            size_kb = target_path.stat().st_size // 1024
                            self._notify(f"[Облако] ✓ {filename} успешно загружен ({size_kb} КБ)", status_cb)
                            return target_path
                        else:
                            if temp_target.exists():
                                temp_target.unlink()
            except Exception:
                if temp_target.exists():
                    try:
                        temp_target.unlink()
                    except Exception:
                        pass
                continue

        self._notify(f"[Ошибка] Не удалось скачать {filename} из GitHub.", status_cb)
        return None

    def run_adb(self, args: List[str], timeout: int = 20) -> Dict[str, Any]:
        """Безопасный вызов ADB с жестким контролем таймаута."""
        cmd = [self.adb_bin]
        if self.current_device:
            cmd.extend(["-s", self.current_device])
        cmd.extend(args)

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            return {
                "ok": proc.returncode == 0,
                "code": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "code": -1, "stdout": "", "stderr": "ADB Timeout expired"}
        except Exception as exc:
            return {"ok": False, "code": -2, "stdout": "", "stderr": str(exc)}

    def connect_tv(self, ip: str, port: int = 5555) -> Dict[str, Any]:
        target = f"{ip.strip()}:{port}"
        res = self.run_adb(["connect", target], timeout=12)
        stdout_lower = res["stdout"].lower()
        connected = "connected to" in stdout_lower or "already connected" in stdout_lower
        if connected:
            self.current_device = target
            info = self.inspect_device()
            return {"ok": True, "device": target, "info": info}
        return {"ok": False, "error": res["stdout"] or res["stderr"]}

    def wireless_pair(self, ip: str, pair_port: int, pair_code: str) -> Dict[str, Any]:
        """Сопряжение по 6-значному коду для Android 11–14 (Wireless Debugging)."""
        target = f"{ip.strip()}:{pair_port}"
        res = self.run_adb(["pair", target, pair_code.strip()], timeout=15)
        success = "successfully paired" in res["stdout"].lower()
        return {"ok": success, "output": res["stdout"] or res["stderr"]}

    def inspect_device(self) -> Dict[str, Any]:
        """Считывает параметры шасси, версию Android и статистику RAM/ZRAM."""
        brand = self.run_adb(["shell", "getprop", "ro.product.manufacturer"])["stdout"]
        model = self.run_adb(["shell", "getprop", "ro.product.model"])["stdout"]
        android_ver = self.run_adb(["shell", "getprop", "ro.build.version.release"])["stdout"]
        board = self.run_adb(["shell", "getprop", "ro.product.board"])["stdout"]
        mem = self.get_memory_stats()

        return {
            "brand": brand or "Unknown",
            "model": model or "Smart TV",
            "android_version": android_ver or "Unknown",
            "board": board or "Unknown",
            "memory": mem,
            "recommended_profile": self._detect_profile(brand, model, board),
        }

    def get_memory_stats(self) -> Dict[str, int]:
        """Парсит dumpsys meminfo для отображения загрузки ОЗУ и ZRAM до и после очистки."""
        res = self.run_adb(["shell", "dumpsys", "meminfo"], timeout=15)
        text = res["stdout"]

        def extract_kb(pattern: str) -> int:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = re.sub(r"[^\d]", "", match.group(1))
                return int(val) // 1024 if val else 0
            return 0

        total_mb = extract_kb(r"Total RAM:\s*([\d,]+)\s*K")
        free_mb = extract_kb(r"Free RAM:\s*([\d,]+)\s*K")
        used_mb = extract_kb(r"Used RAM:\s*([\d,]+)\s*K")
        zram_mb = extract_kb(r"([\d,]+)\s*K physical used for\s*[\d,]+\s*K in swap")

        if total_mb == 0:
            total_mb = 1536
            free_mb = 512
            used_mb = 1024

        return {
            "total_mb": total_mb,
            "free_mb": free_mb,
            "used_mb": used_mb,
            "zram_physical_mb": zram_mb,
        }

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

    def install_and_activate_launcher(
        self, launcher_id: str, disable_stock: bool = True
    ) -> Dict[str, Any]:
        """Устанавливает выбранный лаунчер и безопасно делает его главным экраном."""
        launchers = self.launchers_db.get("launchers", {})
        if launcher_id not in launchers:
            return {"ok": False, "error": f"Неизвестный лаунчер: {launcher_id}"}

        meta = launchers[launcher_id]
        self._notify(f"Поиск APK для лаунчера {meta.get('name', launcher_id)}...")
        apk_full_path = self.resolve_apk(meta["apk_path"])
        if not apk_full_path:
            return {"ok": False, "error": f"Файл APK не найден и не удалось скачать: {meta['apk_path']}"}

        self._notify(f"Установка APK на ТВ: {apk_full_path.name}...")
        inst_res = self.run_adb(["install", "-r", str(apk_full_path)], timeout=90)
        if not inst_res["ok"]:
            return {"ok": False, "error": f"Ошибка установки APK: {inst_res['stderr'] or inst_res['stdout']}"}

        component = f"{meta['package']}/{meta['main_activity']}"
        self.run_adb(["shell", "cmd", "package", "set-home-activity", component])

        if disable_stock:
            stock_launchers = [
                "com.yandex.tv.launcher",
                "com.google.android.apps.tv.launcherx",
                "com.google.android.tvlauncher",
                "ru.sberdevices.starlauncher",
                "com.haier.launcher.haiermatrix",
                "com.mitv.tvhome",
            ]
            for stock_pkg in stock_launchers:
                self.run_adb(["shell", "pm", "disable-user", "--user", "0", stock_pkg])

        self.run_adb(["shell", "am", "start", "-n", component])

        web_remote_url = None
        if meta.get("supports_web_remote") and self.current_device:
            ip_only = self.current_device.split(":")[0]
            web_remote_url = f"http://{ip_only}:{meta['web_remote_port']}"

        return {
            "ok": True,
            "launcher": meta["name"],
            "web_remote_url": web_remote_url,
        }

    def push_launcher_wallpaper(self, launcher_id: str, local_image_path: str) -> Dict[str, Any]:
        """Загружает кастомный фон с компьютера напрямую в выбранный лаунчер на ТВ."""
        launchers = self.launchers_db.get("launchers", {})
        meta = launchers.get(launcher_id)
        if not meta or not meta.get("supports_custom_wallpaper"):
            return {"ok": False, "error": "Выбранный лаунчер не поддерживает прямую загрузку обоев."}

        remote_path = meta["wallpaper_remote_path"]
        remote_dir = os.path.dirname(remote_path).replace("\\", "/")
        self.run_adb(["shell", "mkdir", "-p", remote_dir])

        push_res = self.run_adb(["push", local_image_path, remote_path], timeout=30)
        if not push_res["ok"]:
            return {"ok": False, "error": push_res["stderr"]}

        self.run_adb([
            "shell", "am", "broadcast",
            "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
            "-d", f"file://{remote_path}"
        ])
        self.run_adb(["shell", "am", "force-stop", meta["package"]])
        self.run_adb(["shell", "am", "start", "-n", f"{meta['package']}/{meta['main_activity']}"])

        return {"ok": True, "remote_path": remote_path}

    def save_launcher_config(self, launcher_id: str, config_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Отправляет JSON-конфигурацию лаунчера (слоты дока, погода, HDMI 1-3) на ТВ."""
        launchers = self.launchers_db.get("launchers", {})
        meta = launchers.get(launcher_id)
        if not meta or not meta.get("config_remote_path"):
            return {"ok": False, "error": "Для этого лаунчера нет прямого конфигурационного пути."}

        temp_cfg = self.backups_dir / f"temp_{launcher_id}_config.json"
        with open(temp_cfg, "w", encoding="utf-8") as f:
            json.dump(config_payload, f, ensure_ascii=False, indent=2)

        remote_cfg = meta["config_remote_path"]
        remote_dir = os.path.dirname(remote_cfg).replace("\\", "/")
        self.run_adb(["shell", "mkdir", "-p", remote_dir])

        push_res = self.run_adb(["push", str(temp_cfg), remote_cfg])
        if push_res["ok"]:
            self.run_adb(["shell", "am", "force-stop", meta["package"]])
            self.run_adb(["shell", "am", "start", "-n", f"{meta['package']}/{meta['main_activity']}"])
            return {"ok": True}
        return {"ok": False, "error": push_res["stderr"]}

    def setup_tv_web_remote(self, enable: bool = True) -> Dict[str, Any]:
        """Устанавливает или отключает автономный веб-пульт прямо на ТВ и добавляет круглую кнопку в CleanYourTV."""
        if not self.current_device:
            return {"ok": False, "error": "Телевизор не подключен к ADB."}

        ip_only = self.current_device.split(":")[0]
        remote_pkg = "com.zhouwj.tvinstaller"

        def update_cleanyourtv_topbar(add_pkg: bool):
            try:
                cfg_remote = "/sdcard/Android/data/com.gathin.tvhome/files/config.json"
                tmp_cfg = self.backups_dir / "clean_config_tmp.json"
                res = self.run_adb(["pull", cfg_remote, str(tmp_cfg)])
                if res.get("ok", False) and tmp_cfg.exists():
                    with open(tmp_cfg, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    top_apps = cfg.get("top_bar_apps", [])
                    changed = False
                    if add_pkg and remote_pkg not in top_apps:
                        top_apps.append(remote_pkg)
                        cfg["top_bar_apps"] = top_apps
                        changed = True
                    elif not add_pkg and remote_pkg in top_apps:
                        top_apps = [p for p in top_apps if p != remote_pkg]
                        cfg["top_bar_apps"] = top_apps
                        changed = True

                    if changed:
                        with open(tmp_cfg, "w", encoding="utf-8") as f:
                            json.dump(cfg, f, indent=4)
                        self.run_adb(["push", str(tmp_cfg), cfg_remote])
                        self.run_adb(["shell", "am", "force-stop", "com.gathin.tvhome"])
                        self.run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"])
            except Exception as e:
                print(f"[TVWebRemote] top bar update error: {e}")

        if not enable:
            self.run_adb(["shell", "pkill", "-f", "busybox.*httpd"])
            self.run_adb(["shell", "rm", "-rf", "/data/local/tmp/web_remote"])
            update_cleanyourtv_topbar(add_pkg=False)
            return {"ok": True, "enabled": False, "msg": "Веб-пульт остановлен, круглая кнопка удалена из панели ТВ."}

        local_remote_dir = self.base_dir / "web_remote"
        if not local_remote_dir.exists():
            for d in [self.exe_dir / "web_remote", self.meipass_dir / "web_remote"]:
                if d.exists():
                    local_remote_dir = d
                    break
        if not local_remote_dir.exists():
            return {"ok": False, "error": "Папка web_remote не найдена."}

        self.run_adb(["shell", "mkdir", "-p", "/data/local/tmp/web_remote/cgi-bin"])
        self.run_adb(["push", str(local_remote_dir / "index.html"), "/data/local/tmp/web_remote/index.html"])

        cgi_dir = local_remote_dir / "cgi-bin"
        if cgi_dir.exists():
            for cgi_file in cgi_dir.iterdir():
                if cgi_file.is_file():
                    self.run_adb(["push", str(cgi_file), f"/data/local/tmp/web_remote/cgi-bin/{cgi_file.name}"])

        self.run_adb(["shell", "chmod", "-R", "755", "/data/local/tmp/web_remote"])
        self.run_adb(["shell", "pkill", "-f", "busybox.*httpd"])
        self.run_adb(["shell", "busybox", "httpd", "-p", "8080", "-h", "/data/local/tmp/web_remote"])

        apk_path = self.resolve_apk("apps/TVWebRemote.apk")
        if not apk_path:
            apk_path = self.resolve_apk("apps/media/TVWebRemote.apk")

        pm_check = self.run_adb(["shell", "pm", "path", remote_pkg])
        if "package:" not in pm_check.get("stdout", "") and apk_path:
            self._notify("Установка TVWebRemote на ТВ...")
            self.run_adb(["install", "-r", str(apk_path)], timeout=60)

        update_cleanyourtv_topbar(add_pkg=True)

        url = f"http://{ip_only}:8080"
        qr_b64 = ""
        try:
            import qrcode, io, base64
            qr = qrcode.QRCode(box_size=6, border=2)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qr_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        except Exception:
            pass

        return {
            "ok": True,
            "enabled": True,
            "port": 8080,
            "url": url,
            "qr_base64": qr_b64,
            "msg": f"Веб-пульт активен! Круглая кнопка вызова QR-кода добавлена на ТВ: {url}"
        }

    def setup_smarttube_and_bypass(
        self,
        install_smarttube: bool = True,
        bypass_mode: str = "byedpi",
        byedpi_args: str = "--split 1+s --disorder 3 --ttl 5",
        custom_proxy_host: str = "127.0.0.1",
        custom_proxy_port: int = 1080,
        force_avc_codec: bool = True,
    ) -> Dict[str, Any]:
        """Установка и тонкая настройка SmartTube + обхода замедлений YouTube."""
        steps_log = []
        smarttube_pkg = "com.liskovsoft.smarttubetv.beta"

        if install_smarttube:
            self._notify("[YouTube] Подготовка SmartTube...")
            st_apk = self.resolve_apk("apps/youtube/SmartTube_stable.apk")
            if st_apk and self.is_valid_apk(st_apk):
                self._notify(f"[YouTube] Установка {st_apk.name} на ТВ...")
                res = self.run_adb(["install", "-r", str(st_apk)], timeout=90)
                steps_log.append({"step": "install_smarttube", "ok": res["ok"]})
            else:
                steps_log.append({"step": "install_smarttube", "ok": False, "error": "SmartTube APK не найден"})

        if bypass_mode == "byedpi":
            self._notify("[ByeDPI] Подготовка ByeDPI...")
            byedpi_apk = self.resolve_apk("apps/youtube/ByeDPI_tv.apk")
            if byedpi_apk and self.is_valid_apk(byedpi_apk):
                self._notify(f"[ByeDPI] Установка {byedpi_apk.name} на ТВ...")
                self.run_adb(["install", "-r", str(byedpi_apk)], timeout=60)

            cfg_dir = "/sdcard/Android/data/io.github.dovecoteescapee.byedpi/files"
            self.run_adb(["shell", "mkdir", "-p", cfg_dir])
            self.run_adb(["shell", f"echo '{byedpi_args}' > {cfg_dir}/byedpi_cmd.txt"])
            custom_proxy_host = "127.0.0.1"
            custom_proxy_port = 1080
            steps_log.append({"step": "configure_byedpi", "args": byedpi_args, "ok": True})
        elif bypass_mode == "dns_only":
            self.run_adb(["shell", "settings", "put", "global", "private_dns_mode", "hostname"])
            self.run_adb(["shell", "settings", "put", "global", "private_dns_specifier", "dns.adguard-dns.com"])
            steps_log.append({"step": "configure_private_dns", "dns": "dns.adguard-dns.com", "ok": True})

        if bypass_mode in ("byedpi", "custom_proxy") or force_avc_codec:
            st_prefs_dir = f"/sdcard/Android/data/{smarttube_pkg}/files/smarttube_preset"
            self.run_adb(["shell", "mkdir", "-p", st_prefs_dir])

            preset_data = {
                "proxy_enabled": bypass_mode in ("byedpi", "custom_proxy"),
                "proxy_type": "SOCKS5",
                "proxy_host": custom_proxy_host,
                "proxy_port": custom_proxy_port,
                "preferred_codec": "avc" if force_avc_codec else "vp9",
                "video_buffer_size": "high",
                "sponsor_block_enabled": True,
            }
            local_preset = self.backups_dir / "smarttube_preset.json"
            with open(local_preset, "w", encoding="utf-8") as f:
                json.dump(preset_data, f, indent=2)

            self.run_adb(["push", str(local_preset), f"{st_prefs_dir}/config.json"])
            steps_log.append({"step": "inject_smarttube_prefs", "preset": preset_data, "ok": True})

        return {"ok": True, "steps": steps_log}

    def install_batch_apps(self, app_keys: List[str]) -> Dict[str, Any]:
        """Пакетная установка медиа-приложений из каталога."""
        installed, errors = [], []
        apps_map = {
            "lampa": "apps/media/Lampa.apk",
            "zona": "apps/media/Zona.apk",
            "hdrezka": "apps/media/HDRezka.apk",
            "filemanager": "apps/media/FileManagerPlus.apk",
            "happ": "apps/media/Happ.apk",
            "spotify": "apps/media/SpotifyTV.apk",
            "smarttube": "apps/youtube/SmartTube_stable.apk",
            "byedpi": "apps/youtube/ByeDPI_tv.apk",
            "cleanyourtv": "apps/launchers/CleanYourTV.apk",
            "moytv": "apps/launchers/MoyTV.apk",
            "flauncher": "apps/launchers/FLauncher.apk",
        }

        total = len(app_keys)
        for idx, key in enumerate(app_keys, 1):
            rel_path = apps_map.get(key.lower())
            if not rel_path:
                errors.append({"app": key, "error": "Приложение не найдено в каталоге"})
                continue

            self._notify(f"[{idx}/{total}] Поиск APK: {key} ({Path(rel_path).name})...")
            apk = self.resolve_apk(rel_path)
            if apk and self.is_valid_apk(apk):
                self._notify(f"[{idx}/{total}] Установка {key} на ТВ...")
                res = self.run_adb(["install", "-r", str(apk)], timeout=120)
                out = (res.get("stdout", "") + " " + res.get("stderr", "")).strip()
                if res.get("ok") or "Success" in out:
                    installed.append(key)
                    self._notify(f"[{idx}/{total}] ✓ {key} успешно установлено!")
                else:
                    err_msg = res.get("stderr") or res.get("stdout") or "Ошибка установки"
                    errors.append({"app": key, "error": err_msg})
                    self._notify(f"[{idx}/{total}] ⚠ Ошибка установки {key}: {err_msg}")
            else:
                errors.append({"app": key, "error": "APK файл не найден и не удалось скачать"})
                self._notify(f"[{idx}/{total}] ⚠ Не удалось получить APK для {key}")

        return {"ok": True, "installed": installed, "errors": errors}

    def install_apk_file(self, apk_path: str) -> Dict[str, Any]:
        """Установка пользовательского APK файла на подключенный ТВ."""
        p = Path(apk_path)
        if not p.exists():
            return {"ok": False, "error": f"Файл не найден: {apk_path}"}
        res = self.run_adb(["install", "-r", str(p)], timeout=120)
        stdout = res.get("stdout", "")
        stderr = res.get("stderr", "")
        if "Success" in stdout or "Success" in stderr or res.get("ok", False):
            return {"ok": True, "msg": f"Приложение {p.name} успешно установлено на ТВ!"}
        return {"ok": False, "error": stderr or stdout or "Ошибка установки"}

    def run_raw_adb(self, cmd_str: str) -> Dict[str, Any]:
        """Выполнение произвольной команды в терминале ADB."""
        parts = cmd_str.strip().split()
        if not parts:
            return {"ok": False, "output": "Пустая команда"}
        res = self.run_adb(parts, timeout=15)
        out = (res["stdout"] + "\n" + res["stderr"]).strip()
        return {"ok": res["ok"], "output": out or "Команда выполнена (без вывода)"}

    def list_installed_third_party(self) -> List[Dict[str, str]]:
        """Возвращает список установленных пользовательских пакетов."""
        res = self.run_adb(["shell", "pm", "list", "packages", "-3"])
        if not res["ok"]:
            return []
        packages = []
        for line in res["stdout"].splitlines():
            pkg = line.replace("package:", "").strip()
            if pkg:
                packages.append({"package": pkg, "name": pkg.split(".")[-1].capitalize()})
        return packages

    def scan_network(self) -> List[str]:
        """
        Универсальный многоуровневый поиск ТВ:
        1. Проверка уже подключенных устройств в adb devices
        2. Последний успешно подключенный IP из кэша
        3. Сканирование ARP-таблицы (arp -a)
        4. mDNS-опрос YandexIO / Android TV на порту 5353
        5. Параллельное сканирование всех физических подсетей (192.168.x.x, 10.x.x.x, игнорируя VPN-шлюзы)
        """
        import concurrent.futures

        found = []
        candidates = []

        # 0. Проверяем кэш последнего IP
        cache_file = self.base_dir / "data" / "last_ip.txt"
        if cache_file.exists():
            try:
                last_ip = cache_file.read_text(encoding="utf-8").strip()
                if last_ip and last_ip not in candidates:
                    candidates.append(last_ip)
            except Exception:
                pass

        # 1. Проверяем adb devices
        try:
            res = self.run_adb(["devices"])
            for line in res.get("stdout", "").splitlines():
                if "\tdevice" in line:
                    parts = line.split("\t")[0].split(":")
                    ip = parts[0].strip()
                    if ip and ip.count(".") == 3 and ip not in found:
                        found.append(ip)
        except Exception:
            pass

        # 2. mDNS YandexIO
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
            sock.settimeout(0.6)
            sock.bind(("", 0))
            header = b"\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"
            q = b"\x09_yandexio\x04_tcp\x05local\x00\x00\x0c\x00\x01"
            sock.sendto(header + q, ("224.0.0.251", 5353))
            start_t = time.time()
            while time.time() - start_t < 0.8:
                try:
                    buf, addr = sock.recvfrom(2048)
                    if b"yandex" in buf.lower():
                        if addr[0] not in candidates:
                            candidates.append(addr[0])
                        break
                except socket.timeout:
                    break
            sock.close()
        except Exception:
            pass

        # 3. ARP-таблица (находит устройства даже при включенном VPN!)
        try:
            arp_out = subprocess.check_output("arp -a", shell=True).decode("cp866", errors="ignore")
            for line in arp_out.splitlines():
                parts = line.strip().split()
                if len(parts) >= 2 and parts[0].count(".") == 3:
                    ip = parts[0].strip()
                    if not (ip.startswith(("224.", "239.", "127.", "0.")) or ip.endswith(".255")):
                        if ip not in candidates:
                            candidates.append(ip)
        except Exception:
            pass

        # 4. Обнаружение реальных локальных подсетей (игнорируя VPN)
        subnets = set()
        try:
            host_ips = [item[4][0] for item in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)]
            for hip in sorted(host_ips, key=lambda x: (not x.startswith("192.168."), x)):
                if hip.startswith(("192.168.", "10.", "172.")) and not hip.startswith("10.8."):
                    subnets.add(".".join(hip.split(".")[:3]))
        except Exception:
            pass

        for sub in subnets:
            for i in range(2, 255):
                ip = f"{sub}.{i}"
                if ip not in candidates:
                    candidates.append(ip)

        # 5. Быстрая параллельная проверка порта 5555
        def check_port(target_ip: str) -> Optional[str]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.35)
                code = s.connect_ex((target_ip, 5555))
                s.close()
                if code == 0:
                    return target_ip
            except Exception:
                pass
            return None

        # Проверяем кандидаты через пул потоков
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(check_port, ip) for ip in candidates[:150]]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res and res not in found:
                    found.append(res)

        return found


# Backwards compatibility aliases for CLI/Tkinter scripts
_default_mgr = SmartTVManager()
ADB = _default_mgr.adb_bin
APPS_DIR = str(_default_mgr.base_dir / 'apps')
PRESETS = _default_mgr.packages_db.get('profiles', {})
