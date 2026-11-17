# -*- coding: utf-8 -*-
"""
core.adb_client
Низкоуровневая работа с adb.exe, сокетами и устройствами.
"""
import os
import sys
import re
import socket
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class AdbClientMixin:
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


    def run_raw_adb(self, cmd_str: str) -> Dict[str, Any]:

        """Выполнение произвольной команды в терминале ADB."""

        parts = cmd_str.strip().split()

        if not parts:

            return {"ok": False, "output": "Пустая команда"}

        res = self.run_adb(parts, timeout=15)

        out = (res["stdout"] + "\n" + res["stderr"]).strip()

        return {"ok": res["ok"], "output": out or "Команда выполнена (без вывода)"}


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
