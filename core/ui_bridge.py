# -*- coding: utf-8 -*-
"""
core.ui_bridge
Генерация JSON/HTML данных для интерфейса, пресеты CleanYourTV и диагностика.
"""
import os
import sys
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

CLEANYOURTV_PRESETS = {

    "default": {

        "id": "default",

        "name": "Стандартная (Apple TV)",

        "badge": "tvOS Классика",

        "desc": "Сбалансированный стиль Apple TV с кинематографической верхней полкой, доком любимых приложений и мягким свечением.",

        "config": {

            "columns": 5,

            "rows_below_dock": 1,

            "dock_apps": [

                "mobi.zona",

                "com.lampa.tv",

                "ru.rezka.app",

                "com.google.android.youtube.tv",

                "ru.kinopoisk.tv",

                "com.vk.vkvideo"

            ],

            "fill_dock": True,

            "cinematic_home": True,

            "cinematic_dots": True,

            "cinematic_white_focus": False,

            "cinematic_art": 60,

            "cinematic_scrim": 80,

            "dock_glass": True,

            "dock_opacity": 85,

            "dock_even_padding": True,

            "glass_style": "glass",

            "ambient_glow": True,

            "app_glow": True,

            "show_network_pill": True,

            "show_inputs_pill": True,

            "icon_only_buttons": True,

            "icon_only_inputs": True,

            "show_greeting": True,

            "greeting_name": "Семья",

            "always_show_names": False,

            "reduced_motion": False,

            "wifi_status_color": True,

            "wifi_status_warnings": True,

            "home_idle_clock_minutes": 5,

            "clock_wallpaper": True,

            "clock_glow": True,

            "show_stats": False

        }

    },

    "aurora": {

        "id": "aurora",

        "name": "Aurora (Северное сияние)",

        "badge": "Премиум градиент",

        "desc": "Глубокий бирюзово-фиолетовый градиент, свечение Horizon, подсветка Halo и 6 колонок сетки.",

        "config": {

            "columns": 6,

            "rows_below_dock": 0,

            "dock_apps": [

                "mobi.zona",

                "com.lampa.tv",

                "ru.rezka.app",

                "com.google.android.youtube.tv",

                "ru.kinopoisk.tv",

                "com.vk.vkvideo"

            ],

            "fill_dock": True,

            "background_color": "#0a192f",

            "accent_color": "#64ffda",

            "glass_style": "halo",

            "glow_style": "horizon",

            "dock_glass": True,

            "dock_opacity": 70,

            "ambient_glow": True,

            "app_glow": True,

            "cinematic_home": True,

            "cinematic_dots": True,

            "show_network_pill": True,

            "icon_only_buttons": True,

            "icon_only_inputs": True,

            "show_greeting": True,

            "greeting_name": "Гостиная",

            "home_idle_clock_minutes": 10,

            "show_stats": True

        }

    },

    "night": {

        "id": "night",

        "name": "Night Dark (Для OLED)",

        "badge": "OLED Кинозал",

        "desc": "Абсолютно чёрный фон для глубокого контраста OLED, тонкая кромка Rim, часы без свечения и максимальная плавность.",

        "config": {

            "columns": 5,

            "rows_below_dock": 1,

            "dock_apps": [

                "mobi.zona",

                "com.lampa.tv",

                "ru.rezka.app",

                "com.google.android.youtube.tv",

                "ru.kinopoisk.tv"

            ],

            "fill_dock": True,

            "background_color": "#000000",

            "wallpaper": False,

            "glass_style": "rim",

            "dock_glass": False,

            "dock_opacity": 100,

            "ambient_glow": False,

            "app_glow": True,

            "clock_glow": False,

            "icon_only_buttons": True,

            "icon_only_inputs": True,

            "show_network_pill": True,

            "show_inputs_pill": True,

            "reduced_motion": True,

            "home_idle_clock_minutes": 3,

            "show_stats": False

        }

    },

    "minimal": {

        "id": "minimal",

        "name": "Minimalist (Ультрачистый)",

        "badge": "1 ГБ ОЗУ",

        "desc": "Один горизонтальный ряд любимых приложений без нижней сетки. Мгновенный отклик даже на слабых процессорах.",

        "config": {

            "columns": 4,

            "rows_below_dock": 0,

            "single_row": True,

            "dock_row": True,

            "dock_band_all": True,

            "dock_glass": True,

            "dock_opacity": 90,

            "show_greeting": False,

            "always_show_names": False,

            "show_network_pill": True,

            "icon_only_buttons": True,

            "icon_only_inputs": True,

            "reduced_motion": True,

            "animations": True

        }

    }

}


CLEANYOURTV_KEYS_SCHEMA = [

    # dock

    {"key": "columns", "title": "Плиток в одном ряду (сетка)", "desc": "Количество колонок сетки приложений (от 1 до 8). Начиная с 5 плитки пропорционально уменьшаются.", "category": "dock", "type": "int", "min": 1, "max": 8, "default": 5},

    {"key": "rows_below_dock", "title": "Рядов под любимыми приложениями", "desc": "Сколько рядов сетки видно под основным доком (0-3). 0 скрывает нижнюю сетку до скролла вниз.", "category": "dock", "type": "int", "min": 0, "max": 3, "default": 1},

    {"key": "fill_dock", "title": "Автозаполнение свободных мест дока", "desc": "Заполнять свободные места дока первыми приложениями из сетки. При «Нет» оставляет свободные места пустыми.", "category": "dock", "type": "bool", "default": True},

    {"key": "dock_title", "title": "Крупный заголовок над доком", "desc": "Показывать название приложения в фокусе крупным шрифтом над доком. При «Нет» остаётся только подсветка.", "category": "dock", "type": "bool", "default": True},

    {"key": "dock_row", "title": "Док отдельным рядом с подложкой", "desc": "Отображает верхний ряд в виде стеклянной полки tvOS. При «Нет» объединяет все плитки в единую сетку.", "category": "dock", "type": "bool", "default": True},

    {"key": "dock_glass", "title": "Подложка из светлого матового стекла", "desc": "Подложка дока из полупрозрачного матового стекла в стиле кнопок верхней панели.", "category": "dock", "type": "bool", "default": True},

    {"key": "dock_opacity", "title": "Непрозрачность подложки дока (%)", "desc": "Процент непрозрачности полки дока от 30% (полупрозрачное стекло) до 100% (сплошная плашка).", "category": "dock", "type": "int", "min": 30, "max": 100, "default": 85},

    {"key": "dock_even_padding", "title": "Равномерные отступы подложки дока", "desc": "Отступы со всех четырёх сторон полки равны промежутку между плитками.", "category": "dock", "type": "bool", "default": False},

    {"key": "single_row", "title": "Один ряд с горизонтальной прокруткой", "desc": "Все приложения размещаются в одном ряду дока с горизонтальной прокруткой без нижней сетки.", "category": "dock", "type": "bool", "default": False},

    {"key": "dock_band_all", "title": "Сплошная лента подложки для всего ряда", "desc": "При single_row подложка дока тянется за всеми приложениями ряда при прокрутке.", "category": "dock", "type": "bool", "default": False},

    {"key": "uniform_tiles", "title": "Карточки приложений в едином стиле", "desc": "Каждая плитка рисуется как лаконичный значок на цветной карточке вместо тяжелых баннеров.", "category": "dock", "type": "bool", "default": False},

    {"key": "always_show_names", "title": "Всегда показывать названия плиток", "desc": "Подписи приложений видны под всеми плитками одновременно (приглушённо до наведения).", "category": "dock", "type": "bool", "default": False},

    {"key": "app_library", "title": "Кнопка «Библиотека приложений»", "desc": "Добавляет кнопку со всеми установленными приложениями после последнего ряда главного экрана.", "category": "dock", "type": "bool", "default": False},

    {"key": "library_button", "title": "Круглая кнопка библиотеки в шапке", "desc": "Круглая кнопка быстрого перехода в библиотеку приложений в верхней панели рядом с настройками.", "category": "dock", "type": "bool", "default": False},



    # cinematic

    {"key": "cinematic_home", "title": "Кинематографическая верхняя полка tvOS", "desc": "Полноэкранная кинематографическая полка: постер и цвет приложения в фокусе заполняют верх экрана.", "category": "cinematic", "type": "bool", "default": True},

    {"key": "cinematic_dots", "title": "Индикатор-точки позиции в доке", "desc": "Показывать точки пагинации под названием приложения в доке.", "category": "cinematic", "type": "bool", "default": True},

    {"key": "cinematic_white_focus", "title": "Белая подсветка фокуса в полке", "desc": "Подсветка активной плитки остаётся белой вместо адаптации под цвет приложения.", "category": "cinematic", "type": "bool", "default": False},

    {"key": "cinematic_art", "title": "Непрозрачность постера на полке (%)", "desc": "Интенсивность фонового постера приложения в кинематографическом режиме (0-100%).", "category": "cinematic", "type": "int", "min": 0, "max": 100, "default": 60},

    {"key": "cinematic_scrim", "title": "Сила затемнения под текстом полки (%)", "desc": "Степень затемнения за названием для идеальной читаемости текста (0-100%).", "category": "cinematic", "type": "int", "min": 0, "max": 100, "default": 80},



    # visuals

    {"key": "glass_style", "title": "Стиль стекла и подсветки фокуса", "desc": "Вид подсветки активного элемента: glass (стекло с бликом), rim (чёткая кромка), halo (мягкое сияние).", "category": "visuals", "type": "select", "options": ["glass", "rim", "halo"], "default": "glass"},

    {"key": "glow_style", "title": "Форма свечения за приложением", "desc": "Геометрия светового пятна: radial (радиальное круговое) или horizon (стекающий сверху градиент).", "category": "visuals", "type": "select", "options": ["radial", "horizon"], "default": "radial"},

    {"key": "ambient_glow", "title": "Фоновое свечение в цвете приложения", "desc": "Атмосферное рассеянное свечение за доком в основном цвете выбранного приложения.", "category": "visuals", "type": "bool", "default": True},

    {"key": "app_glow", "title": "Индивидуальная подсветка каждой плитки", "desc": "Подсветка фокуса окрашивается в индивидуальный брендовый цвет приложения.", "category": "visuals", "type": "bool", "default": True},

    {"key": "background_color", "title": "Цвет фона экрана (HEX)", "desc": "Базовый цвет подложки всего экрана (по умолчанию глубокий черный #000000).", "category": "visuals", "type": "color", "default": "#000000"},

    {"key": "accent_color", "title": "Пользовательский цвет акцента (HEX)", "desc": "Цвет свечения и кнопок интерфейса при включении кастомной цветовой гаммы.", "category": "visuals", "type": "color", "default": "#38bdf8"},

    {"key": "wallpaper", "title": "Отображение обоев", "desc": "Показывать загруженные фото-обои (wallpaper.jpg). При выключении используется background_color.", "category": "visuals", "type": "bool", "default": True},

    {"key": "wallpaper_rotation_minutes", "title": "Автосмена обоев (интервал в минутах)", "desc": "Периодичность автосмены картинок из папки wallpapers/ на ТВ (0 — зафиксировать одни обои).", "category": "visuals", "type": "int", "min": 0, "max": 1440, "default": 0},

    {"key": "wallpaper_order", "title": "Порядок смены обоев", "desc": "shuffle — случайный порядок без повторов; sequential — по алфавиту имен файлов.", "category": "visuals", "type": "select", "options": ["shuffle", "sequential"], "default": "shuffle"},

    {"key": "wallpaper_dim", "title": "Затемнение обоев (%)", "desc": "Степень затемнения фонового фото от 0% до 90% для повышенного контраста иконок.", "category": "visuals", "type": "int", "min": 0, "max": 90, "default": 0},

    {"key": "wallpaper_true_color", "title": "32-битная глубина цвета обоев", "desc": "Декодировать обои в ARGB_8888 вместо RGB_565 (убирает полосы градиентов на тёмном небе).", "category": "visuals", "type": "bool", "default": False},

    {"key": "sky_intensity", "title": "Градиент времени суток Sky Intensity (%)", "desc": "Динамический градиент неба, меняющий оттенок в зависимости от часа суток (0% — выкл).", "category": "visuals", "type": "int", "min": 0, "max": 100, "default": 0},

    {"key": "reduced_motion", "title": "Меньше анимаций (для слабых ТВ)", "desc": "Оптимизация под бюджетные телевизоры: фокус скользит мгновенно (<90 мс) без задержек.", "category": "visuals", "type": "bool", "default": False},

    {"key": "animations", "title": "Базовые системные анимации", "desc": "Анимации фокуса, стекла и плавного появления плиток при старте.", "category": "visuals", "type": "bool", "default": True},

    {"key": "advanced_effects", "title": "Дополнительные 3D-эффекты", "desc": "Приподнятая плитка в фокусе, увеличение значка и плавный фоновый цвет.", "category": "visuals", "type": "bool", "default": False},

    {"key": "focus_overshoot", "title": "Эффект отскока фокуса (Overshoot)", "desc": "Плитка слегка пружинит при переходе фокуса, создавая фирменное ощущение tvOS.", "category": "visuals", "type": "bool", "default": True},

    {"key": "fade_rows", "title": "Плавное растворение рядов под часы", "desc": "Ряды плиток при скролле вверх плавно растворяются под часами вместо резкой обрезки.", "category": "visuals", "type": "bool", "default": False},



    # topbar

    {"key": "show_network_pill", "title": "Кнопка Сеть (Wi-Fi / LAN)", "desc": "Отображать круглую кнопку статуса сети в правом верхнем углу шапки.", "category": "topbar", "type": "bool", "default": True},

    {"key": "icon_only_buttons", "title": "Только круглые иконки в шапке (Apple Style)", "desc": "Кнопки Сети и Настроек отображаются в виде компактных круглых значков без подписей.", "category": "topbar", "type": "bool", "default": True},

    {"key": "show_inputs_pill", "title": "Кнопка «Входы» (HDMI)", "desc": "Кнопка быстрого меню физических ТВ-входов (HDMI 1, 2, AV) в правом верхнем углу.", "category": "topbar", "type": "bool", "default": True},

    {"key": "icon_only_inputs", "title": "Иконка входов без текста", "desc": "Отображать кнопку «Входы» в виде круглой иконки со штекером HDMI без текста.", "category": "topbar", "type": "bool", "default": True},

    {"key": "top_menu", "title": "Единая шестерёнка меню по центру", "desc": "Объединяет «Входы», Сеть и Настройки в одну центральную круглую кнопку-шестерёнку.", "category": "topbar", "type": "bool", "default": False},

    {"key": "reorder_button", "title": "Кнопка перестановки плиток в шапке", "desc": "Добавляет кнопку быстрого режима сортировки иконок прямо в верхнюю панель.", "category": "topbar", "type": "bool", "default": False},

    {"key": "wifi_status_color", "title": "Цветной индикатор статуса Wi-Fi", "desc": "Значок сети светится зелёным при активном соединении и белым при отсутствии сети.", "category": "topbar", "type": "bool", "default": True},

    {"key": "wifi_status_warnings", "title": "Предупреждения о проблемах сети", "desc": "Оранжевый цвет значка при подключении без интернета, красный — при обрыве связи.", "category": "topbar", "type": "bool", "default": True},

    {"key": "wifi_label_width", "title": "Ширина имени сети Wi-Fi (dp)", "desc": "Ограничение ширины текстового названия Wi-Fi сети (0 оставляет только значок).", "category": "topbar", "type": "int", "min": 0, "max": 300, "default": 0},

    {"key": "vpn_app", "title": "Круглая кнопка VPN в шапке", "desc": "Имя пакета VPN-клиента (su.happ.proxyutility, com.wireguard.android) для быстрого запуска из шапки.", "category": "topbar", "type": "string", "default": "su.happ.proxyutility"},



    # clock

    {"key": "show_greeting", "title": "Приветствие над часами", "desc": "Показывать фразу приветствия над часами в зависимости от времени суток.", "category": "clock", "type": "bool", "default": True},

    {"key": "greeting_name", "title": "Имя в приветствии", "desc": "Имя владельца или комнаты (например, «Семья», «Зал», «Спальня»).", "category": "clock", "type": "string", "default": "Семья"},

    {"key": "header_white", "title": "Ярко-белый шрифт даты", "desc": "Дата и разделитель окрашены в яркий белый цвет часов вместо приглушённого.", "category": "clock", "type": "bool", "default": False},

    {"key": "show_stats", "title": "Строка системной статистики под часами", "desc": "Выводить индикаторы текущей загрузки CPU %, свободной памяти ОЗУ и диска под часами.", "category": "clock", "type": "bool", "default": False},

    {"key": "home_idle_clock_minutes", "title": "Заставка с часами при простое (минут)", "desc": "Через сколько минут неактивности включаются плавающие часы (0 — выключить заставку).", "category": "clock", "type": "int", "min": 0, "max": 1440, "default": 5},

    {"key": "clock_wallpaper", "title": "Часы-заставка поверх обоев", "desc": "Плавающие часы заставки отображаются поверх размытых обоев вместо чёрного фона.", "category": "clock", "type": "bool", "default": True},

    {"key": "clock_wallpaper_dim", "title": "Затемнение обоев под заставкой (%)", "desc": "Сила затемнения фото-обоев во время экранной заставки с часами (0-90%).", "category": "clock", "type": "int", "min": 0, "max": 90, "default": 50},

    {"key": "clock_glow", "title": "Цветное свечение часов", "desc": "Мягкое свечение часов (выключите для идеального чёрного фона на OLED телевизорах).", "category": "clock", "type": "bool", "default": True},



    # hardware

    {"key": "boot_to_live_tv", "title": "Запуск эфирного ТВ при включении", "desc": "Сразу при включении телевизора открывает эфирные каналы (live_tv_package).", "category": "hardware", "type": "bool", "default": False},

    {"key": "live_tv_package", "title": "Пакет приложения эфирного ТВ", "desc": "Имя системного пакета эфирного тюнера (например, com.tcl.tv, com.haier.tv.input).", "category": "hardware", "type": "string", "default": ""},

    {"key": "settings_key_panel", "title": "Панель быстрых настроек вместо настроек ТВ", "desc": "Кнопка «Настройки» открывает компактное полупрозрачное меню быстрых параметров.", "category": "hardware", "type": "bool", "default": False},

    {"key": "consume_volume_keys", "title": "Устранение двойного шага громкости", "desc": "Исправляет баг прошивок TCL/Haier, когда нажатие меняло громкость сразу на 2 деления.", "category": "hardware", "type": "bool", "default": False},

    {"key": "tile_menu", "title": "Контекстное меню при удержании OK", "desc": "Долгое нажатие OK на плитке открывает меню: «Переместить», «Убрать» и «О приложении».", "category": "hardware", "type": "bool", "default": True}

]


class UIBridgeMixin:
    def _resolve_file(self, rel_path: str) -> Path:

        for root in [self.exe_dir, self.meipass_dir, self.base_dir]:

            p = root / rel_path

            if p.exists():

                return p

        return self.base_dir / rel_path


    @staticmethod

    def _load_json(path: Path) -> Dict[str, Any]:

        if path.exists():

            with open(path, "r", encoding="utf-8") as f:

                return json.load(f)

        return {}


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


    def get_cleanyourtv_config(self) -> Dict[str, Any]:

        """Считывает config.json лаунчера CleanYourTV с телевизора или возвращает дефолтный пресет."""

        remote_cfg = "/sdcard/Android/data/com.gathin.tvhome/files/config.json"

        local_tmp = self.backups_dir / "cleanyourtv_current.json"

        from_tv = False

        loaded_cfg = None



        if not self.current_device:

            last_ip = self._get_last_known_ip()

            if last_ip:

                self.connect_tv(last_ip)



        if self.current_device:

            pull_res = self.run_adb(["pull", remote_cfg, str(local_tmp)], timeout=10)

            if pull_res.get("ok") and local_tmp.exists() and local_tmp.stat().st_size > 5:

                try:

                    with open(local_tmp, "r", encoding="utf-8") as f:

                        loaded_cfg = json.load(f)

                    from_tv = True

                except Exception:

                    loaded_cfg = None



        if not loaded_cfg:

            loaded_cfg = dict(CLEANYOURTV_PRESETS["default"]["config"])



        # Determine granular button placement from TV config

        wifi_active = loaded_cfg.get("show_network_pill", True)

        reorder_active = loaded_cfg.get("reorder_button", True)

        inputs_active = loaded_cfg.get("show_inputs_pill", False)

        inputs_menu = loaded_cfg.get("show_inputs_menu_row", False)

        library_active = loaded_cfg.get("library_button", False)



        loaded_cfg["wifi_location"] = "top" if wifi_active else "menu"

        loaded_cfg["reorder_location"] = "top" if reorder_active else "menu"

        if inputs_active:

            loaded_cfg["inputs_location"] = "top"

        elif inputs_menu:

            loaded_cfg["inputs_location"] = "menu"

        else:

            loaded_cfg["inputs_location"] = "hide"

        loaded_cfg["library_location"] = "top" if library_active else "hide"



        return {

            "ok": True,

            "config": loaded_cfg,

            "presets": CLEANYOURTV_PRESETS,

            "schema": CLEANYOURTV_KEYS_SCHEMA,

            "from_tv": from_tv

        }


    def save_cleanyourtv_config(self, config_payload: Dict[str, Any], restart_home: bool = True) -> Dict[str, Any]:

        """Сохраняет измененную конфигурацию CleanYourTV на ТВ, пушит обои и перезапускает главный экран."""

        if not self.current_device:

            last_ip = self._get_last_known_ip()

            if last_ip:

                self.connect_tv(last_ip)

            else:

                return {"ok": False, "error": "Телевизор не подключен по ADB"}



        remote_dir = "/sdcard/Android/data/com.gathin.tvhome/files"

        remote_wp_dir = f"{remote_dir}/wallpapers"

        remote_cfg = f"{remote_dir}/config.json"

        local_cfg = self.backups_dir / "cleanyourtv_pushed.json"



        # 1. Clean payload and ensure dock_apps is a list of package strings

        clean_cfg = dict(config_payload)

        

        # Handle dock_apps

        dock_apps = clean_cfg.get("dock_apps", [])

        clean_dock_apps = []

        for app in dock_apps:

            if isinstance(app, dict):

                pkg = app.get("package") or app.get("pkg") or ""

                if pkg:

                    clean_dock_apps.append(pkg)

            elif isinstance(app, str) and app:

                clean_dock_apps.append(app)

        clean_dock_apps = [p for p in clean_dock_apps if p]

        if clean_dock_apps:

            clean_cfg["dock_apps"] = clean_dock_apps



        # 2. Handle Wallpaper & Themes

        wp_choice = clean_cfg.get("wallpaper_choice")

        wp_path = clean_cfg.get("wallpaper_path", "")

        theme_key = clean_cfg.get("theme_key", "")

        

        # OLED is ONLY black if explicitly requested

        is_oled_black = (

            theme_key == "oled_guard" or 

            "oled_carbon" in str(wp_path) or

            "oled_carbon" in str(wp_choice)

        )

        

        import time as _t

        clean_cfg["theme_revision"] = int(_t.time())

        self.run_adb(["shell", "mkdir", "-p", remote_wp_dir])



        if is_oled_black:

            clean_cfg["wallpaper"] = False

            clean_cfg["wallpaper_choice"] = "none"

            clean_cfg["oled_guard"] = True

            oled_file = self._resolve_file("wallpapers/oled_carbon.jpg")

            if oled_file.exists():

                self.run_adb(["push", str(oled_file), f"{remote_wp_dir}/01-dusk-peaks.jpg"], timeout=15)

                self.run_adb(["push", str(oled_file), f"{remote_dir}/wallpaper.jpg"], timeout=15)

        else:

            clean_cfg["wallpaper"] = True

            clean_cfg["oled_guard"] = False

            target_wp = None

            if wp_path:

                wp_basename = os.path.basename(wp_path)

                local_wp = self._resolve_file(f"wallpapers/{wp_basename}")

                if local_wp.exists():

                    target_wp = local_wp

                    clean_cfg["wallpaper_choice"] = wp_basename

            elif wp_choice and wp_choice != "none":

                local_wp = self._resolve_file(f"wallpapers/{wp_choice}")

                if local_wp.exists():

                    target_wp = local_wp

                    clean_cfg["wallpaper_choice"] = wp_choice



            if not target_wp or not target_wp.exists():

                target_wp = self._resolve_file("wallpapers/01-dusk-peaks.jpg")

                clean_cfg["wallpaper_choice"] = "01-dusk-peaks.jpg"



            if target_wp and target_wp.exists():

                self.run_adb(["push", str(target_wp), f"{remote_wp_dir}/01-dusk-peaks.jpg"], timeout=15)

                self.run_adb(["push", str(target_wp), f"{remote_dir}/wallpaper.jpg"], timeout=15)

                if clean_cfg.get("wallpaper_choice"):

                    self.run_adb(["push", str(target_wp), f"{remote_wp_dir}/{clean_cfg['wallpaper_choice']}"], timeout=15)



        # Handle rows and grid layout

        if "rows_below_dock" in clean_cfg:

            try:

                clean_cfg["rows_below_dock"] = int(clean_cfg["rows_below_dock"])

                clean_cfg["single_row"] = (clean_cfg["rows_below_dock"] == 0)

            except:

                pass

        if "columns" in clean_cfg:

            try:

                clean_cfg["columns"] = int(clean_cfg["columns"])

            except:

                pass

        if "fade_rows" in clean_cfg:

            clean_cfg["fade_rows"] = bool(clean_cfg["fade_rows"])

        if "cinematic_dots" in clean_cfg:

            clean_cfg["cinematic_dots"] = bool(clean_cfg["cinematic_dots"])



        # 3. Top Buttons & Title mapping

        if "dock_title" in clean_cfg:

            clean_cfg["dock_title"] = bool(clean_cfg.get("dock_title"))

        if "icon_only_buttons" in clean_cfg:

            clean_cfg["icon_only_buttons"] = bool(clean_cfg.get("icon_only_buttons"))

            clean_cfg["icon_only_inputs"] = bool(clean_cfg.get("icon_only_buttons"))

            if clean_cfg["icon_only_buttons"]:

                clean_cfg["wifi_label_width"] = 0

        # Granular button locations: 'top' (circle on screen), 'menu' (collapsed in gear), 'hide' (disabled)

        wifi_loc = clean_cfg.get("wifi_location")

        reorder_loc = clean_cfg.get("reorder_location")

        inputs_loc = clean_cfg.get("inputs_location")

        library_loc = clean_cfg.get("library_location")



        # Fallback to boolean flags if locations not explicitly passed

        if wifi_loc is None:

            wifi_loc = "top" if clean_cfg.get("show_network", True) else "menu"

        if reorder_loc is None:

            reorder_loc = "top" if clean_cfg.get("show_reorder", True) else "menu"

        if inputs_loc is None:

            inputs_loc = "top" if clean_cfg.get("show_inputs", False) else "hide"

        if library_loc is None:

            library_loc = "top" if clean_cfg.get("show_library", False) else "hide"



        # Apply exact CleanYourTV flags

        clean_cfg["show_network_pill"] = (wifi_loc == "top")

        clean_cfg["reorder_button"] = (reorder_loc == "top")



        # Inputs (HDMI/AV) in CleanYourTV is enabled via show_inputs_pill.
        # When show_inputs_pill is True, CleanYourTV displays "Источники" inside the glassPopup menu.
        if inputs_loc in ("top", "menu"):
            clean_cfg["show_inputs_pill"] = True
            clean_cfg["show_inputs_menu_row"] = True
        else: # hide
            clean_cfg["show_inputs_pill"] = False
            clean_cfg["show_inputs_menu_row"] = False



        clean_cfg["library_button"] = (library_loc == "top")

        clean_cfg["show_library_pill"] = (library_loc == "top")

        clean_cfg["app_library"] = (library_loc == "top")



        if "show_settings" in clean_cfg:

            clean_cfg["launcher_settings_button"] = bool(clean_cfg.get("show_settings"))

        if "show_home_settings" in clean_cfg:

            clean_cfg["show_home_settings_shortcut"] = bool(clean_cfg.get("show_home_settings"))



        # settings_key_panel must ALWAYS be True so clicking the gear opens the flyout menu

        clean_cfg["settings_key_panel"] = True



        # User requirement:

        # "если я что то прячу в шестеренку то в шестеренке появляется пункт системные настройки,

        # А ШЕСТЕРЕНКА НА ЭКРАНЕ ОТКРЫВАЕТ СПИСОК! Если выбрать вывести всё то шестеренка становится вызовом системных настроек."

        has_collapsed_items = (

            wifi_loc == "menu" or 

            reorder_loc == "menu" or 

            inputs_loc == "menu" or 

            library_loc == "menu"

        )

        clean_cfg["top_menu"] = True

        clean_cfg["show_home_settings_shortcut"] = True



        # VPN Button in Top Bar handling

        vpn_choice = clean_cfg.get("vpn_choice", "su.happ.proxyutility")

        show_vpn = bool(clean_cfg.get("show_vpn_button", False))

        top_apps = list(clean_cfg.get("top_bar_apps", []))

        known_vpn_pkgs = ["su.happ.proxyutility", "com.wireguard.android", "org.amnezia.vpn", "io.github.dovecoteescapee.byedpi", "org.lumic.byedpi"]

        top_apps = [p for p in top_apps if p not in known_vpn_pkgs]

        if show_vpn and vpn_choice:

            # Auto-check and install if missing

            chk = self.run_adb(["shell", "pm", "path", vpn_choice])

            if not chk.get("ok") or not chk.get("stdout"):

                self._notify(f"[CleanYourTV] VPN приложение {vpn_choice} не установлено на ТВ — запускаем авто-установку...")

                if "wireguard" in vpn_choice:

                    self.install_vpn_client("wireguard")

                elif "amnezia" in vpn_choice:

                    self.install_vpn_client("amnezia")

                elif "happ" in vpn_choice:

                    self.install_vpn_client("happ")

                elif "byedpi" in vpn_choice:

                    self.install_vpn_client("byedpi")

            top_apps.append(vpn_choice)

        # CRITICAL: CleanYourTV uses vpn_app as an override for the Wi-Fi icon click.

        # If vpn_app is non-empty, clicking Wi-Fi ("Сеть") opens the VPN app instead of Wi-Fi settings!

        # Therefore vpn_app MUST ALWAYS remain empty string. The VPN client is placed strictly in top_bar_apps.

        clean_cfg["vpn_app"] = ""

        clean_cfg["top_bar_apps"] = top_apps



        # 4. Save and push config.json

        try:

            with open(local_cfg, "w", encoding="utf-8") as f:

                json.dump(clean_cfg, f, ensure_ascii=False, indent=2)

        except Exception as e:

            return {"ok": False, "error": f"Ошибка сохранения JSON: {e}"}



        push_res = self.run_adb(["push", str(local_cfg), remote_cfg], timeout=15)

        if not push_res.get("ok"):

            return {"ok": False, "error": f"Ошибка отправки на ТВ: {push_res.get('stderr')}"}



        self.run_adb(["shell", "chmod", "666", remote_cfg])



        # 5. Restart Home Screen

        if restart_home:

            self._notify("[CleanYourTV] Перезапуск домашнего экрана для применения изменений...")

            self.run_adb(["shell", "am", "force-stop", "com.gathin.tvhome"], timeout=10)

            self.run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"], timeout=10)



        self._notify("[CleanYourTV] ✓ Конфигурация и обои успешно применены на ТВ!")

        return {"ok": True, "msg": "Конфигурация и обои успешно применены на ТВ!"}


    def reset_cleanyourtv_to_factory(self) -> Dict[str, Any]:

        """Полный сброс лаунчера CleanYourTV к заводским настройкам (pm clear + восстановление стандартных обоев)."""

        if not self.current_device:

            last_ip = self._get_last_known_ip()

            if last_ip:

                self.connect_tv(last_ip)

            else:

                return {"ok": False, "error": "Телевизор не подключен по ADB"}



        self._notify("[CleanYourTV] Полный сброс лаунчера к заводским настройкам...")

        self.run_adb(["shell", "pm", "clear", "com.gathin.tvhome"], timeout=10)

        

        remote_files = "/sdcard/Android/data/com.gathin.tvhome/files"

        self.run_adb(["shell", "mkdir", "-p", f"{remote_files}/wallpapers"])

        default_wp = self._resolve_file("wallpapers/01-dusk-peaks.jpg")

        if default_wp.exists():

            self.run_adb(["push", str(default_wp), f"{remote_files}/wallpapers/01-dusk-peaks.jpg"], timeout=15)

            self.run_adb(["push", str(default_wp), f"{remote_files}/wallpaper.jpg"], timeout=15)

        

        self.run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"], timeout=10)

        self._notify("[CleanYourTV] ✓ Лаунчер полностью сброшен к заводским настройкам!")

        return {"ok": True, "msg": "Лаунчер CleanYourTV сброшен к заводским настройкам"}


    def reset_cleanyourtv_config(self) -> Dict[str, Any]:

        """Сбрасывает конфигурацию CleanYourTV к заводским настройкам (удаляет кастомный config.json с ТВ)."""

        if not self.current_device:

            return {"ok": False, "error": "Телевизор не подключен по ADB"}



        remote_cfg = "/sdcard/Android/data/com.gathin.tvhome/files/config.json"

        self.run_adb(["shell", "rm", "-f", remote_cfg])

        self.run_adb(["shell", "am", "force-stop", "com.gathin.tvhome"], timeout=10)

        self.run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"], timeout=10)

        self._notify("[CleanYourTV] ✓ Настройки лаунчера сброшены к стандартным заводским!")

        return {"ok": True, "msg": "Настройки лаунчера сброшены!"}
