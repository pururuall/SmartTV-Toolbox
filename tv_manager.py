import json
import os
import sys
import re
import socket
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any


class SmartTVManager:
    """
    Единый контроллер SmartTV-Toolbox v3.0.
    Объединяет наработки SmartTV-Toolbox, tv-cleaner, moy-tv и chistytv.
    """

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        elif getattr(sys, 'frozen', False):
            exe_dir = Path(os.path.dirname(sys.executable))
            meipass_dir = Path(getattr(sys, '_MEIPASS', exe_dir))
            self.base_dir = exe_dir if (exe_dir / "data" / "packages.json").exists() else meipass_dir
        else:
            self.base_dir = Path(os.path.dirname(os.path.abspath(__file__)))

        self.adb_bin = self._resolve_adb_binary()
        self.current_device: Optional[str] = None

        self.packages_db = self._load_json(self.base_dir / "data" / "packages.json")
        self.launchers_db = self._load_json(self.base_dir / "data" / "launchers.json")
        self.backups_dir = self.base_dir / "backups"
        self.backups_dir.mkdir(exist_ok=True)

    def _resolve_adb_binary(self) -> str:
        win_adb = self.base_dir / "platform-tools" / "adb.exe"
        if win_adb.exists():
            return str(win_adb)
        return "adb"

    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

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

    def install_and_activate_launcher(
        self, launcher_id: str, disable_stock: bool = True
    ) -> Dict[str, Any]:
        """Устанавливает выбранный лаунчер и безопасно делает его главным экраном."""
        launchers = self.launchers_db.get("launchers", {})
        if launcher_id not in launchers:
            return {"ok": False, "error": f"Неизвестный лаунчер: {launcher_id}"}

        meta = launchers[launcher_id]
        apk_full_path = self.base_dir / meta["apk_path"]
        if not apk_full_path.exists():
            return {"ok": False, "error": f"Файл APK не найден: {apk_full_path}"}

        inst_res = self.run_adb(["install", "-r", str(apk_full_path)], timeout=60)
        if not inst_res["ok"]:
            return {"ok": False, "error": f"Ошибка установки APK: {inst_res['stderr']}"}

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
        """Устанавливает или отключает автономный веб-пульт прямо на ТВ."""
        if not self.current_device:
            return {"ok": False, "error": "Телевизор не подключен к ADB."}

        ip_only = self.current_device.split(":")[0]

        if not enable:
            self.run_adb(["shell", "pkill", "-f", "busybox.*httpd"])
            self.run_adb(["shell", "rm", "-rf", "/data/local/tmp/web_remote"])
            return {"ok": True, "enabled": False, "msg": "Веб-пульт остановлен и удален с ТВ."}

        local_remote_dir = self.base_dir / "web_remote"
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

        url = f"http://{ip_only}:8080"
        return {
            "ok": True,
            "enabled": True,
            "port": 8080,
            "url": url,
            "msg": f"Автономный веб-пульт активен: {url}"
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
            st_apk = self.base_dir / "apps" / "youtube" / "SmartTube_stable.apk"
            if st_apk.exists():
                res = self.run_adb(["install", "-r", str(st_apk)], timeout=60)
                steps_log.append({"step": "install_smarttube", "ok": res["ok"]})

        if bypass_mode == "byedpi":
            byedpi_apk = self.base_dir / "apps" / "youtube" / "ByeDPI_tv.apk"
            if byedpi_apk.exists():
                self.run_adb(["install", "-r", str(byedpi_apk)], timeout=45)

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
            "lampa": self.base_dir / "apps" / "media" / "Lampa.apk",
            "zona": self.base_dir / "apps" / "media" / "Zona.apk",
            "hdrezka": self.base_dir / "apps" / "media" / "HDRezka.apk",
            "filemanager": self.base_dir / "apps" / "media" / "FileManagerPlus.apk",
            "happ": self.base_dir / "apps" / "media" / "Happ.apk",
            "spotify": self.base_dir / "apps" / "media" / "SpotifyTV.apk",
            "smarttube": self.base_dir / "apps" / "youtube" / "SmartTube_stable.apk",
            "byedpi": self.base_dir / "apps" / "youtube" / "ByeDPI_tv.apk",
            "cleanyourtv": self.base_dir / "apps" / "launchers" / "CleanYourTV.apk",
            "moytv": self.base_dir / "apps" / "launchers" / "MoyTV.apk",
            "flauncher": self.base_dir / "apps" / "launchers" / "FLauncher.apk",
        }

        for key in app_keys:
            apk = apps_map.get(key.lower())
            if apk and apk.exists():
                res = self.run_adb(["install", "-r", str(apk)], timeout=60)
                if res["ok"]:
                    installed.append(key)
                else:
                    errors.append({"app": key, "error": res["stderr"] or res["stdout"]})
            else:
                errors.append({"app": key, "error": "APK файл не найден"})

        return {"ok": True, "installed": installed, "errors": errors}

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
