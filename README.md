<div align="center">

<img src="img/banner_header%20v3.0.jpg" alt="Smart TV Toolbox v3.0" width="100%">

<br/><br/>

[![Версия](https://img.shields.io/badge/Версия-v3.0.0_Major-6366f1?style=for-the-badge&logo=github&logoColor=white)](https://github.com/pururuall/SmartTV-Toolbox/releases/latest)
[![Скачать SmartTV_Control.exe](https://img.shields.io/badge/СКАЧАТЬ_SmartTV__Control.exe-22c55e?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/pururuall/SmartTV-Toolbox/releases/latest/download/SmartTV_Control.exe)
[![Скачать весь ZIP](https://img.shields.io/badge/СКАЧАТЬ_ВЕСЬ_РЕПОЗИТОРИЙ-(ZIP)-3b82f6?style=for-the-badge&logo=github&logoColor=white)](https://github.com/pururuall/SmartTV-Toolbox/archive/refs/heads/main.zip)

<br/>

### 🍊 [👉 НАЖМИТЕ ЗДЕСЬ, ЧТОБЫ СКАЧАТЬ ПОСЛЕДНЮЮ ВЕРСИЮ SmartTV_Control.exe (v3.0.0) 👈](https://github.com/pururuall/SmartTV-Toolbox/releases/latest/download/SmartTV_Control.exe)

*(Автономная программа с нативным интерфейсом и иконкой капибары. Не требует установки Python или ADB. Ссылка всегда загружает самый свежий релиз)*

</div>

---

Комплект скриптов, утилит и официальное приложение **SmartTV_Control.exe** (версия **3.0.0**) для глубокой очистки, ускорения, тонкой настройки лаунчеров и обхода замедлений YouTube на любых Smart TV под управлением Android 9–14: **Яндекс ТВ (YaOS / CVTE)** (Tuvio, Hartens, DEXP, Novex, Hi), **Салют ТВ (StarOS / SberBox)**, **Haier** (MatrixTV / uSmart), **Xiaomi / Redmi** (PatchWall), **TCL / iFFALCON** и стандартных **Android TV / Google TV**.

---

## 📸 Скриншоты и демонстрация работы

<div align="center">

### 🖥️ Интерфейс приложения Smart TV Toolbox v3.0

*(Полнофункциональный центр управления: 5 специализированных вкладок, интерактивный калькулятор ОЗУ и Live ADB-терминал)*

<br/>

<details open>
<summary><b>📡 Вкладка 1: Подключение, беспроводное сопряжение и диагностика ОЗУ</b></summary>
<br/>
<img src="img/tab1_connect.png" alt="Вкладка 1: Подключение и диагностика ОЗУ" width="94%">
</details>

<br/>

<details open>
<summary><b>🧹 Вкладка 2: Попакетный конструктор очистки (Debloat) с защитой Hardware Guard</b></summary>
<br/>
<img src="img/tab2_debloat.png" alt="Вкладка 2: Кастомная очистка" width="94%">
</details>

<br/>

<details open>
<summary><b>🍎 Вкладка 3: Лаунчеры (CleanYourTV / Мой ТВ / Projectivy / FLauncher) и Галерея Обоев</b></summary>
<br/>
<img src="img/tab3_launchers.png" alt="Вкладка 3: Лаунчеры и Обои" width="94%">
</details>

<br/>

<details>
<summary><b>⚡ Вкладка 4: SmartTube без рекламы и обход замедлений (ByeDPI / Прокси / DNS)</b></summary>
<br/>
<img src="img/tab4_youtube.png" alt="Вкладка 4: SmartTube и Обход" width="94%">
</details>

<br/>

<details>
<summary><b>📦 Вкладка 5: Каталог медиа-приложений APK и Live ADB консоль</b></summary>
<br/>
<img src="img/tab5_apps.png" alt="Вкладка 5: Каталог APK" width="94%">
</details>

<br/><br/>

### 📺 1. Лаунчер CleanYourTV (Apple TV Style) на ТВ
*(Ультралегкий домашний экран ~500 КБ с настраиваемым доком Топ-6 приложений и нулевой рекламой)*

<img src="img/tv_home_clean.png" alt="Лаунчер CleanYourTV на экране телевизора" width="94%">

<br/><br/>

### 📺 2. Лаунчер «Мой ТВ» (Moy-TV) на ТВ
*(Информационный дашборд с виджетами погоды, курсов валют ЦБ РФ, новостей, ярлыками HDMI 1–3 и веб-пультом)*

<img src="img/moytv_screen.png" alt="Лаунчер Мой ТВ на экране телевизора" width="94%">

<br/><br/>

### 📺 3. Лаунчер FLauncher на ТВ
*(Классический Open-Source лаунчер под Android TV с настраиваемыми категориями и сеткой)*

<img src="img/flauncher_screen.png" alt="Лаунчер FLauncher на экране телевизора" width="94%">

<br/><br/>

### 📺 4. Лаунчер Projectivy Launcher на ТВ
*(Премиальный современный интерфейс: динамические каналы рекомендаций, быстрое переключение входов HDMI 1–3, калибровка дисплея и нулевая реклама)*

<img src="img/projectivy_screen.png" alt="Лаунчер Projectivy на экране телевизора" width="94%">

</div>

---

## 🌟 Что нового в версии 3.0.0 (Custom-First)

Проект полностью модернизирован и объединил базы знаний и архитектурные решения из четырёх профильных экосистем: **SmartTV-Toolbox**, **[Jipok/tv-cleaner](https://github.com/Jipok/tv-cleaner)**, **[andrewm8888/moy-tv](https://github.com/andrewm8888/moy-tv)** и **[by-sonic/chistytv](https://github.com/by-sonic/chistytv)**.

### 1. 📡 Вкладка 1: Подключение, беспроводное сопряжение и ОЗУ
- **Автоопределение шасси:** Система считывает вендора, модель, версию Android и рекомендуемый профиль очистки.
- **Диагностика RAM и ZRAM:** Анализ реальной загрузки ОЗУ и swap через `dumpsys meminfo` до и после оптимизации.
- **Wireless Pairing (Android 11–14):** Быстрое сопряжение по 6-значному коду и порту без проводов.

### 2. 🧹 Вкладка 2: Попакетный конструктор очистки
- **Выбор профилей по брендам:** Яндекс ТВ (YaOS), Салют ТВ, Haier, Xiaomi, TCL, Google TV.
- **Калькулятор ОЗУ:** Динамический подсчет освобождаемой оперативной памяти (в МБ) перед применением деблоата.
- **Hardware Guard (tv-cleaner):** Критические службы HDMI, ТВ-тюнера и кнопок пульта защищены аппаратным стоп-листом и заблокированы от случайного отключения.
- **100% обратимость:** Автоматический слепок состояния перед отключением и кнопка «Откат: Включить всё назад» в 1 клик.

### 3. 🍎 Вкладка 3: Лаунчеры и Обои прямо с ПК
- **Выбор домашнего экрана:**
  - **Мой ТВ (Moy-TV):** Информационный дашборд с виджетами погоды, новостей, управлением подсветкой, именами HDMI 1–3 и локальным веб-пультом (порт `8080`).
  - **CleanYourTV:** Ультралегкий Apple TV интерфейс (~500 КБ) с динамической настройкой нижнего дока.
  - **Projectivy Launcher:** Премиальный домашний экран с поддержкой динамических каналов Android TV, переключением входов HDMI 1–3, профилями калибровки изображения, родительским контролем и нулевой рекламой.
  - **FLauncher:** Классический открытый лаунчер с настраиваемой сеткой и категориями.
- **Встроенная галерея обоев:** Готовая подборка ТВ-обоев высокого разрешения (1080p / 4K) и прямая загрузка любых изображений с ПК в память лаунчера на ТВ.

### 4. ⚡ Вкладка 4: SmartTube и обход замедлений YouTube
- **SmartTube Stable:** Установка актуального клиента YouTube без рекламы, со SponsorBlock и поддержкой 4K HDR.
- **Принудительный AVC/H.264 кодек:** Автоматическая преднастройка кодека и размера буфера для плавного воспроизведения на слабых процессорах (1 ГБ ОЗУ).
- **Гибкие методы обхода замедлений:**
  - **ByeDPI на ТВ:** Запуск локального прокси со сплитом пакетов (`--split 1+s --disorder 3 --ttl 5` и др.).
  - **Внешний SOCKS5/HTTP прокси.**
  - **AdGuard Private DNS:** Системная блокировка рекламы на уровне ОС Android без сторонних VPN.

### 5. 📦 Вкладка 5: Каталог APK и Live ADB консоль
- **Пакетная установка проверенного софта:** Zona TV, HDRezka TV, LAMPA, SmartTube, File Manager+, Happ Proxy, Spotify TV, ByeDPI TV.
- **Интерактивный терминал ADB:** Правая колонка с живым журналом выполнения команд и строкой прямого ввода для опытных пользователей.

---

## 🛠️ Содержимое репозитория

| Файл / Папка | Назначение |
|---|---|
| **`SmartTV_Control.exe`** | 🚀 **Главное приложение (v3.0.0):** 5-вкладочная панель, конструктор лаунчеров, Live ADB консоль |
| `data/packages.json` | 📋 Единая декларативная база пакетов по брендам со стоп-листами (tv-cleaner + chistytv) |
| `data/launchers.json` | 🍎 Метаданные лаунчеров (Moy-TV, CleanYourTV, Projectivy, FLauncher) и пути к конфигам |
| `wallpapers/` | 🖼️ Встроенная коллекция оптимизированных обоев для ТВ |
| `apps/` | 📦 Структурированный каталог APK (лаунчеры, youtube, медиа) |
| `START_HERE.html` | 📖 Интерактивный веб-интерфейс (автономный запуск в браузере) |
| `Instruction.html` | 📖 Автономная копия интерактивной панели |
| `tv_manager.py` | ⚙️ Единый контроллер SmartTVManager (ADB, диагностика ОЗУ, деблоат, YouTube) |
| `main_webview.py` | 🖥️ Нативный графический интерфейс на WebView2 |
| `server.py` | 🌐 Локальный HTTP-сервер (строго `127.0.0.1`) для запуска через браузер |
| `platform-tools/` | Официальные утилиты ADB от Google под Windows |
| `img/` | Баннеры и скриншоты приложения и всех поддерживаемых лаунчеров |

---

## 📖 Инструкция по быстрому запуску

### Включение отладки по сети:
1. **Яндекс ТВ / CVTE (Tuvio, Hartens, DEXP, Novex):** Зажмите кнопку **Menu** (1–2 сек) ➔ быстро нажмите: `Влево ➔ Вверх ➔ Влево ➔ Вверх` ➔ кнопка **Назад** ➔ в меню Factory перейдите в `other options` ➔ установите **`ADB: ON`** (если есть `USB Mode` — выберите **`Device`**).
2. **Android TV / Google TV (Haier, Xiaomi, TCL, Sony, Hisense):** Откройте `Настройки` ➔ `Об устройстве` ➔ нажмите **OK 7 раз на пункте «Номер сборки»** ➔ вернитесь в меню `Для разработчиков` ➔ включите **«Отладка по USB»** (или Wireless Debugging).

### Запуск программы:
1. Запустите **`SmartTV_Control.exe`**.
2. Введите IP телевизора (или нажмите «🔍 Автопоиск ТВ») и нажмите **«📡 Подключиться»**.
3. При первом подключении на экране телевизора подтвердите запрос *«Разрешить отладку по USB?»* (поставьте галочку *«Всегда разрешать с этого компьютера»*).
4. Переходите между вкладками для диагностики ОЗУ, отключения рекламы, настройки лаунчеров и SmartTube!
