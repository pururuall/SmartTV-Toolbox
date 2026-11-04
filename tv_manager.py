# -*- coding: utf-8 -*-
import sys
import os
import json
import socket
import subprocess
import time

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    MEIPASS_DIR = getattr(sys, '_MEIPASS', BASE_DIR)
    SCRIPT_DIR = BASE_DIR
    # Check candidates for ADB
    found_adb = None
    for cand in [
        os.path.join(MEIPASS_DIR, "platform-tools", "adb.exe"),
        os.path.join(BASE_DIR, "platform-tools", "adb.exe"),
        os.path.join(os.getcwd(), "platform-tools", "adb.exe")
    ]:
        if os.path.exists(cand):
            found_adb = cand
            break
    ADB = found_adb or os.path.join(BASE_DIR, "platform-tools", "adb.exe")

    # Check candidates for APPS_DIR
    found_apps = None
    for cand_apps in [
        os.path.join(BASE_DIR, "apps"),
        os.path.join(os.getcwd(), "apps")
    ]:
        if os.path.exists(cand_apps):
            found_apps = cand_apps
            break
    APPS_DIR = found_apps or os.path.join(BASE_DIR, "apps")
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ADB = os.path.join(SCRIPT_DIR, "platform-tools", "adb.exe")
    APPS_DIR = os.path.join(SCRIPT_DIR, "apps")

PRESETS = {
    "top6": ["zona.apk", "hdrezka.apk", "lampa.apk", "spotify.apk", "filemanager_plus.apk", "Happ.apk"],
    "basic": ["hdrezka.apk", "zona.apk", "filemanager_plus.apk", "smarttube.apk", "Happ.apk"]
}

YAOS_PACKAGES_LIGHT = [
    "com.yandex.android.advid",
    "com.yandex.tv.bugreportsender",
    "com.yandex.launcher.updaterapp",
    "com.yandex.tv.daydream",
    "com.yandex.browser.tv"
]

YAOS_PACKAGES_FULL = [
    "com.yandex.tv.alice",
    "com.yandex.tv.home",
    "com.yandex.tv.music",
    "com.yandex.browser.tv",
    "com.yandex.tv.live",
    "com.yandex.tv.input.efir",
    "com.yandex.tv.daydream",
    "com.yandex.tv.bugreportsender",
    "com.yandex.android.advid",
    "com.yandex.tv.ytplayer",
    "com.yandex.tv.webplayer",
    "com.yandex.tv.videoplayer",
    "com.yandex.launcher.updaterapp"
]

GENERIC_PACKAGES_LIGHT = [
    "com.google.android.tungsten.setupwraith",
    "com.google.android.feedback",
    "com.google.android.tvrecommendations",
    "com.xiaomi.mitv.advertise",
    "com.xiaomi.mitv.upgrade",
    "com.tcl.partnercustomizer",
    "com.sony.dtv.bravialife"
]

GENERIC_PACKAGES_FULL = [
    "com.google.android.apps.tv.launcherx",
    "com.google.android.tungsten.setupwraith",
    "com.google.android.feedback",
    "com.google.android.tvrecommendations",
    "com.mitv.tvhome",
    "com.xiaomi.mitv.advertise",
    "com.xiaomi.mitv.upgrade",
    "com.duokan.videodaily",
    "com.tcl.partnercustomizer",
    "com.tcl.videoplayer",
    "com.tcl.tvmanager",
    "com.sony.dtv.bravialife",
    "com.sony.dtv.smartmediaapp"
]

LOGGER = None

def set_logger(fn):
    global LOGGER
    LOGGER = fn

def log(msg):
    print(f"[*] {msg}", flush=True)
    if LOGGER:
        try:
            LOGGER(msg)
        except Exception:
            pass

def find_tv_ip():
    log("Поиск телевизора в локальной сети...")
    
    # 1. mDNS опрос YandexIO
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        sock.settimeout(2.0)
        sock.bind(('', 0))
        
        header = b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
        q = b'\x09_yandexio\x04_tcp\x05local\x00\x00\x0c\x00\x01'
        sock.sendto(header + q, ('224.0.0.251', 5353))
        
        start = time.time()
        while time.time() - start < 2.5:
            try:
                buf, addr = sock.recvfrom(2048)
                ip = addr[0]
                if b'yandex' in buf.lower():
                    sock.close()
                    log(f"Найдено устройство в сети: {ip}")
                    return ip
            except socket.timeout:
                break
        sock.close()
    except Exception:
        pass

    # 2. Сканирование ARP-кэша на порт 5555
    try:
        arp_out = subprocess.check_output("arp -a", shell=True).decode('cp866', errors='ignore')
        ips = []
        for line in arp_out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2 and parts[0].count('.') == 3 and not parts[0].startswith('224.') and not parts[0].startswith('239.') and not parts[0].endswith('.255'):
                ips.append(parts[0])
        
        for ip in ips:
            s = socket.socket()
            s.settimeout(0.3)
            if s.connect_ex((ip, 5555)) == 0:
                s.close()
                log(f"Найден телевизор с открытым портом 5555: {ip}")
                return ip
            s.close()
    except Exception:
        pass

    return None

def connect_adb(ip=None):
    if not ip:
        ip = find_tv_ip()
    if not ip:
        print("\n[!] Не удалось автоматически обнаружить IP телевизора.")
        ip = input("Пожалуйста, введите IP-адрес телевизора вручную (например, 192.168.1.50): ").strip()
    
    log(f"Подключение к телевизору {ip}:5555 ...")
    subprocess.run([ADB, "connect", f"{ip}:5555"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    
    devs = subprocess.check_output([ADB, "devices"]).decode('utf-8', errors='ignore')
    if "device\n" in devs or "device\r" in devs or f"{ip}:5555\tdevice" in devs:
        log("Успешно подключено по ADB!")
        return ip
    elif "unauthorized" in devs:
        log("\n[ВНИМАНИЕ] На экране телевизора появилось окно «Разрешить отладку».")
        log("Поставьте галочку «Всегда разрешать с этого компьютера» и нажмите ОК пультом!")
        input("После нажатия ОК нажмите Enter для продолжения...")
        return connect_adb(ip)
    else:
        log("\n[ОШИБКА] Не удалось подключиться к порту 5555.")
        log("Убедитесь, что телевизор и ПК в одной Wi-Fi сети и отладка включена.")
        return None

def adb_shell(ip, cmd):
    res = subprocess.run([ADB, "-s", f"{ip}:5555", "shell", cmd], capture_output=True, text=True)
    return res.stdout.strip()

def action_test_connection(manual_ip=None):
    log("=== ПРОВЕРКА ВОЗМОЖНОСТИ СОЕДИНЕНИЯ С ТЕЛЕВИЗОРОМ ===")
    ip = connect_adb(manual_ip)
    if not ip:
        print("\n[ОШИБКА] СВЯЗЬ НЕ УСТАНОВЛЕНА!")
        print("Телевизор не отвечает по порту 5555.")
        return None
    
    try:
        model = adb_shell(ip, "getprop ro.product.model")
        brand = adb_shell(ip, "getprop ro.product.brand")
        android_v = adb_shell(ip, "getprop ro.build.version.release")
        launcher = adb_shell(ip, "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME")
        cur_launcher = launcher.splitlines()[-1] if launcher else "Unknown"
        
        dns_mode = adb_shell(ip, "settings get global private_dns_mode")
        dns_spec = adb_shell(ip, "settings get global private_dns_specifier")
        dns_status = "AdGuard DNS АКТИВЕН" if (dns_mode == "hostname" and "adguard" in dns_spec.lower()) else "Стандартный DNS"

        print("\n" + "="*55)
        print("[УСПЕХ] ТЕЛЕВИЗОР НА СВЯЗИ!")
        print("="*55)
        print(f" • IP-адрес:         {ip}:5555")
        print(f" • Марка / Модель:   {brand} {model}")
        print(f" • Версия Android:   {android_v}")
        print(f" • Текущий лаунчер:  {cur_launcher}")
        print(f" • Защита от рекламы:{dns_status}")
        print(" • Статус отладки:   РАЗРЕШЕНО (Полный доступ к управлению)")
        print("="*55)
        return {
            "ip": ip,
            "brand": brand,
            "model": model,
            "android": android_v,
            "launcher": cur_launcher,
            "dns_mode": dns_mode,
            "dns_specifier": dns_spec
        }
    except Exception as e:
        print(f"[!] Ошибка чтения свойств: {e}")
        return None

def action_install_apps(ip, apks=None):
    if not apks:
        apks = PRESETS["top6"]
    elif isinstance(apks, str):
        apks = PRESETS.get(apks, [apks])
    elif apks == "all":
        apks = [f for f in os.listdir(APPS_DIR) if f.lower().endswith(".apk")]

    log(f"\n--- ПОДГРУЗКА ПРИЛОЖЕНИЙ ({len(apks)} шт.) ---")
    installed_count = 0
    for apk_name in apks:
        p = os.path.join(APPS_DIR, apk_name)
        if os.path.exists(p):
            log(f"Установка {apk_name} ...")
            res = subprocess.run([ADB, "-s", f"{ip}:5555", "install", "-r", p], capture_output=True, text=True)
            if "Success" in res.stdout or "Success" in res.stderr:
                log(f" -> {apk_name} успешно установлено!")
                installed_count += 1
            else:
                log(f" -> {apk_name}: {res.stdout.strip()} {res.stderr.strip()}")
        else:
            log(f"Файл {apk_name} не найден в папке apps.")
    log(f"Подгрузка завершена! Успешно установлено: {installed_count} из {len(apks)}.")
    return installed_count

def action_set_dns(ip, enable=True):
    if enable:
        log("Включение AdGuard Private DNS на телевизоре...")
        adb_shell(ip, "settings put global private_dns_mode hostname")
        adb_shell(ip, "settings put global private_dns_specifier dns.adguard-dns.com")
        log("✅ Системная блокировка рекламы (AdGuard DNS) успешно АКТИВИРОВАНА!")
        return True
    else:
        log("Отключение Private DNS на телевизоре...")
        adb_shell(ip, "settings put global private_dns_mode off")
        adb_shell(ip, "settings put global private_dns_specifier ''")
        log("⚪ Private DNS отключен (восстановлен стандартный DNS).")
        return False

def action_get_dns(ip):
    mode = adb_shell(ip, "settings get global private_dns_mode")
    spec = adb_shell(ip, "settings get global private_dns_specifier")
    enabled = (mode == "hostname" and "adguard" in spec.lower())
    return {"enabled": enabled, "mode": mode, "specifier": spec}

def action_set_dock(ip, dock_apps=None, columns=6):
    if not dock_apps:
        dock_apps = [
            "mobi.zona",
            "com.falcofemoralis.hdrezkaapp",
            "ru.twicker.lampa",
            "com.spotify.tv.android",
            "su.happ.proxyutility",
            "com.alphainventor.filemanager"
        ]
    cfg = {
        "columns": columns,
        "dock_apps": dock_apps,
        "fill_dock": True,
        "reorder_button": True
    }
    cfg_json = json.dumps(cfg, indent=2, ensure_ascii=False)
    tmp_path = os.path.join(SCRIPT_DIR, "dock_config.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(cfg_json)
    
    adb_shell(ip, "mkdir -p /sdcard/Android/data/com.gathin.tvhome/files")
    subprocess.run([ADB, "-s", f"{ip}:5555", "push", tmp_path, "/sdcard/Android/data/com.gathin.tvhome/files/config.json"], capture_output=True)
    if os.path.exists(tmp_path):
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    adb_shell(ip, "am force-stop com.gathin.tvhome")
    adb_shell(ip, "am start -n com.gathin.tvhome/.MainActivity")
    log("Конфигурация дока успешно обновлена на телевизоре!")
    return True

def action_switch_launcher(ip, launcher_name="cleanyourtv"):
    if launcher_name == "cleanyourtv":
        apk_p = os.path.join(APPS_DIR, "cleanyourtv.apk")
        if os.path.exists(apk_p):
            subprocess.run([ADB, "-s", f"{ip}:5555", "install", "-r", apk_p], capture_output=True)
        adb_shell(ip, "cmd package set-home-activity com.gathin.tvhome/.MainActivity")
        adb_shell(ip, "am start -a android.intent.action.MAIN -c android.intent.category.HOME")
        log("Успешно активирован Apple TV лаунчер CleanYourTV!")
    elif launcher_name == "flauncher":
        apk_p = os.path.join(APPS_DIR, "flauncher.apk")
        if os.path.exists(apk_p):
            subprocess.run([ADB, "-s", f"{ip}:5555", "install", "-r", apk_p], capture_output=True)
        adb_shell(ip, "cmd package set-home-activity me.efesser.flauncher/.MainActivity")
        adb_shell(ip, "am start -a android.intent.action.MAIN -c android.intent.category.HOME")
        log("Успешно активирован FLauncher!")
    return True

def action_light_debloat(ip, tv_type="yaos"):
    pkgs = YAOS_PACKAGES_LIGHT if tv_type == "yaos" else GENERIC_PACKAGES_LIGHT
    log(f"\n--- ЛЕГКАЯ ОПТИМИЗАЦИЯ ({tv_type.upper()}) ---")
    log("Отключение рекламы и аналитики через pm disable-user...")
    count = 0
    for pkg in pkgs:
        un = adb_shell(ip, f"pm disable-user --user 0 {pkg}")
        adb_shell(ip, f"am force-stop {pkg}")
        log(f"Заморозка {pkg}: {un}")
        count += 1
    log(f"Легкая оптимизация выполнена! Заморожено {count} служб.")
    return True

def action_full_debloat(ip, tv_type="yaos", launcher_choice="cleanyourtv"):
    log(f"\n--- ПОЛНЫЙ ДЕБЛОАТ И ПЕРЕХОД НА ЛАУНЧЕР ({launcher_choice.upper()}) ---")
    
    # 1. Установка и назначение лаунчера
    action_switch_launcher(ip, launcher_choice)
    
    # Настройка дока, если выбран CleanYourTV
    if launcher_choice == "cleanyourtv":
        action_set_dock(ip)
    
    # 2. Заморозка вендорских и рекламных служб
    pkgs = YAOS_PACKAGES_FULL if tv_type == "yaos" else GENERIC_PACKAGES_FULL
    for pkg in pkgs:
        un = adb_shell(ip, f"pm disable-user --user 0 {pkg}")
        adb_shell(ip, f"am force-stop {pkg}")
        log(f"Заморозка {pkg}: {un}")
    
    adb_shell(ip, "am start -a android.intent.action.MAIN -c android.intent.category.HOME")
    log(f"Полный деблоат завершен! Домашний экран переведен на {launcher_choice.upper()}.")
    return True

def action_restore(ip, tv_type="yaos"):
    log(f"\n--- ВОССТАНОВЛЕНИЕ СТАНДАРТНОЙ СИСТЕМЫ ({tv_type.upper()}) ---")
    pkgs = YAOS_PACKAGES_FULL if tv_type == "yaos" else GENERIC_PACKAGES_FULL
    for pkg in pkgs:
        res = adb_shell(ip, f"pm enable {pkg}")
        log(f"Включение {pkg}: {res}")
    
    if tv_type == "yaos":
        log("Возврат стандартного домашнего экрана Яндекса...")
        adb_shell(ip, "cmd package set-home-activity com.yandex.tv.home/.HomeActivity")
    else:
        log("Возврат стандартного домашнего экрана Google TV...")
        adb_shell(ip, "cmd package set-home-activity com.google.android.apps.tv.launcherx/.home.HomeActivity")
        adb_shell(ip, "cmd package set-home-activity com.mitv.tvhome/.MainActivity")
    
    adb_shell(ip, "am start -a android.intent.action.MAIN -c android.intent.category.HOME")
    log("Восстановление завершено! Телевизор вернулся в исходное заводское состояние.")
    return True

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    
    if mode == "test":
        action_test_connection()
        try:
            input("\nНажмите Enter для выхода...")
        except EOFError:
            pass
        return
    
    ip = connect_adb()
    if not ip:
        print("\nЗавершение работы: нет связи с ТВ.")
        try:
            input("\nНажмите Enter для выхода...")
        except EOFError:
            pass
        return

    if mode == "install":
        preset = sys.argv[2] if len(sys.argv) > 2 else "top6"
        action_install_apps(ip, preset)
    elif mode == "dns_on":
        action_set_dns(ip, True)
    elif mode == "dns_off":
        action_set_dns(ip, False)
    elif mode == "light_debloat":
        action_light_debloat(ip, "yaos")
    elif mode == "full_debloat":
        action_install_apps(ip, "top6")
        action_full_debloat(ip, "yaos", "cleanyourtv")
    elif mode == "restore":
        action_restore(ip, "yaos")
    else:
        while True:
            print("\n" + "="*55)
            print(f" SMART TV TOOLBOX v2.0 (IP: {ip})")
            print("="*55)
            print(" 0. Проверить соединение с телевизором")
            print(" 1. Подгрузка приложений (Zona, HDrezka, Lampa, Spotify, Happ, FM+)")
            print(" 2. Переключить на Apple TV лаунчер CleanYourTV")
            print(" 3. Переключить на FLauncher")
            print(" 4. Включить AdGuard DNS блокировку рекламы")
            print(" 5. Отключить AdGuard DNS (стандартный DNS)")
            print(" 6. Полная оптимизация Яндекс ТВ (Apple TV лаунчер + деблоат)")
            print(" 7. Восстановить всё как было (Заводской Яндекс ТВ)")
            print(" 9. Выход")
            print("="*55)
            choice = input("Выберите вариант: ").strip()
            if choice == "0":
                action_test_connection(ip)
            elif choice == "1":
                action_install_apps(ip, "top6")
            elif choice == "2":
                action_switch_launcher(ip, "cleanyourtv")
            elif choice == "3":
                action_switch_launcher(ip, "flauncher")
            elif choice == "4":
                action_set_dns(ip, True)
            elif choice == "5":
                action_set_dns(ip, False)
            elif choice == "6":
                action_full_debloat(ip, "yaos", "cleanyourtv")
            elif choice == "7":
                action_restore(ip, "yaos")
            elif choice in ["9", "q", "exit"]:
                break
            else:
                print("Неверный выбор.")

    try:
        input("\nГотово! Нажмите Enter для выхода...")
    except EOFError:
        pass

if __name__ == "__main__":
    main()
