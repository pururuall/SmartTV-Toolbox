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
            self.save_known_device(
                ip=ip.strip(),
                port=port,
                brand=info.get("brand", ""),
                model=info.get("model", ""),
                android_ver=info.get("android_version", "")
            )
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
            "happ": "apps/Happ.apk",
            "spotify": "apps/media/SpotifyTV.apk",
            "smarttube": "apps/youtube/SmartTube_stable.apk",
            "byedpi": "apps/youtube/ByeDPI_tv.apk",
            "wireguard": "apps/wireguard.apk",
            "amnezia": "apps/amnezia.apk",
            "msx": "apps/Media+Station+X+v.0.1.160.apk",
            "num": "apps/NUM_1.0.150-release.apk",
            "webremote": "apps/TVWebRemote.apk",
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


    def _get_known_devices_file(self) -> Path:
        data_dir = self.exe_dir / "data"
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            data_dir = self.base_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / "known_devices.json"

    def get_known_devices(self) -> List[Dict[str, Any]]:
        f = self._get_known_devices_file()
        if f.exists():
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        return list(data.values())
            except Exception:
                pass
        return []

    def save_known_device(self, ip: str, port: int = 5555, brand: str = "", model: str = "", nickname: str = "", android_ver: str = ""):
        f = self._get_known_devices_file()
        devices_dict = {}
        if f.exists():
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    raw = json.load(fp)
                    if isinstance(raw, list):
                        for item in raw:
                            if isinstance(item, dict) and "ip" in item:
                                devices_dict[item["ip"]] = item
                    elif isinstance(raw, dict):
                        devices_dict = raw
            except Exception:
                devices_dict = {}

        existing = devices_dict.get(ip, {})
        dev_nickname = nickname or existing.get("nickname", "")
        dev_brand = brand or existing.get("brand", "")
        dev_model = model or existing.get("model", "")
        dev_ver = android_ver or existing.get("android_version", "")

        display_name = existing.get("name")
        if not display_name or display_name in ("Smart TV", "Smart TV (Android)"):
            if dev_brand and dev_model:
                display_name = f"{dev_brand} {dev_model}".strip()
            elif dev_brand:
                display_name = f"{dev_brand} Smart TV"
            elif dev_model:
                display_name = f"Smart TV {dev_model}"
            else:
                display_name = "Smart TV"

        devices_dict[ip] = {
            "ip": ip,
            "port": port,
            "brand": dev_brand,
            "model": dev_model,
            "name": display_name,
            "nickname": dev_nickname,
            "android_version": dev_ver,
            "last_connected": time.strftime("%Y-%m-%d %H:%M"),
            "is_active": (self.current_device == f"{ip}:{port}"),
            "status": "online"
        }

        try:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(devices_dict, fp, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def set_device_nickname(self, ip: str, nickname: str) -> bool:
        f = self._get_known_devices_file()
        devices_dict = {}
        if f.exists():
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    raw = json.load(fp)
                    if isinstance(raw, list):
                        for item in raw:
                            if isinstance(item, dict) and "ip" in item:
                                devices_dict[item["ip"]] = item
                    elif isinstance(raw, dict):
                        devices_dict = raw
            except Exception:
                devices_dict = {}

        if ip in devices_dict:
            devices_dict[ip]["nickname"] = nickname.strip()
            try:
                with open(f, "w", encoding="utf-8") as fp:
                    json.dump(devices_dict, fp, ensure_ascii=False, indent=2)
                return True
            except Exception:
                return False
        else:
            self.save_known_device(ip, nickname=nickname)
            return True

    def scan_network(self) -> List[Dict[str, Any]]:
        """
        Многоуровневый параллельный поиск всех Smart TV в локальной сети (порт 5555):
        1. Проверка уже подключенных устройств в adb devices
        2. Ранее сохраненные известные устройства (known_devices)
        3. Сканирование ARP-таблицы (arp -a)
        4. mDNS-опрос YandexIO / Android TV на порту 5353
        5. Параллельное сканирование всех физических подсетей (192.168.x.1-254, 10.x.x.x, 172.x.x.x)
        Возвращает подробный список всех найденных телевизоров с марками, моделями и комнатами.
        """
        import concurrent.futures

        found_ips = []
        candidates = []

        # 0. Известные устройства из кэша
        known_list = self.get_known_devices()
        known_map = {d["ip"]: d for d in known_list if "ip" in d}
        for ip in known_map:
            if ip not in candidates:
                candidates.append(ip)

        # 1. Проверяем adb devices
        try:
            res = self.run_adb(["devices"])
            for line in res.get("stdout", "").splitlines():
                if "	device" in line or "	unauthorized" in line:
                    parts = line.split("	")[0].split(":")
                    ip = parts[0].strip()
                    if ip and ip.count(".") == 3 and ip not in found_ips:
                        found_ips.append(ip)
                        if ip not in candidates:
                            candidates.append(ip)
        except Exception:
            pass

        # 2. mDNS YandexIO
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
            sock.settimeout(0.5)
            sock.bind(("", 0))
            header = b"\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"
            q = b"\x09_yandexio\x04_tcp\x05local\x00\x00\x0c\x00\x01"
            sock.sendto(header + q, ("224.0.0.251", 5353))
            start_t = time.time()
            while time.time() - start_t < 0.6:
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
            for i in range(1, 255):
                ip = f"{sub}.{i}"
                if ip not in candidates:
                    candidates.append(ip)

        # 5. Быстрая параллельная проверка порта 5555 (таймаут 0.35s)
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

        # Проверяем кандидаты через пул потоков (до 80 одновременных сокетов)
        with concurrent.futures.ThreadPoolExecutor(max_workers=80) as executor:
            futures = [executor.submit(check_port, ip) for ip in candidates]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res and res not in found_ips:
                    found_ips.append(res)

        # 6. Формируем подробные карточки устройств (определяем марку/модель)
        device_cards = []
        for ip in found_ips:
            existing = known_map.get(ip, {})
            brand = existing.get("brand", "")
            model = existing.get("model", "")
            nickname = existing.get("nickname", "")
            name = existing.get("name", "")

            # Если модель еще не известна, попробуем быстро опросить через adb
            if not model or model in ("Smart TV", ""):
                try:
                    target = f"{ip}:5555"
                    self.run_adb(["connect", target], timeout=2)
                    res_m = self.run_adb(["-s", target, "shell", "getprop", "ro.product.model"], timeout=2)
                    res_b = self.run_adb(["-s", target, "shell", "getprop", "ro.product.manufacturer"], timeout=2)
                    m_val = res_m.get("stdout", "").strip()
                    b_val = res_b.get("stdout", "").strip()
                    if m_val:
                        model = m_val
                    if b_val:
                        brand = b_val
                except Exception:
                    pass

            if not name or name in ("Smart TV", "Smart TV (Android)"):
                if brand and model:
                    name = f"{brand} {model}".strip()
                elif brand:
                    name = f"{brand} Smart TV"
                elif model:
                    name = f"Smart TV {model}"
                else:
                    name = "Smart TV (Android)"

            card = {
                "ip": ip,
                "port": 5555,
                "brand": brand or "Android TV",
                "model": model or "Smart TV",
                "name": name,
                "nickname": nickname,
                "is_active": (self.current_device == f"{ip}:5555"),
                "status": "online"
            }
            self.save_known_device(ip, 5555, brand=brand, model=model, nickname=nickname)
            device_cards.append(card)

        # Сортируем: активный ТВ первый, затем с именами комнат, затем остальные
        device_cards.sort(key=lambda x: (not x["is_active"], not bool(x["nickname"]), x["name"]))
        return device_cards


    
    
    def _get_last_known_ip(self) -> Optional[str]:
        devices = self.get_known_devices()
        if devices and isinstance(devices, list):
            for d in devices:
                if isinstance(d, dict) and d.get("ip"):
                    return d["ip"]
        cache_file = self.base_dir / "data" / "last_ip.txt"
        if cache_file.exists():
            try:
                ip = cache_file.read_text(encoding="utf-8").strip()
                if ip:
                    return ip
            except Exception:
                pass
        return None

    def capture_tv_screenshot(self) -> Dict[str, Any]:
        """Захватывает реальный экран телевизора через ADB screencap и возвращает base64 PNG."""
        if not self.current_device:
            last_ip = self._get_last_known_ip()
            if last_ip:
                self.connect_tv(last_ip)
            else:
                res = self.run_adb(["devices"])
                for line in res.get("stdout", "").splitlines():
                    if "\tdevice" in line:
                        self.current_device = line.split("\t")[0].strip()
                        break

        if not self.current_device:
            return {"ok": False, "error": "Телевизор не подключен по ADB. Подключитесь во вкладке «Общее»"}

        # Wake up display if screensaver turned screen off
        self.run_adb(["shell", "input", "keyevent", "224"], timeout=3)
        remote_path = "/sdcard/tv_screenshot.png"
        local_path = self.backups_dir / "tv_current_screen.png"

        self.run_adb(["shell", "screencap", "-p", remote_path], timeout=10)
        pull_res = self.run_adb(["pull", remote_path, str(local_path)], timeout=10)
        self.run_adb(["shell", "rm", remote_path], timeout=5)

        if pull_res.get("ok") and local_path.exists() and local_path.stat().st_size > 1000:
            import base64
            with open(local_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            return {
                "ok": True,
                "image": f"data:image/png;base64,{b64}",
                "size": local_path.stat().st_size,
                "device": self.current_device
            }

        return {"ok": False, "error": "Не удалось получить снимок экрана ТВ"}

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

        if inputs_loc == "top":
            clean_cfg["show_inputs_pill"] = True
            clean_cfg["show_inputs_menu_row"] = True
        elif inputs_loc == "menu":
            clean_cfg["show_inputs_pill"] = False
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
        clean_cfg["top_menu"] = has_collapsed_items
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

    def get_vpn_status(self) -> Dict[str, Any]:
        """Проверяет статус установки поддерживаемых VPN клиентов на телевизоре."""
        status = {
            "wireguard": False,
            "amnezia": False,
            "happ": False,
            "byedpi": False
        }
        if not self.current_device:
            return {"ok": False, "status": status, "error": "ТВ не подключен"}
        res = self.run_adb(["shell", "pm", "list", "packages", "-3"], timeout=8)
        if res.get("ok"):
            stdout = res.get("stdout", "")
            status["wireguard"] = ("com.wireguard.android" in stdout)
            status["amnezia"] = ("org.amnezia.vpn" in stdout)
            status["happ"] = ("su.happ.proxyutility" in stdout)
            status["byedpi"] = ("io.github.dovecoteescapee.byedpi" in stdout or "org.lumic.byedpi" in stdout)
        return {"ok": True, "status": status}

    def install_vpn_client(self, client_name: str) -> Dict[str, Any]:
        """Устанавливает выбранный VPN клиент на ТВ из встроенной папки apps."""
        if not self.current_device:
            last_ip = self._get_last_known_ip()
            if last_ip:
                self.connect_tv(last_ip)
            else:
                return {"ok": False, "error": "Телевизор не подключен по ADB"}

        client = (client_name or "").lower().strip()
        apk_candidates = {
            "wireguard": ["apps/wireguard.apk"],
            "amnezia": ["apps/amnezia.apk"],
            "happ": ["apps/Happ.apk", "apps/media/Happ.apk"],
            "byedpi": ["apps/youtube/ByeDPI_tv.apk", "apps/byedpi.apk"]
        }
        candidates = apk_candidates.get(client, [])
        target_path = None
        for cand in candidates:
            p = self._resolve_file(cand)
            if p.exists() and p.stat().st_size > 100000:
                target_path = p
                break
        
        if not target_path:
            return {"ok": False, "error": f"Файл APK для {client_name} не найден в apps/"}

        self._notify(f"[{client_name.upper()}] Установка {target_path.name} на ТВ...")
        res = self.install_apk_file(str(target_path))
        if res.get("ok"):
            self._notify(f"[{client_name.upper()}] ✓ Приложение успешно установлено на телевизор!")
        return res

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


    def push_wireguard_conf(self, conf_content: str, filename: str = "wg0.conf") -> Dict[str, Any]:
        """Загружает файл конфигурации WireGuard (.conf) в папку Download на ТВ и открывает приложение."""
        if not self.current_device:
            last_ip = self._get_last_known_ip()
            if last_ip:
                self.connect_tv(last_ip)
            else:
                return {"ok": False, "error": "Телевизор не подключен по ADB"}

        if not conf_content or not conf_content.strip():
            return {"ok": False, "error": "Конфигурация WireGuard пуста"}

        if not filename.endswith(".conf"):
            filename = f"{filename}.conf"

        clean_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        if not clean_filename:
            clean_filename = "wg0.conf"

        local_tmp = self.backups_dir / clean_filename
        try:
            with open(local_tmp, "w", encoding="utf-8") as f:
                f.write(conf_content.strip() + "\n")
        except Exception as e:
            return {"ok": False, "error": f"Ошибка сохранения локального файла: {e}"}

        # 1. Create Download dir on TV
        self.run_adb(["shell", "mkdir", "-p", "/sdcard/Download"])
        
        # 2. Push file
        remote_target = f"/sdcard/Download/{clean_filename}"
        push_res = self.run_adb(["push", str(local_tmp), remote_target], timeout=15)
        if not push_res.get("ok"):
            return {"ok": False, "error": f"Ошибка передачи файла на ТВ: {push_res.get('stderr')}"}

        self.run_adb(["shell", "chmod", "666", remote_target])

        # 3. Try to launch WireGuard on TV
        self._notify(f"[WireGuard] Файл {clean_filename} успешно загружен в /sdcard/Download/ на ТВ!")
        self.run_adb(["shell", "am", "start", "-n", "com.wireguard.android/.activity.MainActivity"], timeout=8)

        return {
            "ok": True,
            "msg": f"Конфиг {clean_filename} успешно сохранён в папку «Download» на ТВ! Приложение WireGuard запущено на экране.",
            "path": remote_target
        }

    def import_happ_subscription(self, url: str) -> Dict[str, Any]:
        """Отправляет ссылку подписки в приложение Happ на телевизоре через Android Intent."""
        if not self.current_device:
            last_ip = self._get_last_known_ip()
            if last_ip:
                self.connect_tv(last_ip)
            else:
                return {"ok": False, "error": "Телевизор не подключен по ADB"}

        url = (url or "").strip()
        if not url:
            return {"ok": False, "error": "Ссылка подписки Happ пуста"}

        self._notify(f"[Happ] Отправка ссылки подписки на ТВ: {url[:30]}...")
        self.run_adb(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url], timeout=10)
        
        check_pkg = self.run_adb(["shell", "pm", "path", "su.happ.proxyutility"])
        if not check_pkg.get("ok") or not check_pkg.get("stdout"):
            return {
                "ok": True,
                "msg": "Ссылка отправлена! Примечание: Приложение Happ ещё не установлено на ТВ — установите его кнопкой «Установить Happ».",
                "happ_installed": False
            }

        return {"ok": True, "msg": "Ссылка подписки успешно передана в Happ на телевизоре!", "happ_installed": True}

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

    def get_installed_tv_apps(self) -> Dict[str, Any]:
        """Возвращает список всех установленных на ТВ приложений с понятными именами для выбора в док/скрытие."""
        apps_list = []
        installed_set = set()

        if self.current_device:
            res3 = self.run_adb(["shell", "pm", "list", "packages", "-3"], timeout=10)
            if res3["ok"]:
                for line in res3["stdout"].splitlines():
                    pkg = line.replace("package:", "").strip()
                    if pkg:
                        installed_set.add(pkg)

            res_all = self.run_adb(["shell", "pm", "list", "packages"], timeout=10)
            if res_all["ok"]:
                for line in res_all["stdout"].splitlines():
                    pkg = line.replace("package:", "").strip()
                    if pkg in KNOWN_TV_PACKAGES and KNOWN_TV_PACKAGES[pkg].get("category") in ("user_app", "media_app"):
                        installed_set.add(pkg)

        if installed_set:
            for pkg in sorted(installed_set):
                meta = KNOWN_TV_PACKAGES.get(pkg)
                name = meta["name"] if meta else pkg.split(".")[-1].replace("_", " ").title()
                apps_list.append({
                    "pkg": pkg,
                    "name": name,
                    "desc": meta["desc"] if meta else pkg
                })
        else:
            fallback_pkgs = [
                "mobi.zona", "com.lampa.tv", "ru.rezka.app", "com.google.android.youtube.tv",
                "ru.kinopoisk.tv", "com.vk.vkvideo", "ru.ivi.client", "ru.rt.video.app.tv",
                "com.spb.tv.android", "tv.smarttube.beta", "com.google.android.apps.tv.launcherx"
            ]
            for pkg in fallback_pkgs:
                meta = KNOWN_TV_PACKAGES.get(pkg)
                name = meta["name"] if meta else pkg
                apps_list.append({
                    "pkg": pkg,
                    "name": name,
                    "desc": meta["desc"] if meta else pkg
                })

        return {"ok": True, "apps": apps_list}


# Backwards compatibility aliases for CLI/Tkinter scripts
_default_mgr = SmartTVManager()
ADB = _default_mgr.adb_bin
APPS_DIR = str(_default_mgr.base_dir / 'apps')
PRESETS = _default_mgr.packages_db.get('profiles', {})
