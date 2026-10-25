# -*- coding: utf-8 -*-
import sys
import os
import socket
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ADB = os.path.join(SCRIPT_DIR, "platform-tools", "adb.exe")
APPS_DIR = os.path.join(SCRIPT_DIR, "apps")

def log(msg):
    print(f"[*] {msg}", flush=True)

def find_tv_ip():
    log("Поиск телевизора в локальной сети...")
    
    # 1. Сначала пробуем mDNS быстрый опрос YandexIO
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        sock.settimeout(2.0)
        sock.bind(('', 0))
        
        # DNS query for _yandexio._tcp.local
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
                    log(f"Найдено устройство Яндекс ТВ через mDNS: {ip}")
                    return ip
            except socket.timeout:
                break
        sock.close()
    except Exception:
        pass

    # 2. Если mDNS не ответил, смотрим кэш ARP и пробуем порт 5555
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
        ip = input("Пожалуйста, введите IP-адрес телевизора вручную (например, 192.168.3.54): ").strip()
    
    log(f"Подключение к телевизору {ip}:5555 ...")
    subprocess.run([ADB, "connect", f"{ip}:5555"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    
    devs = subprocess.check_output([ADB, "devices"]).decode('utf-8', errors='ignore')
    if "device\n" in devs or "device\r" in devs or f"{ip}:5555\tdevice" in devs:
        log("Успешно подключено по ADB!")
        return ip
    elif "unauthorized" in devs:
        log("\n[ВНИМАНИЕ] На экране телевизора появилось окно «Разрешить отладку».")
        log("Поставьте галочку «Всегда разрешать» и нажмите ОК пультом!")
        input("После нажатия ОК нажмите Enter для продолжения...")
        return connect_adb(ip)
    else:
        log("\n[ОШИБКА] Не удалось подключиться к порту 5555.")
        log("Убедитесь, что телевизор включен и в сервисном меню включен ADB (ON).")
        return None

def adb_shell(ip, cmd):
    res = subprocess.run([ADB, "-s", f"{ip}:5555", "shell", cmd], capture_output=True, text=True)
    return res.stdout.strip()

def action_install_apps(ip):
    log("\n--- УСТАНОВКА ПРИЛОЖЕНИЙ (Zona, HDrezka, File Manager+, SmartTube) ---")
    apks = ["hdrezka.apk", "zona.apk", "filemanager_plus.apk", "smarttube.apk", "Happ.apk"]
    for apk_name in apks:
        p = os.path.join(APPS_DIR, apk_name)
        if os.path.exists(p):
            log(f"Установка {apk_name} ...")
            res = subprocess.run([ADB, "-s", f"{ip}:5555", "install", "-r", p], capture_output=True, text=True)
            if "Success" in res.stdout or "Success" in res.stderr:
                log(f" -> {apk_name} успешно установлено!")
            else:
                log(f" -> {apk_name}: {res.stdout.strip()} {res.stderr.strip()}")
        else:
            log(f"Файл {apk_name} не найден в папке apps.")

def action_light_debloat(ip):
    log("\n--- ЛЕГКАЯ ОПТИМИЗАЦИЯ (Отключение рекламы и тяжелых фоновых служб) ---")
    log("Лаунчер Яндекса остается активным, сохраняются все базовые функции!")
    pkgs = [
        "com.yandex.android.advid",       # Рекламный трекер
        "com.yandex.tv.bugreportsender",  # Фоновый сборщик отчетов и логов
        "com.yandex.launcher.updaterapp", # Фоновый автообновлятор рекламы
        "com.yandex.tv.daydream",         # Заставка
        "com.yandex.browser.tv"           # Встроенный фоновый браузер
    ]
    for pkg in pkgs:
        un = adb_shell(ip, f"pm uninstall --user 0 {pkg}")
        adb_shell(ip, f"am force-stop {pkg}")
        log(f"Отключение {pkg}: {un}")
    log("Легкая оптимизация выполнена!")

def action_full_debloat(ip):
    log("\n--- ПОЛНЫЙ ДЕБЛОАТ И ПЕРЕХОД НА ЧИСТЫЙ FLAUNCHER ---")
    
    fl_apk = os.path.join(APPS_DIR, "flauncher.apk")
    if os.path.exists(fl_apk):
        log("Установка FLauncher...")
        subprocess.run([ADB, "-s", f"{ip}:5555", "install", "-r", fl_apk], capture_output=True)
    
    log("Назначение FLauncher домашним экраном...")
    adb_shell(ip, "cmd package set-home-activity me.efesser.flauncher/.MainActivity")
    
    pkgs = [
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
    for pkg in pkgs:
        un = adb_shell(ip, f"pm uninstall --user 0 {pkg}")
        adb_shell(ip, f"am force-stop {pkg}")
        log(f"Отключение {pkg}: {un}")
    
    adb_shell(ip, "am start -a android.intent.action.MAIN -c android.intent.category.HOME")
    log("Полный деблоат завершен! Домашний экран теперь чистый FLauncher.")

def action_restore(ip):
    log("\n--- ПОЛНОЕ ВОССТАНОВЛЕНИЕ ЗАВОДСКИХ СЕРВИСОВ ЯНДЕКС ТВ ---")
    pkgs = [
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
    for pkg in pkgs:
        res = adb_shell(ip, f"cmd package install-existing {pkg}")
        log(f"Восстановление {pkg}: {res}")
    
    log("Возврат стандартного домашнего экрана Яндекса...")
    adb_shell(ip, "cmd package set-home-activity com.yandex.tv.home/.HomeActivity")
    adb_shell(ip, "am start -a android.intent.action.MAIN -c android.intent.category.HOME")
    log("Восстановление завершено! Телевизор вернулся в исходное состояние.")

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    
    ip = connect_adb()
    if not ip:
        print("\nЗавершение работы: нет связи с ТВ.")
        input("\nНажмите Enter для выхода...")
        return

    if mode == "install":
        action_install_apps(ip)
    elif mode == "light_debloat":
        action_light_debloat(ip)
    elif mode == "full_debloat":
        action_install_apps(ip)
        action_full_debloat(ip)
    elif mode == "restore":
        action_restore(ip)
    else:
        while True:
            print("\n" + "="*55)
            print(f" МЕНЕДЖЕР ТЕЛЕВИЗОРА (IP: {ip})")
            print("="*55)
            print(" 1. Установить приложения (HDrezka, Zona, File Manager+, SmartTube)")
            print(" 2. Легкая оптимизация (Отключить рекламу, ЯНДЕКС ЛАУНЧЕР ОСТАЕТСЯ)")
            print(" 3. Полная оптимизация (Установить всё + чистый FLauncher)")
            print(" 4. Восстановить всё как было (Заводской Яндекс ТВ)")
            print(" 0. Выход")
            print("="*55)
            choice = input("Выберите вариант (0-4): ").strip()
            if choice == "1":
                action_install_apps(ip)
            elif choice == "2":
                action_light_debloat(ip)
            elif choice == "3":
                action_full_debloat(ip)
            elif choice == "4":
                action_restore(ip)
            elif choice == "0":
                break
            else:
                print("Неверный выбор.")

    input("\nГотово! Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
